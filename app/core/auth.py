from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from ..models.schemas import UserInfo
from fastapi.requests import Request

# Make tokenUrl optional by setting auto_error=False
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserInfo:
    """
    Temporary implementation - returns mock user
    """
    return UserInfo(
        email="test@example.com",
        role="admin"
    )

async def get_optional_user(request: Request) -> Optional[UserInfo]:
    """
    Get user if token exists, otherwise return None
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
        
    return UserInfo(
        email="test@example.com",
        role="admin"
    )

def verify_token(token: str) -> Optional[UserInfo]:
    """
    Verify the authentication token
    """
    try:
        # Implement proper token verification here
        return UserInfo(
            email="test@example.com",
            role="admin"
        )
    except Exception:
        return None 