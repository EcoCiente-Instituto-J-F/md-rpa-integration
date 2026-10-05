"""Normalização: padroniza textos e formatos antes do mapeamento."""

import re

from config.logging_config import get_logger

logger = get_logger()

_PARTICULAS = {"da", "de", "do", "das", "dos", "e"}
# ponytail: texto fora desta lista vira False; acrescente o valor usado no legado.
_VERDADEIROS = {"sim", "s", "true", "t", "1", "ativo", "a"}


class DataNormalizer:
    def normalize_text(self, value):
        if value is None:
            return None
        return re.sub(r"\s+", " ", str(value)).strip() or None

    def normalize_name(self, name):
        """'  JOÃO DA SILVA ' vira 'João da Silva'."""
        name = self.normalize_text(name)
        if not name:
            return None
        words = name.lower().split(" ")
        return " ".join(
            word if index and word in _PARTICULAS else word.capitalize()
            for index, word in enumerate(words)
        )

    def normalize_email(self, email):
        return email.strip().lower() if email else None

    def normalize_digits(self, value):
        """CPF, CNPJ e telefone: só os dígitos."""
        return re.sub(r"\D", "", str(value)) or None if value else None

    def normalize_zipcode(self, zipcode):
        digits = self.normalize_digits(zipcode)
        return digits.zfill(8) if digits else None

    def normalize_boolean(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower() in _VERDADEIROS
        return bool(value)

    def normalize_usuario(self, usuario):
        return {
            **usuario,
            "nome": self.normalize_name(usuario.get("nome")),
            "email": self.normalize_email(usuario.get("email")),
            "cpf": self.normalize_digits(usuario.get("cpf")),
            "ativo": self.normalize_boolean(usuario.get("ativo")),
        }

    def normalize_endereco(self, endereco):
        return {
            **endereco,
            "logradouro": self.normalize_text(endereco.get("logradouro")),
            "cidade": self.normalize_name(endereco.get("cidade")),
            "estado": self.normalize_text(endereco.get("estado")),
            "cep": self.normalize_zipcode(endereco.get("cep")),
        }

    def normalize_condominio(self, condominio):
        return {
            **condominio,
            "nome": self.normalize_text(condominio.get("nome")),
            "cnpj": self.normalize_digits(condominio.get("cnpj")),
        }

    def normalize_dataset(self, dataset):
        normalizers = {
            "usuarios": self.normalize_usuario,
            "enderecos": self.normalize_endereco,
            "condominios": self.normalize_condominio,
        }
        # Datasets sem normalizador (síndicos) passam adiante sem alteração.
        normalized = {
            name: (
                [normalizers[name](item) for item in records]
                if name in normalizers
                else list(records)
            )
            for name, records in dataset.items()
        }
        logger.info("Normalização finalizada")
        return normalized
