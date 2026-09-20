"""
Data Mapper da migração.

Responsável por:

- Converter modelo legado para modelo normalizado
- Mapear campos antigos para novos campos
- Controlar relacionamento entre IDs
- Preparar payloads para carga no banco destino
"""

from datetime import datetime

from config.logging_config import get_logger


logger = get_logger()


class DataMapper:

    def __init__(self):

        # Controle interno de relacionamento
        # Legado -> Novo
        self.id_mapping = {

            "usuario": {},

            "endereco": {},

            "sindico": {},

            "condominio": {},

            "cooperativa": {},

            "material": {},

            "conteudo": {}

        }


    # =====================================================
    # USUÁRIO
    # =====================================================

    def map_usuario(
        self,
        usuario
    ):

        try:

            mapped = {

                "nome_usuario":

                    usuario.get("nome"),


                "email_usuario":

                    usuario.get("email"),


                "senha_hash":

                    usuario.get(
                        "senha_hash",
                        "MIGRACAO_TEMP"
                    ),


                "cpf":

                    usuario.get("cpf"),


                "ativo":

                    usuario.get("ativo", True),


                "registro_em":

                    usuario.get(
                        "data_cadastro",
                        datetime.now()
                    ),


                "tipo_usuario_id":

                    usuario.get(
                        "tipo_usuario_id",
                        1
                    ),


                "endereco_id":

                    self.get_new_id(
                        "endereco",
                        usuario.get(
                            "legacy_endereco_id"
                        )
                    )

            }


            return mapped


        except Exception as error:

            logger.error(
                f"Erro mapeando usuário: {error}"
            )

            raise



    # =====================================================
    # ENDEREÇO
    # =====================================================

    def map_endereco(
        self,
        endereco
    ):

        return {


            "logradouro":

                endereco.get("logradouro"),


            "numero":

                endereco.get("numero"),


            "cidade":

                endereco.get("cidade"),


            "estado":

                endereco.get("estado"),


            "cep":

                endereco.get("cep"),


            "complemento":

                endereco.get("complemento")

        }



    # =====================================================
    # SÍNDICO
    # =====================================================

    def map_sindico(
        self,
        sindico
    ):


        return {


            "usuario_id":

                self.get_new_id(
                    "usuario",
                    sindico.get(
                        "legacy_usuario_id"
                    )
                )

        }



    # =====================================================
    # CONDOMÍNIO
    # =====================================================

    def map_condominio(
        self,
        condominio
    ):


        return {


            "nome_condominio":

                condominio.get(
                    "nome"
                ),


            "cnpj":

                condominio.get(
                    "cnpj"
                ),


            "endereco_id":

                self.get_new_id(
                    "endereco",
                    condominio.get(
                        "legacy_endereco_id"
                    )
                ),


            "sindico_id":

                self.get_new_id(
                    "sindico",
                    condominio.get(
                        "legacy_sindico_id"
                    )
                )

        }



    # =====================================================
    # COOPERATIVA
    # =====================================================

    def map_cooperativa(
        self,
        cooperativa
    ):


        return {


            "nome":

                cooperativa.get(
                    "nome"
                ),


            "descricao":

                cooperativa.get(
                    "descricao"
                ),


            "ativa":

                True

        }



    # =====================================================
    # MATERIAL
    # =====================================================

    def map_material(
        self,
        material
    ):


        return {


            "nome":

                material.get(
                    "nome"
                ),


            "descricao":

                material.get(
                    "descricao"
                )

        }



    # =====================================================
    # CONTEÚDO EDUCATIVO
    # =====================================================

    def map_conteudo(
        self,
        conteudo
    ):


        return {


            "titulo":

                conteudo.get(
                    "titulo"
                ),


            "descricao":

                conteudo.get(
                    "descricao"
                ),


            "url":

                conteudo.get(
                    "url"
                )

        }



    # =====================================================
    # DATASET COMPLETO
    # =====================================================

    def transform_dataset(
        self,
        dataset
    ):


        logger.info(
            "Iniciando transformação completa"
        )


        transformed = {}



        if "usuarios" in dataset:


            transformed["usuarios"] = [

                {

                    **self.map_usuario(usuario),
                    "legacy_endereco_id":
                        usuario.get("legacy_endereco_id"),


                    "legacy_usuario_id":

                        usuario.get(
                            "legacy_usuario_id"
                        )

                }


                for usuario in dataset["usuarios"]

            ]



        if "enderecos" in dataset:


            transformed["enderecos"] = [

                {

                    **self.map_endereco(endereco),


                    "legacy_endereco_id":

                        endereco.get(
                            "legacy_endereco_id"
                        )

                }


                for endereco in dataset["enderecos"]

            ]



        if "sindicos" in dataset:


            transformed["sindicos"] = [

                {

                    **self.map_sindico(sindico),
                    "legacy_usuario_id":
                        sindico.get("legacy_usuario_id"),


                    "legacy_sindico_id":

                        sindico.get(
                            "legacy_sindico_id"
                        )

                }


                for sindico in dataset["sindicos"]

            ]



        if "condominios" in dataset:


            transformed["condominios"] = [

                {

                    **self.map_condominio(condominio),


                    "legacy_condominio_id":

                        condominio.get(
                            "legacy_condominio_id"
                        )

                }


                for condominio in dataset["condominios"]

            ]



        if "cooperativas" in dataset:


            transformed["cooperativas"] = [

                self.map_cooperativa(item)

                for item in dataset["cooperativas"]

            ]



        if "materiais" in dataset:


            transformed["materiais"] = [

                self.map_material(item)

                for item in dataset["materiais"]

            ]



        if "conteudos" in dataset:


            transformed["conteudos"] = [

                self.map_conteudo(item)

                for item in dataset["conteudos"]

            ]



        logger.info(
            "Transformação concluída"
        )


        return transformed



    # =====================================================
    # CONTROLE DE IDS
    # =====================================================

    def save_mapping(
        self,
        entity,
        old_id,
        new_id
    ):


        if old_id is None:

            return


        self.id_mapping[entity][old_id] = new_id


        logger.info(

            f"Mapeamento criado {entity}: "
            f"{old_id} -> {new_id}"

        )



    def get_new_id(
        self,
        entity,
        old_id
    ):


        if old_id is None:

            return None


        return self.id_mapping.get(

            entity,

            {}

        ).get(

            old_id

        )