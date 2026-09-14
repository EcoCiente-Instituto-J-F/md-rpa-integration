"""
Queries do banco legado.

Responsável por:
- Consultas de extração
- Controle dos campos utilizados
- Padronização do dataset de saída
"""


# =====================================================
# USUÁRIO
# =====================================================

def get_users():


    return """

    SELECT

        u.id_usuario AS legacy_usuario_id,

        u.nome AS nome,

        u.email AS email,

        u.telefone AS telefone,

        u.cpf AS cpf,

        u.data_cadastro AS data_cadastro


    FROM usuario u;


    """



# =====================================================
# ENDEREÇO
# =====================================================

def get_addresses():


    return """

    SELECT

        e.id_endereco AS legacy_endereco_id,

        e.logradouro AS logradouro,

        e.numero AS numero,

        e.bairro AS bairro,

        e.cidade AS cidade,

        e.estado AS estado,

        e.cep AS cep


    FROM endereco e;


    """



# =====================================================
# CONDOMÍNIO
# =====================================================

def get_condominiums():


    return """

    SELECT

        c.id_condominio AS legacy_condominio_id,

        c.nome AS nome,

        c.cnpj AS cnpj,

        c.id_endereco AS legacy_endereco_id


    FROM condominio c;


    """



# =====================================================
# MATERIAL
# =====================================================

def get_materials():


    return """

    SELECT

        m.id_material AS legacy_material_id,

        m.nome AS nome,

        m.descricao AS descricao,

        m.categoria AS categoria


    FROM material m;


    """



# =====================================================
# CONTEÚDO EDUCATIVO
# =====================================================

def get_educational_contents():


    return """

    SELECT

        c.id_conteudo AS legacy_conteudo_id,

        c.titulo AS titulo,

        c.descricao AS descricao,

        c.url AS url


    FROM conteudo_educativo c;


    """

def get_users_batch(
    limit,
    offset
):


    return f"""

    SELECT

        u.id_usuario AS legacy_usuario_id,

        u.nome,

        u.email,

        u.telefone,

        u.cpf


    FROM usuario u


    ORDER BY u.id_usuario


    LIMIT {limit}

    OFFSET {offset};

    """