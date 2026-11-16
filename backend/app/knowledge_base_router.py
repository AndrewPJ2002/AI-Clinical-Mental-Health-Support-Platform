from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.admin.router import require_admin
from app.database import get_db
from app.db_tables import KnowledgeChunk, User
from app.load_kb import EXCLUDED_FILES, KB_DIR, chunk_text
from app.retr_aug_gen import create_embedding


router = APIRouter(
    prefix="/knowledge-base",
    tags=["Knowledge Base"],
)


class KnowledgeDocumentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=100_000)


class RetrievalTestRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)


def _get_document_path(filename: str) -> Path:
    if (
        not filename.endswith(".md")
        or filename in EXCLUDED_FILES
        or Path(filename).name != filename
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge-base document not found.",
        )

    document_path = (KB_DIR / filename).resolve()

    if document_path.parent != KB_DIR.resolve() or not document_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge-base document not found.",
        )

    return document_path


@router.get("/document/{filename}")
def get_knowledge_document(
    filename: str,
    current_user: User = Depends(require_admin),
):
    document_path = _get_document_path(filename)

    try:
        content = document_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge-base document could not be read.",
        ) from exc

    return {
        "filename": filename,
        "content": content,
    }


@router.put("/document/{filename}")
def update_knowledge_document(
    filename: str,
    payload: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    document_path = _get_document_path(filename)
    if not payload.content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Knowledge-base document content cannot be empty.",
        )

    chunks = chunk_text(payload.content)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Knowledge-base document must contain indexable text.",
        )

    prepared_chunks = []
    for chunk in chunks:
        embedding = create_embedding(chunk)
        if len(embedding) != 384:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Knowledge-base embedding has an invalid dimension.",
            )
        prepared_chunks.append(
            {
                "source_document": filename,
                "content": chunk,
                "embedding": embedding,
            }
        )

    try:
        previous_content = document_path.read_bytes()
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge-base document could not be read before updating.",
        ) from exc

    try:
        document_path.write_text(payload.content, encoding="utf-8")
    except OSError as exc:
        try:
            document_path.write_bytes(previous_content)
        except OSError as restore_exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document save failed and the original could not be restored.",
            ) from restore_exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge-base document could not be saved.",
        ) from exc

    try:
        (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.source_document == filename)
            .delete(synchronize_session=False)
        )
        db.add_all(
            KnowledgeChunk(**chunk_record)
            for chunk_record in prepared_chunks
        )
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        try:
            document_path.write_bytes(previous_content)
        except OSError as restore_exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Knowledge-base indexing failed and the original "
                    "document could not be restored."
                ),
            ) from restore_exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Knowledge-base index could not be updated; "
                "the document change was rolled back."
            ),
        ) from exc

    return {
        "filename": filename,
        "updated": True,
        "chunk_count": len(prepared_chunks),
    }


@router.post("/test")
def test_knowledge_retrieval(
    payload: RetrievalTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Retrieval query cannot be empty.",
        )

    try:
        query_embedding = create_embedding(query)
        chunks = (
            db.query(KnowledgeChunk)
            .order_by(
                KnowledgeChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(10)
            .all()
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge-base retrieval test failed.",
        ) from exc

    documents = []
    context_sections = []
    seen_documents = set()

    for chunk in chunks:
        source_document = chunk.source_document
        if not source_document or source_document in seen_documents:
            continue

        seen_documents.add(source_document)
        documents.append(source_document)
        context_sections.append(chunk.content)

        if len(documents) == 3:
            break

    return {
        "documents": documents,
        "context": "\n\n".join(context_sections),
    }