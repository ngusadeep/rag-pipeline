"""Document ingestion endpoint."""

import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.models.schemas import UploadResponse
from app.services.rag import ingest_file

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "text/plain", "application/octet-stream"}


@router.post(
    "/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type {file.content_type}",
        )

    settings = get_settings()
    settings.documents_path.mkdir(parents=True, exist_ok=True)
    destination = settings.documents_path / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunk_count = ingest_file(destination)
    return UploadResponse(
        filename=file.filename,
        chunks=chunk_count,
        collection=settings.zvec_collection_name,
    )
