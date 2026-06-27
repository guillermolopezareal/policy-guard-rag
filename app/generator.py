from openai import OpenAI
from .models import QueryResponse, SourceChunk, TraceChunk, TraceResponse
from .retriever import CONFIDENCE_THRESHOLD

_EMBEDDING_MODEL = "text-embedding-3-small"
_EMBEDDING_DIMS = 1536
_GENERATION_MODEL = "gpt-4o-mini"
_GENERATION_TEMP = 0.1

client = OpenAI()

SYSTEM_PROMPT = (
    "You are a security and compliance policy assistant. "
    "Answer the user's question using ONLY the context provided below. "
    "Do not use any external knowledge. "
    "If the context does not contain enough information to answer confidently, say so explicitly. "
    "Always reference which document your answer comes from."
)


def generate_answer(question: str, chunks: list[dict], confidence_threshold: float = CONFIDENCE_THRESHOLD) -> QueryResponse:
    if not chunks:
        return QueryResponse(
            answered=False,
            reason="Insufficient evidence in knowledge base. Confidence: 0.00. Please consult a security expert.",
            confidence=0.0,
            sources=[],
        )

    best_score = chunks[0]["score"]

    if best_score < confidence_threshold:
        return QueryResponse(
            answered=False,
            reason=f"Insufficient evidence in knowledge base. Confidence: {best_score:.2f}. Please consult a security expert.",
            confidence=best_score,
            sources=[],
        )


    context_chunks = [c for c in chunks if c["score"] >= confidence_threshold]
    context_blocks = []
    for i, chunk in enumerate(context_chunks, 1):
        context_blocks.append(
            f"[Source {i}: {chunk['document']}]\n{chunk['excerpt']}"
        )
    context = "\n\n".join(context_blocks)

    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=_GENERATION_MODEL,
        temperature=_GENERATION_TEMP,
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
        for chunk in context_chunks
    ]

    return QueryResponse(
        answered=True,
        answer=answer,
        confidence=best_score,
        sources=sources,
    )


def generate_answer_with_trace(
    question: str,
    chunks: list[dict],
    total_chunks: int,
    top_k: int = 5,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> TraceResponse:
    best_score = chunks[0]["cosine_similarity"] if chunks else 0.0
    gate_passed = bool(chunks) and best_score >= confidence_threshold

    trace_chunks = [
        TraceChunk(
            rank=c["rank"],
            document=c["document"],
            excerpt=c["excerpt"],
            chunk_index=c["chunk_index"],
            l2_distance=c["l2_distance"],
            cosine_similarity=c["cosine_similarity"],
            used_in_context=gate_passed and c["cosine_similarity"] >= confidence_threshold,
        )
        for c in chunks
    ]

    if not gate_passed:
        return TraceResponse(
            question=question,
            embedding_model=_EMBEDDING_MODEL,
            embedding_dimensions=_EMBEDDING_DIMS,
            total_chunks_in_collection=total_chunks,
            top_k=top_k,
            retrieval_results=trace_chunks,
            confidence_threshold=confidence_threshold,
            best_score=best_score,
            gate_passed=False,
            answered=False,
            reason=f"Insufficient evidence in knowledge base. Confidence: {best_score:.2f}. Please consult a security expert.",
        )

    context_chunks = [c for c in chunks if c["cosine_similarity"] >= confidence_threshold]
    context_blocks = []
    for i, chunk in enumerate(context_chunks, 1):
        context_blocks.append(
            f"[Source {i}: {chunk['document']}]\n{chunk['excerpt']}"
        )
    context = "\n\n".join(context_blocks)

    response = client.chat.completions.create(
        model=_GENERATION_MODEL,
        temperature=_GENERATION_TEMP,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    return TraceResponse(
        question=question,
        embedding_model=_EMBEDDING_MODEL,
        embedding_dimensions=_EMBEDDING_DIMS,
        total_chunks_in_collection=total_chunks,
        top_k=top_k,
        retrieval_results=trace_chunks,
        confidence_threshold=confidence_threshold,
        best_score=best_score,
        gate_passed=True,
        generation_model=_GENERATION_MODEL,
        generation_temperature=_GENERATION_TEMP,
        context_sent_to_llm=context,
        answered=True,
        answer=response.choices[0].message.content,
    )
