"""Configurações do projeto, lidas do .env."""

import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Empacotado com PyInstaller, o .env e os logs ficam ao lado do executável.
BASE_DIR = (
    Path(sys.executable).parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent.parent
)


class Settings(BaseSettings):
    LEGACY_DATABASE_URL: str
    TARGET_DATABASE_URL: str
    MAX_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"
    LOG_PATH: Path = BASE_DIR / "logs"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # .env antigos têm variáveis que não são mais lidas
    )


settings = Settings()
