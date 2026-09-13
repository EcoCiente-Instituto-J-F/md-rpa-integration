from loguru import logger


logger.add(

"logs/migration.log",

rotation="10 MB",

level="INFO"

)