import sys
import os
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path (força o reconhecimento)
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DATABASE_URL: str = "sqlite:///./data/lucas_garage.db"
    UPLOAD_DIR: Path = Path("./uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    AI_API_KEY: Optional[str] = None
    AI_ENDPOINT: Optional[str] = None
    SECRET_KEY: str = "change_this_in_production_please"
    DEBUG: bool = True
    APP_NAME: str = "Lucas Garage"

    def __init__(self):
        super().__init__()
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        Path("./data").mkdir(parents=True, exist_ok=True)

settings = Settings()
