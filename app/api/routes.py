from fastapi import APIRouter, Depends

from app.core.config import get_settings, Settings
from app.services import rag
from app.models.schemas import (
    GenerationRequest,
    GenerationResponse,
    IndexRequest,
    QueryRequest,
    QueryResponse,
)

router = APIRouter()


def get_app_settings() -> Settings:
    return get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/index", response_model=dict[str, int])
def index_documents(payload: IndexRequest, settings: Settings = Depends(get_app_settings)):
    count = rag.index_documents(payload.documents)
    return {"indexed": count}


@router.post("/retrieve", response_model=QueryResponse)
def retrieve(payload: QueryRequest):
    return rag.retrieve(payload)


@router.post("/generate", response_model=GenerationResponse)
def generate(payload: GenerationRequest):
    return rag.generate(payload)
