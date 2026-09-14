"""
Reconciliação da migração.

Responsável por:
- Comparar origem e destino
- Identificar divergências
- Validar integridade da carga
- Gerar relatório de conferência
"""


from datetime import datetime

from sqlalchemy import text

from config.logging_config import get_logger



logger = get_logger()



class Reconciliation:



    def __init__(
        self,
        legacy_engine,
        target_engine
    ):

        self.legacy_engine = legacy_engine

        self.target_engine = target_engine


        self.results = []



    # =====================================================
    # CONTAR REGISTROS
    # =====================================================

    def count_records(
        self,
        engine,
        table
    ):


        query = text(
            f"""
            SELECT COUNT(*)
            FROM {table}
            """
        )


        with engine.connect() as connection:


            result = connection.execute(
                query
            )


            return result.scalar()



    # =====================================================
    # COMPARAR TABELA
    # =====================================================

    def compare_table(
        self,
        legacy_table,
        target_table
    ):


        logger.info(

            f"Iniciando reconciliação "
            f"{legacy_table} -> {target_table}"

        )



        try:


            legacy_count = self.count_records(

                self.legacy_engine,

                legacy_table

            )



            target_count = self.count_records(

                self.target_engine,

                target_table

            )



            difference = (

                legacy_count -

                target_count

            )



            status = (

                "OK"

                if difference == 0

                else

                "DIVERGENCIA"

            )



            result = {


                "source_table":

                    legacy_table,


                "target_table":

                    target_table,


                "source_count":

                    legacy_count,


                "target_count":

                    target_count,


                "difference":

                    difference,


                "status":

                    status,


                "checked_at":

                    datetime.now()

            }



            self.results.append(
                result
            )



            if status == "OK":


                logger.info(

                    f"Tabela validada: {legacy_table}"

                )


            else:


                logger.error(

                    f"Divergência encontrada: "
                    f"{legacy_table}"

                )



            return result



        except Exception as error:


            logger.error(

                f"Erro reconciliação {legacy_table}: {error}"

            )


            raise



    # =====================================================
    # RECONCILIAÇÃO COMPLETA
    # =====================================================

    def run(
        self,
        mappings
    ):


        """
        Exemplo:

        mappings = {

            "usuario":
            "usuario",

            "material":
            "material"

        }

        """


        logger.info(

            "===== INÍCIO RECONCILIAÇÃO ====="

        )



        for legacy, target in mappings.items():


            self.compare_table(

                legacy,

                target

            )



        logger.info(

            "===== FIM RECONCILIAÇÃO ====="

        )


        return self.results



    # =====================================================
    # RELATÓRIO FINAL
    # =====================================================

    def report(self):


        total = len(
            self.results
        )


        success = len(

            [

                item

                for item in self.results

                if item["status"] == "OK"

            ]

        )


        return {


            "tables_checked":

                total,


            "success":

                success,


            "failed":

                total - success,


            "results":

                self.results

        }