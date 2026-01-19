import os
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Growth Masterplan — Clean Slate"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Separate DB for Clean Slate
    DEFAULT_DATA_DIR: ClassVar[Path] = Path(os.getenv("DATA_DIR", ".")).resolve()
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DATA_DIR / 'growth_engine.db'}"
    
    class Config:
        case_sensitive = True
        env_prefix = "GROWTH_"

settings = Settings()
