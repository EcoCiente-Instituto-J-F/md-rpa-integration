"""
Validadores da migração.

Responsável por:
- Validar dados antes da carga
- Bloquear registros inconsistentes
- Garantir qualidade dos dados
- Registrar problemas encontrados
"""


import re

from config.logging_config import get_logger



logger = get_logger()



class DataValidator:



    def __init__(self):


        self.errors = []



    # =====================================================
    # REGISTRAR ERRO
    # =====================================================

    def add_error(
        self,
        entity,
        field,
        value,
        message
    ):


        error = {


            "entity":
                entity,


            "field":
                field,


            "value":
                value,


            "message":
                message

        }


        self.errors.append(
            error
        )


        logger.warning(

            f"Validação falhou: "
            f"{entity}.{field} - {message}"

        )



    # =====================================================
    # VALIDAR CAMPO OBRIGATÓRIO
    # =====================================================

    def required(
        self,
        entity,
        field,
        value
    ):


        if value is None or value == "":


            self.add_error(

                entity,

                field,

                value,

                "Campo obrigatório vazio"

            )


            return False



        return True



    # =====================================================
    # VALIDAR EMAIL
    # =====================================================

    def validate_email(
        self,
        email
    ):


        if not email:

            return False



        pattern = (

            r"^[\w\.-]+@[\w\.-]+\.\w+$"

        )



        return bool(

            re.match(
                pattern,
                email
            )

        )



    # =====================================================
    # VALIDAR CPF
    # =====================================================

    def validate_cpf(
        self,
        cpf
    ):


        if not cpf:

            return False



        cpf = re.sub(

            r"\D",

            "",

            str(cpf)

        )



        return len(cpf) == 11



    # =====================================================
    # VALIDAR CNPJ
    # =====================================================

    def validate_cnpj(
        self,
        cnpj
    ):


        if not cnpj:

            return False



        cnpj = re.sub(

            r"\D",

            "",

            str(cnpj)

        )



        return len(cnpj) == 14



    # =====================================================
    # VALIDAR CEP
    # =====================================================

    def validate_cep(
        self,
        cep
    ):


        if not cep:

            return False



        cep = re.sub(

            r"\D",

            "",

            str(cep)

        )



        return len(cep) == 8



    # =====================================================
    # VALIDAR USUÁRIO
    # =====================================================

    def validate_usuario(
        self,
        usuario
    ):


        valid = True



        if not self.required(

            "usuario",

            "nome",

            usuario.get("nome")

        ):

            valid = False



        email = usuario.get(
            "email"
        )



        if email and not self.validate_email(email):


            self.add_error(

                "usuario",

                "email",

                email,

                "Email inválido"

            )


            valid = False



        cpf = usuario.get(
            "cpf"
        )



        if cpf and not self.validate_cpf(cpf):


            self.add_error(

                "usuario",

                "cpf",

                cpf,

                "CPF inválido"

            )


            valid = False



        return valid



    # =====================================================
    # VALIDAR ENDEREÇO
    # =====================================================

    def validate_endereco(
        self,
        endereco
    ):


        valid = True



        if not self.required(

            "endereco",

            "cidade",

            endereco.get("cidade")

        ):

            valid = False



        cep = endereco.get(
            "cep"
        )



        if cep and not self.validate_cep(cep):


            self.add_error(

                "endereco",

                "cep",

                cep,

                "CEP inválido"

            )


            valid = False



        return valid



    # =====================================================
    # VALIDAR DATASET COMPLETO
    # =====================================================

    def validate_dataset(
        self,
        dataset
    ):


        logger.info(

            "Iniciando validação dos dados"

        )


        valid_records = {}



        if "usuarios" in dataset:


            valid_records["usuarios"] = []



            for usuario in dataset["usuarios"]:


                if self.validate_usuario(usuario):


                    valid_records["usuarios"].append(

                        usuario

                    )



        if "enderecos" in dataset:


            valid_records["enderecos"] = []



            for endereco in dataset["enderecos"]:


                if self.validate_endereco(endereco):


                    valid_records["enderecos"].append(

                        endereco

                    )



        logger.info(

            f"Validação finalizada. "
            f"Erros encontrados: {len(self.errors)}"

        )


        return valid_records



    # =====================================================
    # RETORNAR ERROS
    # =====================================================

    def get_errors(self):


        return self.errors