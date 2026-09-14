"""
Controle de auditoria da migração.

Responsável por:
- Registrar execução
- Controlar quantidade de registros
- Armazenar status
- Gerar histórico da migração
"""


from datetime import datetime

from config.logging_config import get_logger



logger = get_logger()



class MigrationLogger:



    def __init__(self):


        self.execution = {

            "start_time": None,

            "end_time": None,

            "status": None,

            "tables": {}

        }



    # =====================================================
    # INÍCIO DA MIGRAÇÃO
    # =====================================================

    def start(self):


        self.execution["start_time"] = datetime.now()



        logger.info(

            "Auditoria: migração iniciada"

        )



    # =====================================================
    # REGISTRO DE TABELA
    # =====================================================

    def register_table(

        self,

        table_name,

        extracted,

        inserted,

        errors=0

    ):


        self.execution["tables"][table_name] = {


            "extracted":

                extracted,


            "inserted":

                inserted,


            "errors":

                errors,


            "timestamp":

                datetime.now()

        }



        logger.info(

            f"Auditoria tabela {table_name}: "

            f"extraídos={extracted}, "

            f"inseridos={inserted}, "

            f"erros={errors}"

        )



    # =====================================================
    # FINALIZAÇÃO
    # =====================================================

    def finish(

        self,

        success=True

    ):


        self.execution["end_time"] = datetime.now()



        self.execution["status"] = (

            "SUCCESS"

            if success

            else

            "FAILED"

        )



        logger.info(

            f"Auditoria finalizada: "
            f"{self.execution['status']}"

        )



    # =====================================================
    # OBTER RELATÓRIO
    # =====================================================

    def get_report(self):


        return self.execution



    # =====================================================
    # IMPRIMIR RESUMO
    # =====================================================

    def summary(self):


        print("\n")
        print("==============================")
        print("RELATÓRIO DE MIGRAÇÃO")
        print("==============================")



        print(

            f"Status: {self.execution['status']}"

        )



        print(

            f"Início: {self.execution['start_time']}"

        )



        print(

            f"Fim: {self.execution['end_time']}"

        )



        print("\nTabelas:")



        for table, data in self.execution["tables"].items():


            print(

                f"""

{table}

Origem:
{data['extracted']}

Destino:
{data['inserted']}

Falhas:
{data['errors']}

                """

            )