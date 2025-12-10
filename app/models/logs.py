"""Log models for audit and analytics."""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QueryLog(Base):
    """Query log for auditing and analytics."""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    sources = Column(Text, nullable=True)  # JSON string of sources
    response_time_ms = Column(Integer, nullable=True)
    user_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IndexingLog(Base):
    """Log for document indexing operations."""

    __tablename__ = "indexing_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(50), nullable=False)  # 'full_reindex', 'incremental', etc.
    documents_processed = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'in_progress'
    error_message = Column(Text, nullable=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    admin_user = relationship("AdminUser", backref="indexing_logs")

