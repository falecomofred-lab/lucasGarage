import sys
from pathlib import Path

# Raiz do projeto
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Caminho ABSOLUTO do banco (não depende de onde o servidor é iniciado)
    DATABASE_URL: str = f"sqlite:///{(DATA_DIR / 'lucas_garage.db').as_posix()}"
    UPLOAD_DIR: Path = UPLOADS_DIR
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    AI_API_KEY: Optional[str] = None
    AI_ENDPOINT: Optional[str] = None
    SECRET_KEY: str = "change_this_in_production_please"

    # Senha do painel (dashboard/edição). Troque via .env: DASHBOARD_PASSWORD=suasenha
    DASHBOARD_PASSWORD: str = "lucasgarage"

    DEBUG: bool = True
    APP_NAME: str = "Lucas Garage"

    def __init__(self):
        super().__init__()
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
