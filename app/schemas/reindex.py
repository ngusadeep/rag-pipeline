"""Reindexing-related schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class ReindexRequest(BaseModel):
    """Request to trigger reindexing."""

    source_type: Optional[str] = Field(
        default="all", description="Type of source to reindex: 'all', 'website', 'pdfs'"
    )
    force: bool = Field(default=False, description="Force full reindex even if index exists")


class ReindexResponse(BaseModel):
    """Response for reindexing operation."""

    status: str
    message: str
    documents_processed: int = 0
    chunks_created: int = 0
    indexing_log_id: Optional[int] = None

