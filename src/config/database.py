"""
Configuração das conexões com bancos de dados.

Responsável por:
- Criar engines SQLAlchemy
- Gerenciar sessões
- Separar banco legado e banco destino
- Garantir conexão reutilizável pelo RPA/ETL
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

from config.settings import settings


# =====================================================
# BANCO LEGADO
# =====================================================

legacy_engine = create_engine(
    settings.LEGACY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)


LegacySession = sessionmaker(
    bind=legacy_engine,
    autocommit=False,
    autoflush=False
)


# =====================================================
# BANCO NOVO NORMALIZADO
# =====================================================

target_engine = create_engine(
    settings.TARGET_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)


TargetSession = sessionmaker(
    bind=target_engine,
    autocommit=False,
    autoflush=False
)


# Base para futuros Models ORM
Base = declarative_base()



# =====================================================
# GERADORES DE SESSÃO
# =====================================================

def get_legacy_session():
    """
    Retorna conexão com banco legado.
    Usado na etapa Extract.
    """

    session = LegacySession()

    try:
        yield session

    finally:
        session.close()



def get_target_session():
    """
    Retorna conexão com banco novo.
    Usado na etapa Load.
    """

    session = TargetSession()

    try:
        yield session

    finally:
        session.close()



# =====================================================
# TESTE DE CONEXÃO
# =====================================================

def test_connection(engine, database_name):
    """
    Testa se banco está acessível.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        print(
            f"[OK] Conexão estabelecida: {database_name}"
        )

        return True


    except SQLAlchemyError as error:

        print(
            f"[ERRO] Falha conexão {database_name}: {error}"
        )

        return False



# =====================================================
# HEALTH CHECK DO SISTEMA
# =====================================================

def database_health_check():

    results = {

        "legacy":
            test_connection(
                legacy_engine,
                "Banco Legado"
            ),

        "target":
            test_connection(
                target_engine,
                "Banco Normalizado"
            )
    }


    return results