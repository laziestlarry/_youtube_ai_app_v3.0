import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Growth Masterplan — Clean Slate"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Separate DB for Clean Slate
    GROWTH_DATABASE_URL: str = "sqlite:///./growth_engine.db"
    
    class Config:
        case_sensitive = True
        env_prefix = "GROWTH_"

settings = Settings()
