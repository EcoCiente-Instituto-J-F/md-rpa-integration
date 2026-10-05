"""
Entidades migradas, na ordem exigida pelas chaves estrangeiras.

Cada FK é (coluna no destino, entidade pai, obrigatória). O ID legado do pai
vem no registro como `legacy_<pai>_id`.

`chave_natural` vale para tabelas de domínio: se o destino já tem uma linha
com o mesmo valor nessa coluna, ela é reaproveitada em vez de duplicada.
"""

from typing import NamedTuple


class Entidade(NamedTuple):
    nome: str
    dataset: str
    tabela_legado: str
    tabela_destino: str
    pk_destino: str
    fks: tuple = ()
    chave_natural: str | None = None


ENTIDADES = (
    Entidade(
        "tipo_usuario",
        "tipos_usuarios",
        "tipo_usuario",
        "tb_lkp_tipos_usuarios",
        "id_tipo_usuario",
        chave_natural="nome_tipo",
    ),
    Entidade(
        "tipo_condominio",
        "tipos_condominios",
        "tipo_condominio",
        "tb_lkp_tipos_condominios",
        "id_tipo_condominio",
        chave_natural="nome_tipo",
    ),
    Entidade("endereco", "enderecos", "endereco", "tb_enderecos", "id_endereco"),
    Entidade(
        "usuario",
        "usuarios",
        "usuario",
        "tb_usuarios",
        "id_usuario",
        (("tipo_usuario_id", "tipo_usuario", True), ("endereco_id", "endereco", True)),
    ),
    Entidade(
        "telefone",
        "telefones",
        "telefone_usuario",
        "tb_telefones",
        "id_telefone",
        (("usuario_id", "usuario", True),),
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
        (
            ("tipo_condominio_id", "tipo_condominio", True),
            ("endereco_id", "endereco", False),
            ("sindico_id", "sindico", False),
        ),
    ),
    Entidade(
        "torre",
        "torres",
        "torre",
        "tb_torres",
        "id_torre",
        (("condominio_id", "condominio", True),),
    ),
    Entidade(
        "morador",
        "moradores",
        "morador",
        "tb_moradores",
        "id_morador",
        (("usuario_id", "usuario", True), ("condominio_id", "condominio", True)),
    ),
    Entidade(
        "cooperativa",
        "cooperativas",
        "cooperativa",
        "tb_cooperativas",
        "id_cooperativa",
        (("usuario_id", "usuario", False),),
    ),
)
