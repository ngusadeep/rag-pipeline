from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.models.schemas import IndexRequest
from app.services import rag

router = APIRouter(tags=["indexing"])


def get_app_settings() -> Settings:
    return get_settings()


@router.post("/index", response_model=dict[str, int])
def index_documents(
    payload: IndexRequest, settings: Settings = Depends(get_app_settings)
):
    count = rag.index_documents(payload.documents)
    return {"indexed": count}
