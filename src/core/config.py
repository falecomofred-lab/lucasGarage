import os
import secrets
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

    # Chave secreta do login. NUNCA fica escrita no código:
    #  - se existir a variável de ambiente SECRET_KEY, usa ela;
    #  - senão, gera uma chave aleatória guardada em data/.secret_key.
    # Assim quem vê o código no GitHub não consegue forjar o cookie de login.
    SECRET_KEY: str = ""

    # Senha do painel (dashboard/edição). Troque via .env: DASHBOARD_PASSWORD=suasenha
    DASHBOARD_PASSWORD: str = "lucasgarage"

    DEBUG: bool = True
    APP_NAME: str = "Lucas Garage"

    def __init__(self):
        super().__init__()
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Resolve a chave secreta sem nunca gravá-la no código
        if not self.SECRET_KEY:
            self.SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
        if not self.SECRET_KEY:
            arq = DATA_DIR / ".secret_key"
            if arq.exists():
                self.SECRET_KEY = arq.read_text().strip()
            else:
                self.SECRET_KEY = secrets.token_hex(32)
                try:
                    arq.write_text(self.SECRET_KEY)
                except Exception:
                    pass


settings = Settings()
