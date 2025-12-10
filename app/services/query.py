"""Query service for handling user queries."""

import time
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.rag.chain import RAGChain
from app.rag.agent import RAGAgent
from app.models.logs import QueryLog
from app.schemas.query import Source
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class QueryService:
    """Service for processing user queries."""

    def __init__(self):
        """Initialize the query service."""
        rag_mode = settings.rag_mode.lower()
        if rag_mode == "agent":
            self.rag_engine = RAGAgent()
            logger.info("QueryService initialized with agentic RAG mode")
        else:
            self.rag_engine = RAGChain()
            logger.info("QueryService initialized with chain RAG mode")

    def process_query(
        self,
        query: str,
        db: Session,
        user_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """Process a user query and return answer with sources.
        
        Args:
            query: User query string
            db: Database session for logging
            user_ip: Optional user IP address
            user_agent: Optional user agent string
            
        Returns:
            Dictionary with 'answer' and 'sources'
        """
        start_time = time.time()
        
        try:
            logger.info("Processing query", query=query[:50])
            
            # Query the configured RAG engine (agentic or chain)
            result = self.rag_engine.query_with_sources(query)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Format sources
            sources = []
            for source_doc in result.get("sources", []):
                source = Source(
                    url=source_doc.get("metadata", {}).get("source"),
                    title=source_doc.get("metadata", {}).get("title"),
                    chunk_id=source_doc.get("metadata", {}).get("chunk_id"),
                )
                sources.append(source)
            
            # Log the query
            query_log = QueryLog(
                query=query,
                answer=result["answer"],
                sources=json.dumps([s.dict() for s in sources]),
                response_time_ms=response_time_ms,
                user_ip=user_ip,
                user_agent=user_agent,
            )
            db.add(query_log)
            db.commit()
            
            logger.info(
                "Query processed successfully",
                query=query[:50],
                response_time_ms=response_time_ms,
            )
            
            return {
                "answer": result["answer"],
                "sources": sources,
                "response_time_ms": response_time_ms,
            }
            
        except Exception as e:
            logger.error("Query processing failed", query=query[:50], error=str(e))
            
            # Log failed query
            query_log = QueryLog(
                query=query,
                answer=None,
                sources=None,
                response_time_ms=int((time.time() - start_time) * 1000),
                user_ip=user_ip,
                user_agent=user_agent,
            )
            db.add(query_log)
            db.commit()
            
            raise

