"""
Serviço de carga dos dados migrados.

Responsável por:

- Inserir dados no banco destino
- Utilizar transação externa
- Registrar IDs criados
- Manter integridade referencial
"""


from sqlalchemy import text

from sqlalchemy.exc import SQLAlchemyError


from src.load.primary_keys import PRIMARY_KEYS

from config.logging_config import get_logger



logger = get_logger()



class InsertService:



    def __init__(
        self,
        data_mapper
    ):


        self.data_mapper = data_mapper



    # =====================================================
    # INSERT GENÉRICO
    # =====================================================

    def insert(
        self,
        table,
        data,
        session
    ):


        primary_key = PRIMARY_KEYS.get(
            table
        )



        if not primary_key:


            raise Exception(

                f"PK não configurada para {table}"

            )



        columns = ", ".join(
            data.keys()
        )



        values = ", ".join(

            [
                f":{column}"

                for column in data.keys()

            ]

        )



        query = f"""

        INSERT INTO {table}

        ({columns})

        VALUES

        ({values})

        RETURNING {primary_key};

        """



        result = self.retry.execute(

    session.execute,

    text(query),

    data

)


        return result.fetchone()[0]



    # =====================================================
    # USUARIO
    # =====================================================

    def insert_usuario(
        self,
        usuarios,
        session
    ):


        logger.info(
            "Inserindo usuários"
        )



        for usuario in usuarios:



            new_id = self.insert(

                "usuario",

                usuario,

                session

            )



            old_id = usuario.get(

                "legacy_usuario_id"

            )



            self.data_mapper.save_mapping(

                "usuario",

                old_id,

                new_id

            )



    # =====================================================
    # ENDEREÇO
    # =====================================================

    def insert_endereco(
        self,
        enderecos,
        session
    ):


        logger.info(
            "Inserindo endereços"
        )



        for endereco in enderecos:



            new_id = self.insert(

                "endereco",

                endereco,

                session

            )



            old_id = endereco.get(

                "legacy_endereco_id"

            )



            self.data_mapper.save_mapping(

                "endereco",

                old_id,

                new_id

            )



    # =====================================================
    # CARGA PRINCIPAL
    # =====================================================

    def load_dataset(
        self,
        dataset,
        session
    ):


        logger.info(

            "===== INÍCIO LOAD ====="

        )



        try:



            # Ordem respeitando FK


            if "enderecos" in dataset:


                self.insert_endereco(

                    dataset["enderecos"],

                    session

                )



            if "usuarios" in dataset:


                self.insert_usuario(

                    dataset["usuarios"],

                    session

                )



            logger.info(

                "===== LOAD FINALIZADO ====="

            )



        except SQLAlchemyError as error:


            logger.error(

                f"Erro durante carga: {error}"

            )


            raise