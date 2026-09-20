"""
Normalização de dados da migração.

Responsável por:
- Padronizar textos
- Limpar dados inconsistentes
- Normalizar contatos
- Corrigir formatos
- Preparar dados para validação e carga
"""


import re
from datetime import datetime

from config.logging_config import get_logger



logger = get_logger()



class DataNormalizer:



    # =====================================================
    # TEXTO
    # =====================================================

    def normalize_text(
        self,
        value
    ):

        """
        Remove espaços extras
        e padroniza texto.
        """

        if value is None:

            return None


        value = str(value)


        value = value.strip()


        value = re.sub(
            r"\s+",
            " ",
            value
        )


        return value



    # =====================================================
    # NOME
    # =====================================================

    def normalize_name(
        self,
        name
    ):

        """
        Exemplo:

        '  JOÃO DA SILVA '

        vira:

        'João da Silva'
        """


        if not name:

            return None



        name = self.normalize_text(
            name
        )


        return name.title()



    # =====================================================
    # EMAIL
    # =====================================================

    def normalize_email(
        self,
        email
    ):


        if not email:

            return None



        email = email.strip().lower()



        return email



    # =====================================================
    # TELEFONE
    # =====================================================

    def normalize_phone(
        self,
        phone
    ):


        if not phone:

            return None



        # remove tudo que não é número

        phone = re.sub(
            r"\D",
            "",
            str(phone)
        )



        # Brasil:
        # adiciona DDD caso necessário
        #
        # Ex:
        # 999999999
        #
        # vira:
        # 999999999


        return phone



    # =====================================================
    # CPF / CNPJ
    # =====================================================

    def normalize_document(
        self,
        document
    ):


        if not document:

            return None



        return re.sub(
            r"\D",
            "",
            str(document)
        )



    # =====================================================
    # CEP
    # =====================================================

    def normalize_zipcode(
        self,
        zipcode
    ):


        if not zipcode:

            return None



        zipcode = re.sub(
            r"\D",
            "",
            str(zipcode)
        )



        return zipcode.zfill(8)



    # =====================================================
    # DATAS
    # =====================================================

    def normalize_date(
        self,
        date_value
    ):


        if not date_value:

            return None



        if isinstance(
            date_value,
            datetime
        ):

            return date_value



        formats = [

            "%d/%m/%Y",

            "%Y-%m-%d",

            "%d-%m-%Y"

        ]



        for fmt in formats:


            try:

                return datetime.strptime(
                    str(date_value),
                    fmt
                )


            except ValueError:

                continue



        logger.warning(

            f"Data inválida encontrada: {date_value}"

        )


        return None



    # =====================================================
    # BOOLEAN
    # =====================================================

    def normalize_boolean(
        self,
        value
    ):


        if value is None:

            return False



        true_values = [

            "sim",

            "s",

            "true",

            "1",

            1,

            True

        ]



        return value in true_values



    # =====================================================
    # NORMALIZAR USUÁRIO
    # =====================================================

    def normalize_usuario(
        self,
        usuario
    ):


        return {
            **usuario,


            "nome":
                self.normalize_name(
                    usuario.get("nome")
                ),



            "email":
                self.normalize_email(
                    usuario.get("email")
                ),



            "telefone":
                self.normalize_phone(
                    usuario.get("telefone")
                ),



            "cpf":
                self.normalize_document(
                    usuario.get("cpf")
                ),



            "ativo":
                self.normalize_boolean(
                    usuario.get("ativo")
                )

        }



    # =====================================================
    # NORMALIZAR ENDEREÇO
    # =====================================================

    def normalize_endereco(
        self,
        endereco
    ):


        return {
            **endereco,


            "logradouro":
                self.normalize_text(
                    endereco.get("logradouro")
                ),




            "cidade":
                self.normalize_name(
                    endereco.get("cidade")
                ),


            "estado":
                self.normalize_text(
                    endereco.get("estado")
                ),


            "cep":
                self.normalize_zipcode(
                    endereco.get("cep")
                )

        }



    # =====================================================
    # NORMALIZA DATASET COMPLETO
    # =====================================================

    def normalize_dataset(
        self,
        dataset
    ):


        logger.info(
            "Iniciando normalização dos dados"
        )



        normalized = {}



        if "usuarios" in dataset:


            normalized["usuarios"] = [

                self.normalize_usuario(item)

                for item in dataset["usuarios"]

            ]



        if "enderecos" in dataset:


            normalized["enderecos"] = [

                self.normalize_endereco(item)

                for item in dataset["enderecos"]

            ]



        # Síndicos não têm campos a normalizar: repassa sem descartar
        if "sindicos" in dataset:

            normalized["sindicos"] = list(
                dataset["sindicos"]
            )


        logger.info(
            "Normalização finalizada"
        )



        return normalized