from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class DocumentInput(BaseModel):
    id: str = Field(..., description="Document id or external reference")
    text: str = Field(..., description="Raw document text to index")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata to store with the doc"
    )


class QueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    k: int = Field(default=4, description="Number of documents to retrieve")


class RetrievalResult(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    results: List[RetrievalResult]


class GenerationRequest(QueryRequest):
    pass


class GenerationResponse(BaseModel):
    answer: str
    citations: List[RetrievalResult]
