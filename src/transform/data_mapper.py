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

        """
        Guarda o relacionamento:

        ID antigo -> ID novo

        Exemplo:

        usuario legado:
            50

        usuario novo:
            120


        """

        self.id_mapping = {

            "usuario": {},

            "endereco": {},

            "condominio": {},

            "cooperativa": {},

            "material": {},

            "conteudo": {}

        }



    # =====================================================
    # USUARIO
    # =====================================================

    def map_usuario(
        self,
        usuario
    ):

        """
        Converte usuário legado
        para estrutura nova.
        """


        try:


            mapped = {


                # novo banco
                "nome":
                    usuario.get("nome"),


                "email":
                    usuario.get("email"),


                "telefone":
                    usuario.get("telefone"),


                "data_cadastro":
                    usuario.get(
                        "data_cadastro",
                        datetime.now()
                    ),


                "ativo":
                    True

            }



            logger.info(
                "Usuário convertido para modelo destino"
            )


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


            "bairro":
                endereco.get("bairro"),


            "cidade":
                endereco.get("cidade"),


            "estado":
                endereco.get("estado"),


            "cep":
                endereco.get("cep")

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
                cooperativa.get("nome"),


            "descricao":
                cooperativa.get("descricao"),


            "ativa":
                True

        }



    # =====================================================
    # CONDOMÍNIO
    # =====================================================

    def map_condominio(
        self,
        condominio
    ):


        return {


            "nome":
                condominio.get("nome"),


            "cnpj":
                condominio.get("cnpj"),


            "id_endereco":
                self.get_new_id(

                    "endereco",

                    condominio.get(
                        "id_endereco"
                    )

                )

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
                material.get("nome"),


            "descricao":
                material.get("descricao"),


            "categoria":
                material.get("categoria")

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
                conteudo.get("titulo"),


            "descricao":
                conteudo.get("descricao"),


            "url":
                conteudo.get("url")

        }



    # =====================================================
    # MAPEAR DATASET COMPLETO
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

                self.map_usuario(usuario)

                for usuario in dataset["usuarios"]

            ]



        if "enderecos" in dataset:


            transformed["enderecos"] = [

                self.map_endereco(endereco)

                for endereco in dataset["enderecos"]

            ]



        if "cooperativas" in dataset:


            transformed["cooperativas"] = [

                self.map_cooperativa(cooperativa)

                for cooperativa in dataset["cooperativas"]

            ]



        if "condominios" in dataset:


            transformed["condominios"] = [

                self.map_condominio(condominio)

                for condominio in dataset["condominios"]

            ]



        if "materiais" in dataset:


            transformed["materiais"] = [

                self.map_material(material)

                for material in dataset["materiais"]

            ]



        if "conteudos" in dataset:


            transformed["conteudos"] = [

                self.map_conteudo(conteudo)

                for conteudo in dataset["conteudos"]

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

        """
        Salva relacionamento:

        Banco antigo:
            ID 10

        Banco novo:
            ID 500

        """


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