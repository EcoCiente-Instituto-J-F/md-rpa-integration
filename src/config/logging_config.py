"""Logging: migration.log, errors.log, console e memória (para a interface)."""

import logging
import sys
from collections import deque

from config.settings import settings

settings.LOG_PATH.mkdir(parents=True, exist_ok=True)

memory_log = deque(maxlen=500)


class _MemoryHandler(logging.Handler):
    def emit(self, record):
        memory_log.append(self.format(record))


def _build_logger():
    logger = logging.getLogger("migration_rpa")
    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL.upper())
    logger.propagate = False

    general = logging.FileHandler(settings.LOG_PATH / "migration.log", encoding="utf-8")
    errors = logging.FileHandler(settings.LOG_PATH / "errors.log", encoding="utf-8")
    errors.setLevel(logging.ERROR)
    handlers = [general, errors, _MemoryHandler()]
    if sys.stderr:  # executável sem console não tem stderr
        handlers.append(logging.StreamHandler())

    formatter = logging.Formatter(
        "%(asctime)s | %(filename)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def get_logger():
    return _build_logger()
