"""Consultas de extração do banco legado, por dataset (ver docs/banco-legado-er.png)."""

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
            email,
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
        FROM telefone_usuario
        ORDER BY id_telefone
    """,
    "sindicos": """
        SELECT
            id_sindico AS legacy_sindico_id,
            id_usuario AS legacy_usuario_id,
            id_condominio AS legacy_condominio_id,
            cpf
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
    "torres": """
        SELECT
            id_torre AS legacy_torre_id,
            id_condominio AS legacy_condominio_id,
            nome
        FROM torre
        ORDER BY id_torre
    """,
    # No destino o morador aponta para o condomínio; no legado, para a torre.
    "moradores": """
        SELECT
            m.id_morador AS legacy_morador_id,
            m.id_usuario AS legacy_usuario_id,
            t.id_condominio AS legacy_condominio_id
        FROM morador m
        LEFT JOIN torre t ON t.id_torre = m.id_torre
        ORDER BY m.id_morador
    """,
    # A cooperativa do legado não tem nome nem e-mail próprios: vêm do usuário dela.
    "cooperativas": """
        SELECT
            c.id_cooperativa AS legacy_cooperativa_id,
            c.id_usuario AS legacy_usuario_id,
            c.cnpj,
            u.nome,
            u.email
        FROM cooperativa c
        LEFT JOIN usuario u ON u.id_usuario = c.id_usuario
        ORDER BY c.id_cooperativa
    """,
}
