import os
from openai import OpenAI
from sqlalchemy.orm import Session
from app.db_tables import KnowledgeChunk

client = OpenAI(
    api_key=os.getenv("")
)


def create_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def retrieve_context(
    db: Session,
    question: str,
    top_k: int = 3
):
    query_embedding = create_embedding(question)

    results = (
        db.query(KnowledgeChunk)
        .order_by(
            KnowledgeChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(top_k)
        .all()
    )

    context = "\n\n".join(
        chunk.content for chunk in results
    )

    return context


def answer_question(
    db: Session,
    question: str
):
    context = retrieve_context(
        db=db,
        question=question
    )

    response = client.chat.completions.create(
        model="",
        messages=[
            {
                "role": "system",
                "content": """
You are a mental health support assistant.

Answer using only the provided knowledge base.
If the knowledge base does not contain the answer,
say so clearly.
"""
            },
            {
                "role": "user",
                "content": f"""
Knowledge Base:

{context}

Question:

{question}
"""
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content