"""
Entrada principal da aplicação RPA.
"""
import sys
from config.logging_config import get_logger
from rpa.orchestrator import MigrationOrchestrator
from config.settings import settings

logger = get_logger()

def main():

    print("LEGACY:", settings.LEGACY_DATABASE_URL)
    print("TARGET:", settings.TARGET_DATABASE_URL)
    logger.info(
        "========== MIGRATION RPA START =========="
    )


    try:


        orchestrator = MigrationOrchestrator()


        success = orchestrator.execute()



        if success:


            logger.info(
                "Migração executada com sucesso"
            )


            return 0



        else:


            logger.error(
                "Migração finalizada com falhas"
            )


            return 1



    except Exception as error:


        logger.exception(

            f"Erro crítico na aplicação: {error}"

        )


        return 1




if __name__ == "__main__":
    sys.exit(
        main()
    )