from pathlib import Path
from app.database import SessionLocal, Base, engine
from app.db_tables import KnowledgeChunk
from app.retr_aug_gen import create_embedding

db = SessionLocal()
db.query(KnowledgeChunk).delete()
db.commit()

def chunk_text(text, size=500):
    return [
        text[i:i+size]
        for i in range(0, len(text), size)
    ]

KB_DIR = Path("C:/Users/14047/ai 7993/AI-Clinical-Mental-Health-Support-Platform/knowledge-base")
Base.metadata.create_all(bind=engine)


for file in KB_DIR.glob("*.md"):

    text = file.read_text(
        encoding="utf-8"
    )

    chunks = chunk_text(text)

    for chunk in chunks:

        db.add(
            KnowledgeChunk(
                source_document=file.name,
                content=chunk,
                embedding=create_embedding(
                    chunk
                ),
            )
        )

db.commit()
