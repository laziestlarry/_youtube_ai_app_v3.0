from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import os

# Load .env file from the root of the mini-app
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class MiniAppConfig(BaseSettings):
    app_port: int = Field(default=8080, env="APP_PORT")
    main_platform_url: str = Field(default="http://localhost:8000", env="MAIN_PLATFORM_URL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    serper_api_key: Optional[str] = Field(None, env="SERPER_API_KEY")

    class Config:
        env_file_encoding = 'utf-8'

settings = MiniAppConfig()