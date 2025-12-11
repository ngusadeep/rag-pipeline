from fastapi import APIRouter

from app.models.schemas import GenerationRequest, GenerationResponse
from app.services import rag

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=GenerationResponse)
def chat(payload: GenerationRequest):
    """Chat-style RAG endpoint (retriever → prompt → LLM)."""
    return rag.generate(payload)
