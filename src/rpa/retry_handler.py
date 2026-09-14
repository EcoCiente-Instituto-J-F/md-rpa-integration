"""
Controle de retentativas da migração.

Responsável por:
- Reexecutar operações falhas
- Controlar tentativas
- Registrar erros temporários
"""


import time

from functools import wraps


from config.settings import settings

from config.logging_config import get_logger



logger = get_logger()



class RetryHandler:



    def __init__(
        self,
        retries=None,
        delay=5
    ):


        self.retries = (

            retries

            if retries

            else settings.MAX_RETRIES

        )


        self.delay = delay



    def execute(
        self,
        function,
        *args,
        **kwargs
    ):


        attempt = 0



        while attempt < self.retries:


            try:


                attempt += 1



                logger.info(

                    f"Executando {function.__name__} "
                    f"tentativa {attempt}/{self.retries}"

                )



                return function(
                    *args,
                    **kwargs
                )



            except Exception as error:


                logger.warning(

                    f"Falha tentativa {attempt}: {error}"

                )



                if attempt >= self.retries:


                    logger.error(

                        f"{function.__name__} "
                        "falhou definitivamente"

                    )


                    raise



                time.sleep(
                    self.delay
                )



    def retry(self, function):


        @wraps(function)

        def wrapper(
            *args,
            **kwargs
        ):


            return self.execute(

                function,

                *args,

                **kwargs

            )


        return wrapper