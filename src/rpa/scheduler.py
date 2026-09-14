"""
Scheduler do RPA.

Responsável por:
- Agendar execuções automáticas
- Controlar frequência da migração
- Evitar execuções duplicadas
"""


import time

from datetime import datetime

from threading import Lock


from config.logging_config import get_logger

from config.settings import settings

from src.rpa.orchestrator import MigrationOrchestrator



logger = get_logger()



class MigrationScheduler:



    def __init__(self):


        self.lock = Lock()


        self.running = False


        self.orchestrator = MigrationOrchestrator()



    # =====================================================
    # EXECUTAR MIGRAÇÃO
    # =====================================================

    def run_migration(self):


        if self.running:


            logger.warning(

                "Migração já está em execução"

            )


            return



        with self.lock:


            self.running = True



            logger.info(

                "Scheduler iniciando migração"

            )



            try:


                success = self.orchestrator.execute()



                if success:


                    logger.info(

                        "Execução automática concluída"

                    )


                else:


                    logger.error(

                        "Execução automática falhou"

                    )



            finally:


                self.running = False



    # =====================================================
    # EXECUÇÃO PERIÓDICA
    # =====================================================

    def start(
        self,
        interval_seconds=86400
    ):


        """
        Executa periodicamente.

        Padrão:

        86400 segundos = 24 horas

        """



        logger.info(

            "Scheduler iniciado"

        )



        while True:


            current_time = datetime.now()



            logger.info(

                f"Verificação scheduler: {current_time}"

            )



            self.run_migration()



            logger.info(

                f"Aguardando próxima execução "
                f"em {interval_seconds} segundos"

            )



            time.sleep(

                interval_seconds

            )