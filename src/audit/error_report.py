"""
Relatório de erros da migração.

Responsável por:
- Registrar falhas individuais
- Armazenar registros problemáticos
- Controlar tentativas de reprocessamento
- Gerar histórico de erros
"""


from datetime import datetime

from config.logging_config import get_logger



logger = get_logger()



class ErrorReport:



    def __init__(self):


        self.errors = []



    # =====================================================
    # REGISTRAR ERRO
    # =====================================================

    def add_error(

        self,

        table,

        record_id,

        error,

        operation

    ):


        error_data = {


            "table":

                table,


            "record_id":

                record_id,


            "operation":

                operation,


            "error":

                str(error),


            "status":

                "PENDING_RETRY",


            "created_at":

                datetime.now()

        }



        self.errors.append(
            error_data
        )



        logger.error(

            f"""
Falha registrada

Tabela:
{table}

Registro:
{record_id}

Operação:
{operation}

Erro:
{error}

"""

        )



    # =====================================================
    # MARCAR COMO RESOLVIDO
    # =====================================================

    def resolve_error(

        self,

        index

    ):


        if index < len(self.errors):


            self.errors[index]["status"] = "RESOLVED"



            logger.info(

                f"Erro {index} resolvido"

            )



    # =====================================================
    # RETORNAR ERROS
    # =====================================================

    def get_errors(self):


        return self.errors



    # =====================================================
    # CONTADOR
    # =====================================================

    def count(self):


        return len(
            self.errors
        )



    # =====================================================
    # EXPORTAR RELATÓRIO
    # =====================================================

    def generate_report(self):


        report = {


            "total_errors":

                len(self.errors),


            "generated_at":

                datetime.now(),


            "errors":

                self.errors

        }


        return report
    
class DataValidator:


    def __init__(
        self,
        error_report=None
    ):


        self.errors = []


        self.error_report = error_report