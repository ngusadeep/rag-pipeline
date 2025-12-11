from fastapi import APIRouter

from app.models.schemas import QueryRequest, QueryResponse
from app.services import rag

router = APIRouter(tags=["retrieval"])


@router.post("/retrieve", response_model=QueryResponse)
def retrieve(payload: QueryRequest):
    return rag.retrieve(payload)
