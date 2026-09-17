"""
Entrada principal da aplicação RPA.
"""
import sys
from config.logging_config import get_logger
from src.rpa.orchestrator import MigrationOrchestrator

logger = get_logger()

def main():

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