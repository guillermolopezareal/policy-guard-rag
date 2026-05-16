from pydantic import BaseModel, Field
from typing import Optional


class IngestResponse(BaseModel):
    status: str
    filename: str
    chunks_stored: int


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)


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
