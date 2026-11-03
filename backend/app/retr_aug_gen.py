
from sqlalchemy.orm import Session
from app.db_tables import KnowledgeChunk
from sentence_transformers import SentenceTransformer

# This model produces 384-dimensional embeddings.
# Keep this model consistent with the embeddings already stored in Supabase.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embedding(text: str) -> list[float]:
    embedding = embedding_model.encode(
        text,
        normalize_embeddings=True
    )
    return embedding.tolist()


def retrieve_context(
    db: Session,
    question: str,
    top_k: int = 3
) -> str:
    query_embedding = create_embedding(question)

    results = (
        db.query(KnowledgeChunk)
        .order_by(
            KnowledgeChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(10)
        .all()
    )

    seen_docs = set()
    unique_results = []

    for chunk in results:
        if chunk.source_document not in seen_docs:
            seen_docs.add(chunk.source_document)
            unique_results.append(chunk)

        if len(unique_results) >= top_k:
            break

    if not unique_results:
        return ""

    context = "\n\n".join(
        chunk.content for chunk in unique_results
    )

    return context
