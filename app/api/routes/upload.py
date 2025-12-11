import json
from io import BytesIO
from typing import Any, Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app.models.schemas import DocumentInput
from app.services import rag

router = APIRouter(tags=["indexing"])


@router.post("/upload", response_model=dict[str, int])
async def upload_document(
    file: UploadFile = File(...),
    id: str = Form(..., description="Document id or external reference"),
    metadata: str | None = Form(
        default=None,
        description="Optional JSON string of metadata to store with the doc",
    ),
):
    """Upload a single file (text or PDF), chunk, embed, and store in Chroma."""
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    meta: Dict[str, Any] = {}
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400, detail="metadata must be valid JSON"
            ) from exc

    is_pdf = "pdf" in (file.content_type or "").lower() or file.filename.lower().endswith(
        ".pdf"
    )
    if is_pdf:
        reader = PdfReader(BytesIO(raw_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        content = "\n\n".join(pages_text)
    else:
        content = raw_bytes.decode("utf-8", errors="ignore")

    doc = DocumentInput(id=id, text=content, metadata=meta)
    count = rag.index_documents([doc])
    return {"indexed": count}
