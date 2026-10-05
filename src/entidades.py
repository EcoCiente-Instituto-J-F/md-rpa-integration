"""
Entidades migradas, na ordem exigida pelas chaves estrangeiras.

Cada FK é (coluna no destino, entidade pai, obrigatória). O ID legado do pai
vem no registro como `legacy_<pai>_id`.
"""

from typing import NamedTuple


class Entidade(NamedTuple):
    nome: str
    dataset: str
    tabela_legado: str
    tabela_destino: str
    pk_destino: str
    fks: tuple = ()


ENTIDADES = (
    Entidade("endereco", "enderecos", "endereco", "tb_enderecos", "id_endereco"),
    Entidade(
        "usuario",
        "usuarios",
        "usuario",
        "tb_usuarios",
        "id_usuario",
        (("endereco_id", "endereco", True),),
    ),
    Entidade(
        "sindico",
        "sindicos",
        "sindico",
        "tb_sindicos",
        "id_sindico",
        (("usuario_id", "usuario", True),),
    ),
    Entidade(
        "condominio",
        "condominios",
        "condominio",
        "tb_condominios",
        "id_condominio",
        (("endereco_id", "endereco", False), ("sindico_id", "sindico", False)),
    ),
)
