from fastapi import APIRouter

from app.models.schemas import GenerationRequest, GenerationResponse
from app.services import rag

router = APIRouter(tags=["generation"])


@router.post("/generate", response_model=GenerationResponse)
def generate(payload: GenerationRequest):
    return rag.generate(payload)
