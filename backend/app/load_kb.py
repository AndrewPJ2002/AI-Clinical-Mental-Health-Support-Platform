
from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal
from app.db_tables import KnowledgeChunk
from app.retr_aug_gen import create_embedding


# Resolve the knowledge-base directory relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = PROJECT_ROOT / "knowledge-base"

# Documentation is not intended to become chatbot knowledge.
EXCLUDED_FILES = {"about_knowledge_base.md"}



def chunk_text(
    text: str,
    size: int = 500,
    overlap: int = 75,
) -> list[str]:
    """Split Markdown text into overlapping paragraph-based chunks."""

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # Keep unusually long paragraphs from exceeding the target size.
        if len(paragraph) > size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            start = 0

            while start < len(paragraph):
                end = min(start + size, len(paragraph))
                chunks.append(paragraph[start:end].strip())

                if end == len(paragraph):
                    break

                start = end - overlap

            continue

        candidate = (
            f"{current_chunk}\n\n{paragraph}"
            if current_chunk
            else paragraph
        )

        if len(candidate) <= size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks



def load_knowledge_base() -> None:
    """Insert missing knowledge chunks without deleting existing records."""

    if not KB_DIR.is_dir():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {KB_DIR}"
        )

    db = SessionLocal()

    try:
        files = sorted(
            file for file in KB_DIR.glob("*.md")
            if file.name not in EXCLUDED_FILES
        )

        if not files:
            print("No knowledge-base Markdown files found.")
            return

        inserted = 0
        skipped = 0
        seen_chunks = set()

        for file in files:
            text = file.read_text(encoding="utf-8")
            chunks = chunk_text(text)

            for chunk in chunks:
                chunk_key = (file.name, chunk)

                if chunk_key in seen_chunks:
                    skipped += 1
                    continue

                seen_chunks.add(chunk_key)

                existing = db.execute(
                    select(KnowledgeChunk.id).where(
                        KnowledgeChunk.source_document == file.name,
                        KnowledgeChunk.content == chunk,
                    ).limit(1)
                ).first()

                if existing:
                    skipped += 1
                    continue

                db.add(
                    KnowledgeChunk(
                        source_document=file.name,
                        content=chunk,
                        embedding=create_embedding(chunk),
                    )
                )
                inserted += 1

        db.commit()

        print(f"New chunks inserted: {inserted}")
        print(f"Existing chunks skipped: {skipped}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def rebuild_knowledge_base() -> None:
    """Safely replace existing knowledge chunks with freshly generated chunks."""

    if not KB_DIR.is_dir():
        raise FileNotFoundError(
            f"Knowledge-base directory not found: {KB_DIR}"
        )

    files = sorted(
        file for file in KB_DIR.glob("*.md")
        if file.name not in EXCLUDED_FILES
    )

    if not files:
        raise ValueError("No knowledge-base Markdown files found.")

    # Prepare every chunk and embedding BEFORE changing the database.
    prepared_records = []

    for file in files:
        text = file.read_text(encoding="utf-8")

        for chunk in chunk_text(text):
            embedding = create_embedding(chunk)

            if len(embedding) != 384:
                raise ValueError(
                    f"Invalid embedding dimension in {file.name}: "
                    f"{len(embedding)}"
                )

            prepared_records.append({
                "source_document": file.name,
                "content": chunk,
                "embedding": embedding,
            })

    expected_documents = {file.name for file in files}

    if len(prepared_records) != 17:
        raise ValueError(
            f"Expected 17 chunks, found {len(prepared_records)}. "
            "Database was not changed."
        )

    print(f"Prepared {len(prepared_records)} chunks.")
    print("All embeddings passed validation.")

    db = SessionLocal()

    try:
        # Display the current records that will be replaced.
        existing_counts = db.execute(
            select(
                KnowledgeChunk.source_document,
            ).where(
                KnowledgeChunk.source_document.in_(expected_documents)
            )
        ).all()

        print(
            f"Existing records to replace: {len(existing_counts)}"
        )

        # Replace only the five known knowledge-base documents.
        db.query(KnowledgeChunk).filter(
            KnowledgeChunk.source_document.in_(expected_documents)
        ).delete(synchronize_session=False)

        for record in prepared_records:
            db.add(KnowledgeChunk(**record))

        db.commit()

        print("Knowledge base rebuilt successfully.")
        print(f"New chunks inserted: {len(prepared_records)}")

    except Exception:
        db.rollback()
        print("Rebuild failed. Database changes were rolled back.")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_knowledge_base()
