"""Consultas de extração do banco legado, por dataset (ver sql/ecociente_legado_schema.sql)."""

QUERIES = {
    "tipos_usuarios": """
        SELECT id_tipo_usuario AS legacy_tipo_usuario_id, nome_tipo, descricao
        FROM tipo_usuario
        ORDER BY id_tipo_usuario
    """,
    "tipos_condominios": """
        SELECT id_tipo_condominio AS legacy_tipo_condominio_id, nome_tipo, descricao
        FROM tipo_condominio
        ORDER BY id_tipo_condominio
    """,
    "enderecos": """
        SELECT
            id_endereco AS legacy_endereco_id,
            rua AS logradouro,
            numero,
            bairro,
            cidade,
            estado,
            cep,
            complemento
        FROM endereco
        ORDER BY id_endereco
    """,
    "usuarios": """
        SELECT
            id_usuario AS legacy_usuario_id,
            id_endereco AS legacy_endereco_id,
            id_tipo_usuario AS legacy_tipo_usuario_id,
            nome,
            cpf,
            email,
            senha_hash,
            status AS ativo,
            data_cadastro
        FROM usuario
        ORDER BY id_usuario
    """,
    "telefones": """
        SELECT
            id_telefone AS legacy_telefone_id,
            id_usuario AS legacy_usuario_id,
            numero
        FROM telefone
        ORDER BY id_telefone
    """,
    "sindicos": """
        SELECT
            id_sindico AS legacy_sindico_id,
            id_usuario AS legacy_usuario_id,
            id_condominio AS legacy_condominio_id
        FROM sindico
        ORDER BY id_sindico
    """,
    "condominios": """
        SELECT
            id_condominio AS legacy_condominio_id,
            id_endereco AS legacy_endereco_id,
            id_tipo_condominio AS legacy_tipo_condominio_id,
            nome,
            cnpj,
            status AS ativo,
            token
        FROM condominio
        ORDER BY id_condominio
    """,
    # O legado não tem tabela de torre: ela é um texto em morador. Cada torre
    # distinta do condomínio vira uma linha, identificada pelo primeiro morador.
    # ponytail: se esse morador for apagado, a torre ganha outro ID legado.
    "torres": """
        SELECT
            MIN(id_morador) AS legacy_torre_id,
            id_condominio AS legacy_condominio_id,
            (ARRAY_AGG(TRIM(torre) ORDER BY id_morador))[1] AS nome
        FROM morador
        WHERE NULLIF(TRIM(torre), '') IS NOT NULL
        GROUP BY id_condominio, LOWER(TRIM(torre))
        ORDER BY 1
    """,
    "moradores": """
        SELECT
            id_morador AS legacy_morador_id,
            id_usuario AS legacy_usuario_id,
            id_condominio AS legacy_condominio_id
        FROM morador
        ORDER BY id_morador
    """,
    # O e-mail da cooperativa vem do usuário dela.
    "cooperativas": """
        SELECT
            c.id_cooperativa AS legacy_cooperativa_id,
            c.id_usuario AS legacy_usuario_id,
            c.nome_cooperativa AS nome,
            c.cnpj,
            u.email
        FROM cooperativa c
        LEFT JOIN usuario u ON u.id_usuario = c.id_usuario
        ORDER BY c.id_cooperativa
    """,
}
