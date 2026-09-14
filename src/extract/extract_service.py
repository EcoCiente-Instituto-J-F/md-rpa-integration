"""
Serviço de extração.

Responsável por:
- Orquestrar consultas
- Buscar dados do legado
- Preparar dados para transformação
"""


from src.extract.legacy_connector import LegacyConnector

from src.extract import legacy_queries

from config.logging_config import get_logger

from src.rpa.retry_handler import RetryHandler

from config.settings import settings




logger = get_logger()



class ExtractService:



    def __init__(self):

        self.connector = LegacyConnector()



    # ======================================
    # EXTRAÇÃO DE UMA TABELA
    # ======================================

    def extract_table(
        self,
        query
    ):


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

    from config.settings import settings



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