"""Pydantic schemas for API requests and responses."""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    collection: str


class ChatRequest(BaseModel):
    question: str = Field(..., examples=["What is BiasharaPlus?"])
    top_k: int = Field(default=4, ge=1, le=10)


class SourceChunk(BaseModel):
    content: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
