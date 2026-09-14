"""
Conector do banco legado.

Responsável por:
- Abrir conexão
- Executar consultas
- Retornar dados
- Controlar erros de conexão
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import legacy_engine
from config.logging_config import get_logger



logger = get_logger()



class LegacyConnector:


    def __init__(self):

        self.engine = legacy_engine



    # ==========================================
    # TESTAR CONEXÃO
    # ==========================================

    def test_connection(self):

        try:

            with self.engine.connect() as connection:

                connection.execute(
                    text("SELECT 1")
                )


            logger.info(
                "Conexão com banco legado realizada com sucesso"
            )


            return True



        except SQLAlchemyError as error:


            logger.error(
                f"Falha conexão banco legado: {error}"
            )


            return False



    # ==========================================
    # EXECUTAR SELECT
    # ==========================================

    def execute_query(
        self,
        query: str
    ):

        try:

            logger.info(
                "Executando consulta no banco legado"
            )


            with self.engine.connect() as connection:


                result = connection.execute(
                    text(query)
                )


                data = [
                    dict(row._mapping)
                    for row in result
                ]



            logger.info(
                f"Consulta finalizada. Registros encontrados: {len(data)}"
            )


            return data



        except SQLAlchemyError as error:


            logger.error(
                f"Erro execução SQL legado: {error}"
            )


            raise



    # ==========================================
    # EXECUTAR CONSULTA COM PARÂMETROS
    # ==========================================

    def execute_query_params(
        self,
        query: str,
        params: dict
    ):


        try:

            with self.engine.connect() as connection:


                result = connection.execute(
                    text(query),
                    params
                )


                return [
                    dict(row._mapping)
                    for row in result
                ]



        except SQLAlchemyError as error:


            logger.error(
                f"Erro consulta parametrizada: {error}"
            )


            raise
    def execute_batch_query(
    self,
    query
):


        return self.execute_query(
            query
        )
    def stream_query(
    self,
    query_builder,
    batch_size
):


        offset = 0


        while True:


            query = query_builder(

                batch_size,

                offset

            )


            data = self.execute_query(
                query
            )


            if not data:

                break



            yield data



            offset += batch_size