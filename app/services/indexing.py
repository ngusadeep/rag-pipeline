"""Indexing service for document ingestion and vector store management."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.rag.loaders import DocumentLoader
from app.rag.chunking import TextChunker
from app.rag.embeddings import EmbeddingService
from app.models.logs import IndexingLog
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class IndexingService:
    """Service for indexing documents into the vector store."""

    def __init__(self):
        """Initialize the indexing service."""
        self.loader = DocumentLoader()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()

    def index_from_urls(
        self,
        urls: List[str],
        db: Session,
        admin_user_id: Optional[int] = None,
        force: bool = False,
    ) -> IndexingLog:
        """Index documents from URLs.
        
        Args:
            urls: List of URLs to index
            db: Database session
            admin_user_id: Optional admin user ID
            force: Force reindex even if index exists
            
        Returns:
            IndexingLog entry
        """
        log = IndexingLog(
            operation_type="url_indexing",
            status="in_progress",
            admin_user_id=admin_user_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        try:
            logger.info("Starting URL indexing", urls=urls, log_id=log.id)
            
            # Load documents
            documents = self.loader.load_from_urls(urls)
            logger.info("Documents loaded", count=len(documents))
            
            # Chunk documents
            chunks = self.chunker.chunk_documents(documents)
            logger.info("Documents chunked", chunk_count=len(chunks))
            
            # Delete existing vectors if force
            if force:
                self.embedding_service.delete_all()
            
            # Add to vector store
            self.embedding_service.add_documents(chunks)
            
            log.status = "success"
            log.documents_processed = len(documents)
            log.chunks_created = len(chunks)
            log.completed_at = func.now()
            
            db.commit()
            logger.info("URL indexing completed", log_id=log.id, chunks=len(chunks))
            
        except Exception as e:
            logger.error("URL indexing failed", log_id=log.id, error=str(e))
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = func.now()
            db.commit()
            raise
        
        return log

    def index_from_directory(
        self,
        directory_path: str,
        db: Session,
        admin_user_id: Optional[int] = None,
        force: bool = False,
    ) -> IndexingLog:
        """Index documents from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            db: Database session
            admin_user_id: Optional admin user ID
            force: Force reindex even if index exists
            
        Returns:
            IndexingLog entry
        """
        log = IndexingLog(
            operation_type="directory_indexing",
            status="in_progress",
            admin_user_id=admin_user_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        try:
            logger.info("Starting directory indexing", directory=directory_path, log_id=log.id)
            
            # Load documents
            documents = self.loader.load_from_directory(directory_path)
            logger.info("Documents loaded", count=len(documents))
            
            # Chunk documents
            chunks = self.chunker.chunk_documents(documents)
            logger.info("Documents chunked", chunk_count=len(chunks))
            
            # Delete existing vectors if force
            if force:
                self.embedding_service.delete_all()
            
            # Add to vector store
            self.embedding_service.add_documents(chunks)
            
            log.status = "success"
            log.documents_processed = len(documents)
            log.chunks_created = len(chunks)
            log.completed_at = func.now()
            
            db.commit()
            logger.info("Directory indexing completed", log_id=log.id, chunks=len(chunks))
            
        except Exception as e:
            logger.error("Directory indexing failed", log_id=log.id, error=str(e))
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = func.now()
            db.commit()
            raise
        
        return log

