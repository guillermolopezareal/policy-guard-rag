from pydantic import BaseModel, Field
from typing import Optional


class IngestResponse(BaseModel):
    status: str
    filename: str
    chunks_stored: int


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)
    top_k: int = Field(default=5, ge=1, le=20)
    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0)


class SourceChunk(BaseModel):
    document: str
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answered: bool
    answer: Optional[str] = None
    reason: Optional[str] = None
    confidence: float
    sources: list[SourceChunk]


class TraceChunk(BaseModel):
    rank: int
    document: str
    excerpt: str
    chunk_index: int
    l2_distance: float
    cosine_similarity: float
    used_in_context: bool = True


class TraceResponse(BaseModel):
    question: str
    embedding_model: str
    embedding_dimensions: int
    total_chunks_in_collection: int
    top_k: int
    retrieval_results: list[TraceChunk]
    confidence_threshold: float
    best_score: float
    gate_passed: bool
    generation_model: Optional[str] = None
    generation_temperature: Optional[float] = None
    context_sent_to_llm: Optional[str] = None
    answered: bool
    answer: Optional[str] = None
    reason: Optional[str] = None
