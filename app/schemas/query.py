"""Query-related schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Request schema for /ask endpoint."""

    query: str = Field(..., description="User query about BiasharaPlus services")


class Source(BaseModel):
    """Source document reference."""

    url: Optional[str] = None
    title: Optional[str] = None
    chunk_id: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response schema for /ask endpoint."""

    answer: str = Field(..., description="AI-generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents")
    response_time_ms: Optional[int] = None

