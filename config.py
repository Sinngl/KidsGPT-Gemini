from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    GEMINI_API_KEY: str

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    APP_NAME: str = "KidsGPT"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()