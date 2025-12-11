from fastapi import APIRouter, HTTPException

from app.models.schemas import IndexFromUrlRequest
from app.services import rag

router = APIRouter(tags=["indexing"])


@router.post("/index_from_url", response_model=dict[str, int])
def index_from_url(payload: IndexFromUrlRequest):
    try:
        count = rag.index_from_url(payload)
        return {"indexed": count}
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=400, detail=str(exc)) from exc
