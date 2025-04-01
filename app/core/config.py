import os
from typing import Dict, List, ClassVar, Optional
from google.oauth2 import service_account
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Perk Backend"
    API_V1_STR: str = "/api/v1"
    GOOGLE_CREDENTIALS_FILE: str = "/Users/chethangopal/Downloads/google_credentials.json"
    GOOGLE_CLIENT_ID: str = "66216119577-a7ftl7l154caoiu9eciakpeshac1muf2.apps.googleusercontent.com"
    
    # Add spreadsheet IDs for different platforms
    ANDROID_SHEET_ID: str = "1oV4OrTphr-PpfZLLtIRVm1tEErDeiVJfSllIyGI0e40"  # Your current sheet
    IOS_SHEET_ID: str = ""  # Add your new iOS sheet ID here
    
    # OAuth2 settings
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    
    # Using ClassVar for class-level constants that shouldn't be treated as settings
    SCOPES: ClassVar[List[str]] = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    USER_ROLES: ClassVar[Dict[str, List[str]]] = {
        "admin": ["read", "write", "delete"],
        "editor": ["read", "write"],
        "viewer": ["read"]
    }
    
    @property
    def CREDENTIALS(self):
        return service_account.Credentials.from_service_account_file(
            self.GOOGLE_CREDENTIALS_FILE, scopes=self.SCOPES
        )

    class Config:
        env_file = ".env"

settings = Settings() 