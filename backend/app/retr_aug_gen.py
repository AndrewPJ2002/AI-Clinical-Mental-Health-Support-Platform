import os
from openai import OpenAI
from sqlalchemy.orm import Session
from app.db_tables import KnowledgeChunk
from app.config import settings
from sentence_transformers import SentenceTransformer

client = OpenAI(
    api_key=settings.open_api_key
)
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def create_embedding(text: str):
    #response = client.embeddings.create(
        #model="text-embedding-3-small",
        #input=text
    #)
    #return response.data[0].embedding
    embedding = embedding_model.encode(
        text,
        normalize_embeddings=True
    )
    return embedding.tolist()


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
    print("\nRETRIEVED DOCUMENTS:")
    for result in unique_results:
        print(result.source_document)
    context = "\n\n".join(
            chunk.content for chunk in unique_results
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
        model=settings.openai_model,
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