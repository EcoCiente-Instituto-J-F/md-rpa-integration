"""Consultas de extração do banco legado, por dataset."""

QUERIES = {
    "enderecos": """
        SELECT
            e.id_endereco AS legacy_endereco_id,
            e.rua AS logradouro,
            e.numero AS numero,
            e.bairro AS bairro,
            e.cidade AS cidade,
            e.estado AS estado,
            e.cep AS cep,
            e.complemento AS complemento
        FROM endereco e
        ORDER BY e.id_endereco
    """,
    "usuarios": """
        SELECT
            u.id_usuario AS legacy_usuario_id,
            u.id_endereco AS legacy_endereco_id,
            u.id_tipo_usuario AS tipo_usuario_id,
            u.nome AS nome,
            u.email AS email,
            NULL AS cpf,
            u.status AS ativo,
            u.data_cadastro AS data_cadastro
        FROM usuario u
        ORDER BY u.id_usuario
    """,
    "sindicos": """
        SELECT
            s.id_sindico AS legacy_sindico_id,
            s.cpf AS cpf,
            s.data_inicio_mandato AS data_inicio_mandato,
            s.data_fim_mandato AS data_fim_mandato,
            s.id_usuario AS legacy_usuario_id,
            s.id_condominio AS legacy_condominio_id
        FROM sindico s
        ORDER BY s.id_sindico
    """,
    "condominios": """
        SELECT
            c.id_condominio AS legacy_condominio_id,
            c.nome AS nome,
            c.cnpj AS cnpj,
            c.id_endereco AS legacy_endereco_id
        FROM condominio c
        ORDER BY c.id_condominio
    """,
}
