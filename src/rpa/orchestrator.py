"""
Orquestrador principal da migração RPA.

Responsável por:

- Controlar fluxo completo ETL
- Coordenar serviços
- Garantir ordem de execução
- Controlar transações
- Registrar execução
"""


from datetime import datetime


from config.logging_config import get_logger

from config.database import database_health_check

from rpa.retry_handler import RetryHandler

from audit.migration_log import MigrationLogger

from audit.error_report import ErrorReport

from audit.reconciliation import Reconciliation

from extract.extract_service import ExtractService

from transform.data_mapper import DataMapper

from transform.normalization import DataNormalizer

from transform.validators import DataValidator

from load.insert_service import InsertService

from audit.reconciliation import Reconciliation

from config.database import legacy_engine, target_engine

from load.transaction_manager import TransactionManager



logger = get_logger()



class MigrationOrchestrator:



    def __init__(self):


        self.extract_service = ExtractService()

        self.retry = RetryHandler()


        self.mapper = DataMapper()

        self.audit = MigrationLogger()

        self.error_report = ErrorReport()

        self.normalizer = DataNormalizer()

        self.validator = DataValidator(        self.error_report
)

        self.insert_service = InsertService(

            self.mapper

        )


        self.transaction = TransactionManager()
        
        self.reconciliation = Reconciliation(
    legacy_engine,
    target_engine
)



    # =====================================================
    # DATABASE HEALTH CHECK
    # =====================================================

    def check_databases(self):


        logger.info(
            "Executando health check dos bancos"
        )


        status = database_health_check()



        if not all(status.values()):

            raise Exception(
                "Falha na conexão com bancos"
            )


        logger.info(
            "Bancos disponíveis"
        )



    # =====================================================
    # EXTRACT
    # =====================================================

    def extract(self):


        logger.info(
            "ETAPA 1 - EXTRAÇÃO"
        )


        data = self.extract_service.extract_all()


        logger.info(
            f"Registros extraídos: {len(data)}"
        )


        return data



    # =====================================================
    # TRANSFORM
    # =====================================================

    def transform(
        self,
        data
    ):


        logger.info(
            "ETAPA 2 - TRANSFORMAÇÃO"
        )


        return self.mapper.transform_dataset(
            data
        )



    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(
        self,
        data
    ):


        logger.info(
            "ETAPA 3 - NORMALIZAÇÃO"
        )


        return self.normalizer.normalize_dataset(
            data
        )



    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
        data
    ):


        logger.info(
            "ETAPA 4 - VALIDAÇÃO"
        )


        valid_data = self.validator.validate_dataset(
            data
        )


        errors = self.validator.get_errors()



        if errors:


            logger.warning(

                f"{len(errors)} registros inválidos encontrados"

            )



        else:


            logger.info(
                "Dados aprovados na validação"
            )



        return valid_data



    # =====================================================
    # LOAD
    # =====================================================

    def load(
        self,
        data
    ):


        logger.info(
            "ETAPA 5 - CARGA"
        )


        with self.transaction.transaction() as session:



            self.insert_service.load_dataset(

                data,

                session

            )

            for table, records in data.items():


                self.audit.register_table(

                    table_name=table,

                    extracted=len(records),

                    inserted=len(records),

                    errors=0

                )



        logger.info(
            "Carga concluída"
        )

    def run_reconciliation(self):


        logger.info(
            "Executando reconciliação"
        )


        result = self.reconciliation.run({

            "usuario":
            "usuario",

            "endereco":
            "endereco"

        })


        return result

    # =====================================================
    # EXECUÇÃO PRINCIPAL
    # =====================================================

    def execute(self):


        start_time = datetime.now()


        self.audit.start()



        logger.info(
            "===================================="
        )

        logger.info(
            "INICIANDO MIGRAÇÃO RPA"
        )



        try:


            self.check_databases()



            extracted = self.extract()



            mapped = self.transform(
                extracted
            )



            normalized = self.normalize(
                mapped
            )



            validated = self.validate(
                normalized
            )



            self.retry.execute(

                    self.load,

                    validated

                )

            self.run_reconciliation()


            end_time = datetime.now()



            logger.info(

                "MIGRAÇÃO FINALIZADA COM SUCESSO"

            )


            logger.info(

                f"Tempo execução: {end_time-start_time}"

            )


            self.audit.finish(
    success=True
)


            return True



        except Exception as error:


                self.audit.finish(
                    success=False
                )


                logger.exception(
                    f"Migração falhou: {error}"
                )


                return False