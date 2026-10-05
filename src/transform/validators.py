"""Validação: separa os registros que não podem ser carregados e diz por quê."""

import re

from config.logging_config import get_logger
from entidades import ENTIDADES

logger = get_logger()

_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def _digits(value, length):
    return len(re.sub(r"\D", "", str(value))) == length


# entidade -> [(campo, regra, motivo)]. A regra recebe o valor do campo.
_OBRIGATORIO = (lambda value: value not in (None, ""), "Campo obrigatório vazio")
RULES = {
    "tipo_usuario": [("nome_tipo", *_OBRIGATORIO)],
    "tipo_condominio": [("nome_tipo", *_OBRIGATORIO)],
    "endereco": [
        ("cep", lambda v: not v or _digits(v, 8), "CEP deve ter 8 dígitos"),
    ],
    "usuario": [
        ("nome_usuario", *_OBRIGATORIO),
        ("email_usuario", *_OBRIGATORIO),
        ("email_usuario", lambda v: not v or bool(_EMAIL.match(v)), "E-mail inválido"),
        ("cpf", lambda v: not v or _digits(v, 11), "CPF deve ter 11 dígitos"),
    ],
    "telefone": [("numero_contato", *_OBRIGATORIO)],
    "sindico": [],
    "condominio": [
        ("nome_condominio", *_OBRIGATORIO),
        ("cnpj", lambda v: not v or _digits(v, 14), "CNPJ deve ter 14 dígitos"),
    ],
    "torre": [("nome_torre", *_OBRIGATORIO)],
    "morador": [],
    "cooperativa": [
        ("nome_cooperativa", *_OBRIGATORIO),
        ("cnpj_cooperativa", *_OBRIGATORIO),
        (
            "cnpj_cooperativa",
            lambda v: not v or _digits(v, 14),
            "CNPJ deve ter 14 dígitos",
        ),
    ],
}


def rejection(entidade, record, campo, motivo):
    """Formato único de registro rejeitado, usado na validação e na carga."""
    return {
        "entidade": entidade,
        "legacy_id": record.get(f"legacy_{entidade}_id"),
        "campo": campo,
        "valor": None if record.get(campo) is None else str(record.get(campo)),
        "motivo": motivo,
    }


class DataValidator:
    def __init__(self):
        self.errors = []

    def validate(self, entidade, record):
        failures = [
            rejection(entidade, record, campo, motivo)
            for campo, rule, motivo in RULES[entidade]
            if not rule(record.get(campo))
        ]
        self.errors.extend(failures)
        return not failures

    def validate_dataset(self, dataset):
        valid = {
            e.dataset: [
                r for r in dataset.get(e.dataset, []) if self.validate(e.nome, r)
            ]
            for e in ENTIDADES
        }
        logger.info(f"Validação finalizada. Rejeições: {len(self.errors)}")
        return valid
