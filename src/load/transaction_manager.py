"""
Gerenciador de transações da migração.

Responsável por:
- Controlar BEGIN / COMMIT / ROLLBACK
- Garantir atomicidade da carga
- Tratar falhas durante inserções
"""


from contextlib import contextmanager

from config.database import TargetSession

from config.logging_config import get_logger



logger = get_logger()



class TransactionManager:



    def __init__(self):

        self.session = None



    # =====================================================
    # ABRIR TRANSAÇÃO
    # =====================================================

    def begin(self):

        """
        Cria uma nova sessão
        e inicia transação.
        """


        self.session = TargetSession()



        logger.info(
            "Transação iniciada no banco destino"
        )


        return self.session



    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self):

        """
        Confirma todas as operações.
        """

        if self.session:


            self.session.commit()



            logger.info(
                "Transação confirmada (COMMIT)"
            )



    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self):

        """
        Desfaz operações pendentes.
        """

        if self.session:


            self.session.rollback()



            logger.error(
                "Transação revertida (ROLLBACK)"
            )



    # =====================================================
    # FECHAR SESSÃO
    # =====================================================

    def close(self):


        if self.session:


            self.session.close()



            logger.info(
                "Sessão do banco encerrada"
            )



    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    @contextmanager
    def transaction(self):

        """
        Uso:

        with transaction_manager.transaction():

             inserir dados


        Se tudo ocorrer:
            COMMIT


        Se ocorrer erro:
            ROLLBACK

        """


        session = self.begin()



        try:


            yield session



            self.commit()



        except Exception as error:


            self.rollback()



            logger.error(

                f"Erro na transação: {error}"

            )


            raise



        finally:


            self.close()