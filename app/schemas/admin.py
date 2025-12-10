"""Admin-related schemas."""

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    """Admin login request."""

    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response."""

    access_token: str
    token_type: str = "bearer"

