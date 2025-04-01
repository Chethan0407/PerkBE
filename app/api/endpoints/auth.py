from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from ...core.config import settings
from ...models.schemas import UserInfo

router = APIRouter()

@router.get("/login")
async def authenticate_user(token: str) -> UserInfo:
    try:
        user_info = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        if not user_info["email"].endswith("@curefit.com"):
            raise HTTPException(
                status_code=403, 
                detail="Access restricted to company users."
            )
        return UserInfo(
            email=user_info["email"],
            role="admin" if user_info["email"].endswith("@curefit.com") else "viewer"
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token") 