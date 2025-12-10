"""Authentication service for admin users."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.admin import AdminUser
from app.core.config import settings
import structlog

logger = structlog.get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication and authorization."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[AdminUser]:
        """Authenticate a user by username and password."""
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[AdminUser]:
        """Get a user by username."""
        return db.query(AdminUser).filter(AdminUser.username == username).first()

    @staticmethod
    def create_default_admin(db: Session) -> AdminUser:
        """Create the default admin user if it doesn't exist."""
        admin = AuthService.get_user_by_username(db, settings.admin_username)
        if admin:
            logger.info("Default admin user already exists")
            return admin
        
        logger.info("Creating default admin user")
        admin = AdminUser(
            username=settings.admin_username,
            hashed_password=AuthService.get_password_hash(settings.admin_password),
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Default admin user created", username=settings.admin_username)
        return admin

