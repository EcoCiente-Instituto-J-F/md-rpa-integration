"""Extração: executa as consultas do legado e devolve listas de dicionários."""

from sqlalchemy import text

from config.database import legacy_engine
from config.logging_config import get_logger
from extract.legacy_queries import QUERIES

logger = get_logger()


class ExtractService:
    def __init__(self, engine=legacy_engine):
        self.engine = engine

    def extract_all(self):
        data = {}
        with self.engine.connect() as connection:
            for dataset, query in QUERIES.items():
                rows = connection.execute(text(query))
                data[dataset] = [dict(row._mapping) for row in rows]
                logger.info(f"Extraídos {len(data[dataset])} registros de {dataset}")
        return data
