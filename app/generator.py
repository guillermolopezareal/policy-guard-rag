from openai import OpenAI
from .models import QueryResponse, SourceChunk
from .retriever import CONFIDENCE_THRESHOLD

client = OpenAI()

SYSTEM_PROMPT = (
    "You are a security and compliance policy assistant. "
    "Answer the user's question using ONLY the context provided below. "
    "Do not use any external knowledge. "
    "If the context does not contain enough information to answer confidently, say so explicitly. "
    "Always reference which document your answer comes from."
)


def generate_answer(question: str, chunks: list[dict]) -> QueryResponse:
    if not chunks:
        return QueryResponse(
            answered=False,
            reason="Insufficient evidence in knowledge base. Confidence: 0.00. Please consult a security expert.",
            confidence=0.0,
            sources=[],
        )

    best_score = chunks[0]["score"]

    if best_score < CONFIDENCE_THRESHOLD:
        return QueryResponse(
            answered=False,
            reason=f"Insufficient evidence in knowledge base. Confidence: {best_score:.2f}. Please consult a security expert.",
            confidence=best_score,
            sources=[],
        )

    context_blocks = []
    for i, chunk in enumerate(chunks, 1):
        context_blocks.append(
            f"[Source {i}: {chunk['document']}]\n{chunk['excerpt']}"
        )
    context = "\n\n".join(context_blocks)

    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    answer = response.choices[0].message.content

    sources = [
        SourceChunk(
            document=chunk["document"],
            excerpt=chunk["excerpt"],
            score=chunk["score"],
        )
        for chunk in chunks
    ]

    return QueryResponse(
        answered=True,
        answer=answer,
        confidence=best_score,
        sources=sources,
    )
