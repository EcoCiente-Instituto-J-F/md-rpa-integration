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
        u.id_endereco AS legacy_endereco_id,
        u.id_tipo_usuario AS tipo_usuario_id,
        u.nome AS nome,
        u.email AS email,
        NULL AS cpf,
        u.status AS ativo,
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

        e.rua AS logradouro,

        e.numero AS numero,

        e.bairro AS bairro,

        e.cidade AS cidade,

        e.estado AS estado,

        e.cep AS cep,

        e.complemento AS complemento


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
        m.reciclavel,
        m.compostavel,
        m.instrucoes_descarte,
        m.status

    FROM material m;

    """

# =====================================================
# SÍNDICO
# =====================================================

def get_managers():

    return """

    SELECT

        s.id_sindico AS legacy_sindico_id,
        s.cpf AS cpf,
        s.data_inicio_mandato AS data_inicio_mandato,
        s.data_fim_mandato AS data_fim_mandato,
        s.id_usuario AS legacy_usuario_id,
        s.id_condominio AS legacy_condominio_id

    FROM sindico s;

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
        c.tipo_conteudo AS tipo,
        c.nivel AS nivel,
        c.duracao AS duracao,
        c.data_publicacao AS data_publicacao,
        c.status AS status

    FROM conteudo_educativo c;

    """

def get_users_batch(limit, offset):

    return f"""

    SELECT

        u.id_usuario AS legacy_usuario_id,
        u.nome,
        u.email,
        t.numero AS telefone,
        NULL AS cpf

    FROM usuario u

    LEFT JOIN telefone_usuario t
        ON t.id_usuario = u.id_usuario

    ORDER BY u.id_usuario

    LIMIT {limit}

    OFFSET {offset};

    """