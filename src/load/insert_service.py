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

from load.primary_keys import PRIMARY_KEYS
from config.logging_config import get_logger
from rpa.retry_handler import RetryHandler


logger = get_logger()


class InsertService:

    def __init__(self, data_mapper):

        self.data_mapper = data_mapper
        self.retry = RetryHandler()


    # =====================================================
    # REMOVE CAMPOS INTERNOS DA MIGRAÇÃO
    # =====================================================

    def sanitize_data(
        self,
        data
    ):

        """
        Remove campos utilizados somente
        no controle da migração.

        Exemplo:

        Remove:
            legacy_usuario_id
            legacy_endereco_id

        Mantém:
            campos reais do banco destino
        """

        return {
            key: value
            for key, value in data.items()
            if not key.startswith("legacy_")
        }


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


        insert_data = self.sanitize_data(
            data
        )


        columns = ", ".join(
            insert_data.keys()
        )


        values = ", ".join(
            [
                f":{column}"
                for column in insert_data.keys()
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
            insert_data
        )


        return result.fetchone()[0]



    # =====================================================
    # USUÁRIO
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


            # Resolve FK agora: o mapeamento só existe após inserir endereços
            usuario["endereco_id"] = self.data_mapper.get_new_id(
                "endereco",
                usuario.get("legacy_endereco_id")
            )

            if not usuario.get("endereco_id"):

                raise Exception(
                    "Usuário sem endereço mapeado"
                )


            if not usuario.get("tipo_usuario_id"):

                raise Exception(
                    "Usuário sem tipo definido"
                )


            new_id = self.insert(
                "tb_usuarios",
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
    # SÍNDICO
    # =====================================================

    def insert_sindico(
        self,
        sindicos,
        session
    ):

        logger.info(
            "Inserindo síndicos"
        )


        for sindico in sindicos:


            sindico["usuario_id"] = self.data_mapper.get_new_id(
                "usuario",
                sindico.get("legacy_usuario_id")
            )

            new_id = self.insert(
                "tb_sindicos",
                sindico,
                session
            )


            old_id = sindico.get(
                "legacy_sindico_id"
            )


            self.data_mapper.save_mapping(
                "sindico",
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
                "tb_enderecos",
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


            if "sindicos" in dataset:

                self.insert_sindico(
                    dataset["sindicos"],
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