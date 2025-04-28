import os
from typing import Dict, List, ClassVar, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PerkBE"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Chethu_8867"
    POSTGRES_DB: str = "perkbe"
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key"  # Change this to a secure secret key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # User roles
    USER_ROLES: ClassVar[Dict[str, List[str]]] = {
        "admin": ["read", "write", "delete"],
        "editor": ["read", "write"],
        "viewer": ["read"]
    }

    class Config:
        env_file = ".env"
        extra = "ignore"  # This will ignore any extra fields in environment variables
        case_sensitive = True

settings = Settings() 