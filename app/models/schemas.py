"""Pydantic schemas for API requests and responses."""

from typing import List

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    collection: str


class ChatRequest(BaseModel):
    question: str = Field(..., examples=["What is this document about?"])
    top_k: int = Field(default=4, ge=1, le=10)


class SourceChunk(BaseModel):
    content: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
