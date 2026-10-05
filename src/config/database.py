"""Engines e sessões dos bancos legado e destino."""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from config.settings import settings

_OPTIONS = {"pool_pre_ping": True, "connect_args": {"connect_timeout": 5}}

legacy_engine = create_engine(settings.LEGACY_DATABASE_URL, **_OPTIONS)
target_engine = create_engine(settings.TARGET_DATABASE_URL, **_OPTIONS)

TargetSession = sessionmaker(bind=target_engine)


def database_health_check():
    """Devolve, por banco, o endereço (sem senha) e o erro de conexão ou None."""
    result = {}
    for name, engine in (("legado", legacy_engine), ("destino", target_engine)):
        url = engine.url
        error = None
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            error = str(getattr(exc, "orig", exc)).strip().splitlines()[0]
        result[name] = {
            "alvo": f"{url.host}:{url.port or 5432}/{url.database}",
            "erro": error,
        }
    return result
