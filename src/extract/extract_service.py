"""
Serviço de extração.

Responsável por:

- Orquestrar consultas
- Buscar dados do legado
- Preparar dados para transformação
"""

from extract.legacy_connector import LegacyConnector
from extract import legacy_queries
from config.logging_config import get_logger
from config.settings import settings


logger = get_logger()


class ExtractService:


    def __init__(self):

        self.connector = LegacyConnector()


    # ======================================
    # EXTRAÇÃO DE UMA TABELA
    # ======================================

    def extract_table(self, query):

        try:

            logger.info(
                "Iniciando extração"
            )


            data = self.connector.execute_query(
                query
            )


            logger.info(
                f"Extração concluída. Total registros: {len(data)}"
            )


            return data


        except Exception as error:


            logger.error(
                f"Erro durante extração: {error}"
            )


            raise



    # ======================================
    # EXTRAÇÃO COMPLETA DO LEGADO
    # ======================================

    # ======================================
    # EXTRAÇÃO COMPLETA DO LEGADO
    # ======================================

    def extract_all(self):

        logger.info(
            "Extração completa do legado iniciada"
        )


        extracted_data = {}


        extracted_data["usuarios"] = self.extract_table(
            legacy_queries.get_users()
        )


        extracted_data["enderecos"] = self.extract_table(
            legacy_queries.get_addresses()
        )


        extracted_data["condominios"] = self.extract_table(
            legacy_queries.get_condominiums()
        )


        extracted_data["materiais"] = self.extract_table(
            legacy_queries.get_materials()
        )


        extracted_data["conteudos"] = self.extract_table(
            legacy_queries.get_educational_contents()
        )


        logger.info(
            "Extração completa finalizada"
        )


        return extracted_data



    # ======================================
    # EXTRAÇÃO EM LOTES
    # ======================================

    def extract_users_batches(self):


        logger.info(
            "Extração de usuários em lote iniciada"
        )


        for batch in self.connector.stream_query(
            legacy_queries.get_users_batch,
            settings.BATCH_SIZE
        ):


            logger.info(
                f"Lote extraído: {len(batch)} registros"
            )


            yield batch