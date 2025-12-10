"""Admin routes for authentication and indexing."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse
from app.schemas.reindex import ReindexRequest, ReindexResponse
from app.services.auth import AuthService
from app.services.indexing import IndexingService
from app.models.admin import AdminUser
from app.core.database import get_db
from app.core.deps import get_settings
from app.core.config import Settings
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["admin"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    """Get the current authenticated admin user."""
    payload = AuthService.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = AuthService.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


@router.post("/login", response_model=AdminLoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Admin login endpoint.
    
    Args:
        form_data: OAuth2 password form with username and password
        db: Database session
        
    Returns:
        AdminLoginResponse with access token
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return AdminLoginResponse(access_token=access_token, token_type="bearer")


@router.post("/reindex", response_model=ReindexResponse)
async def reindex(
    reindex_request: ReindexRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Trigger document reindexing.
    
    Args:
        reindex_request: Reindex request with source type and force flag
        current_user: Current authenticated admin user
        db: Database session
        settings: Application settings
        
    Returns:
        ReindexResponse with operation status
    """
    indexing_service = IndexingService()
    
    try:
        # For now, we'll support URL-based indexing
        # In production, you'd configure URLs in settings or database
        if reindex_request.source_type == "website":
            # Example: Index from BiasharaPlus website
            # You should configure these URLs in settings
            urls = [
                "https://biasharaplus.com",
                # Add more URLs as needed
            ]
            
            log = indexing_service.index_from_urls(
                urls=urls,
                db=db,
                admin_user_id=current_user.id,
                force=reindex_request.force,
            )
            
            return ReindexResponse(
                status="success",
                message="Documents indexed successfully",
                documents_processed=log.documents_processed,
                chunks_created=log.chunks_created,
                indexing_log_id=log.id,
            )
        else:
            return ReindexResponse(
                status="error",
                message=f"Source type '{reindex_request.source_type}' not yet implemented",
            )
            
    except Exception as e:
        logger.error("Reindexing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}",
        )

