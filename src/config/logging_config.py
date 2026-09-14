"""
Configuração centralizada de logs.

Responsável por:
- Padronizar formato dos logs
- Criar arquivos de auditoria
- Separar logs gerais e erros
- Permitir rastreabilidade da migração
"""

import logging
from pathlib import Path

from config.settings import settings



# =====================================================
# CRIAÇÃO DOS DIRETÓRIOS
# =====================================================

settings.LOG_PATH.mkdir(
    parents=True,
    exist_ok=True
)



# =====================================================
# FORMATO DO LOG
# =====================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(filename)s | "
    "%(levelname)s | "
    "%(message)s"
)


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"



# =====================================================
# FORMATTER
# =====================================================

formatter = logging.Formatter(
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT
)



# =====================================================
# HANDLER LOG GERAL
# =====================================================

general_handler = logging.FileHandler(
    settings.LOG_PATH / "migration.log",
    encoding="utf-8"
)


general_handler.setFormatter(
    formatter
)


general_handler.setLevel(
    logging.INFO
)



# =====================================================
# HANDLER SOMENTE ERROS
# =====================================================

error_handler = logging.FileHandler(
    settings.LOG_PATH / "errors.log",
    encoding="utf-8"
)


error_handler.setFormatter(
    formatter
)


error_handler.setLevel(
    logging.ERROR
)



# =====================================================
# LOGGER PRINCIPAL
# =====================================================

logger = logging.getLogger(
    "migration_rpa"
)


logger.setLevel(
    logging.INFO
)



# Evita duplicar logs
logger.propagate = False



# Adiciona handlers apenas uma vez

if not logger.handlers:

    logger.addHandler(
        general_handler
    )

    logger.addHandler(
        error_handler
    )



# =====================================================
# FUNÇÃO PARA OBTER LOGGER
# =====================================================

def get_logger():

    return logger