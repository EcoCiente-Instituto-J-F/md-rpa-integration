"""
Configurações globais do projeto RPA de migração.
"""

from pathlib import Path

from pydantic import (
    BaseSettings,
    SettingsConfigDict
)



BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):


    # ==============================
    # Aplicação
    # ==============================

    APP_NAME: str = "Migration RPA System"

    ENVIRONMENT: str = "development"

    DEBUG: bool = True



    # ==============================
    # Banco
    # ==============================

    LEGACY_DATABASE_URL: str

    TARGET_DATABASE_URL: str


    TARGET_SCHEMA: str = "public"


    DB_POOL_SIZE: int = 10

    DB_MAX_OVERFLOW: int = 20



    # ==============================
    # ETL
    # ==============================

    BATCH_SIZE: int = 500

    MAX_RETRIES: int = 3

    TIMEOUT_SECONDS: int = 60



    MIGRATION_MODE: str = "FULL"



    # ==============================
    # Auditoria
    # ==============================

    ENABLE_AUDIT: bool = True



    # ==============================
    # Diretórios
    # ==============================

    DATA_PATH: Path = BASE_DIR / "data"

    LOG_PATH: Path = BASE_DIR / "logs"

    REPORT_PATH: Path = BASE_DIR / "reports"



    # ==============================
    # Logs
    # ==============================

    LOG_LEVEL: str = "INFO"

    LOG_FILE_NAME: str = "migration.log"



    # ==============================
    # Segurança
    # ==============================

    SECRET_KEY: str | None = None



    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True

    )



    def create_directories(self):

        self.DATA_PATH.mkdir(
            exist_ok=True
        )

        self.LOG_PATH.mkdir(
            exist_ok=True
        )

        self.REPORT_PATH.mkdir(
            exist_ok=True
        )



settings = Settings()


settings.create_directories()