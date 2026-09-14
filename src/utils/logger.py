import logging, os
os.makedirs("logs",exist_ok=True)
def get_logger():
    logging.basicConfig(filename="logs/migration.log",level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger("migration")
