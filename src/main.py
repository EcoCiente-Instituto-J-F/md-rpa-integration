"""
Entrada principal da aplicação RPA.
"""
import sys
from config.logging_config import get_logger
from rpa.orchestrator import MigrationOrchestrator
from config.settings import settings

logger = get_logger()

from datetime import datetime
def main():
    print("Início:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

            print("Fim:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return 0



        else:


            logger.error(
                "Migração finalizada com falhas"
            )

            print("Fim:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
    
