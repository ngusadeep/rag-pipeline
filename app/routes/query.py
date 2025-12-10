"""Query routes for customer queries."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query import QueryService
from app.core.database import get_db
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/ask", tags=["query"])


@router.post("", response_model=QueryResponse)
async def ask_question(
    request_body: QueryRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle customer queries about BiasharaPlus services.
    
    Args:
        request_body: Query request with user question
        request: FastAPI request object
        db: Database session
        
    Returns:
        QueryResponse with answer and sources
    """
    query_service = QueryService()
    
    # Get user IP and user agent
    user_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = query_service.process_query(
        query=request_body.query,
        db=db,
        user_ip=user_ip,
        user_agent=user_agent,
    )
    
    return QueryResponse(**result)

