"""
Migração de ponta a ponta em dois bancos PostgreSQL descartáveis, com os
schemas oficiais do legado (sql/ecociente_legado_schema.sql) e do destino
(sql/ecociente_schema.sql).

    TEST_LEGACY_URL=postgresql://... TEST_TARGET_URL=postgresql://... pytest

ATENÇÃO: o teste APAGA tudo nos dois bancos indicados.
"""

import os
from pathlib import Path

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.skipif(
    "TEST_LEGACY_URL" not in os.environ or "TEST_TARGET_URL" not in os.environ,
    reason="defina TEST_LEGACY_URL e TEST_TARGET_URL",
)

RAIZ = Path(__file__).parent.parent

SEED = """
INSERT INTO tipo_usuario (nome_tipo) VALUES ('Morador'), ('Síndico'), ('Cooperativa');
INSERT INTO tipo_condominio (nome_tipo) VALUES ('Residencial');
INSERT INTO endereco (rua, numero, bairro, cidade, estado, cep) VALUES
    ('Rua das Flores', '10', 'Centro', 'SÃO PAULO', 'sp', '01310100'),
    ('Av. Brasil', '200', 'Centro', 'São Paulo', 'SP', '04000000'),
    ('Rua do Sol', '5', 'Cambuí', 'campinas', 'SP', '13000000'),
    ('Rua da Coleta', '77', 'Distrito', 'Osasco', 'SP', '06000000');
INSERT INTO usuario (id_endereco, id_tipo_usuario, nome, cpf, email, senha_hash, status, data_cadastro) VALUES
    (1, 2, 'ANA DA SILVA', '11122233344', 'ANA@EMAIL.COM', 'hash-ana', true, '2024-03-01'),
    (2, 1, 'Bruno Lima', NULL, 'bruno-sem-arroba', 'h', true, '2024-03-02'), -- e-mail inválido
    (3, 1, 'Carla Souza', '123.456.789', 'carla@email.com', 'h', true, '2024-03-03'), -- CPF com 9 dígitos
    (3, 2, 'Davi Rocha', NULL, 'davi@email.com', 'h', false, '2024-03-04'),
    (3, 1, 'Eva Dias', NULL, 'eva@email.com', 'h', true, '2024-03-05'),
    (4, 3, 'Recicla Osasco', NULL, 'contato@recicla.org', 'h', true, '2024-03-06');
INSERT INTO telefone (numero, id_usuario) VALUES
    ('11999990000', 1),
    ('11988880000', 2);                                       -- usuário rejeitado
INSERT INTO condominio (nome, cnpj, status, token, numero_unidades, id_endereco, id_tipo_condominio) VALUES
    ('Vila Verde', '12345678000190', true, 'ABC123', 40, 1, 1),
    ('Solar', '98765432000110', true, 'XYZ789', 10, 1, 1);    -- endereço repetido: o destino recusa
INSERT INTO sindico (id_usuario, id_condominio) VALUES (1, 1), (4, 2);
INSERT INTO morador (numero_apartamento, id_usuario, torre, id_condominio) VALUES
    ('12', 4, 'Torre A', 1),
    ('34', 5, ' torre a ', 1),                                -- mesma torre
    ('56', 1, 'Torre B', 2);                                  -- condomínio rejeitado
INSERT INTO cooperativa (nome_cooperativa, cnpj, id_usuario) VALUES
    ('Cooperativa Recicla Osasco', '11222333000144', 6);
INSERT INTO parceira (id_condominio, id_cooperativa) VALUES (1, 1);
"""

ESPERADO = {
    "tb_lkp_tipos_usuarios": 3,
    "tb_lkp_tipos_condominios": 1,
    "tb_enderecos": 4,
    "tb_usuarios": 4,
    "tb_telefones": 1,
    "tb_sindicos": 2,
    "tb_condominios": 1,
    "tb_torres": 1,
    "tb_moradores": 2,
    "tb_cooperativas": 1,
}


def _contagens(engine):
    with engine.connect() as c:
        return {
            t: c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in ESPERADO
        }


def _recriar_banco(engine, schema):
    # Conexão crua: o script tem BEGIN/COMMIT, funções em $$ e ':' que o
    # text() do SQLAlchemy tentaria ler como parâmetro.
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute((RAIZ / "sql" / schema).read_text(encoding="utf-8"))
        raw.commit()
    finally:
        raw.close()


def test_migracao_ponta_a_ponta():
    from config.database import legacy_engine, target_engine
    from rpa.orchestrator import MigrationOrchestrator

    _recriar_banco(legacy_engine, "ecociente_legado_schema.sql")
    with legacy_engine.begin() as c:
        c.execute(text(SEED))
    _recriar_banco(target_engine, "ecociente_schema.sql")
    with target_engine.begin() as c:  # tipo que o destino já tinha: é reaproveitado
        c.execute(
            text("INSERT INTO tb_lkp_tipos_usuarios (nome_tipo) VALUES ('morador')")
        )
    antes = _contagens(target_engine)

    # Simulação: tudo roda, nada é gravado.
    simulacao = MigrationOrchestrator(dry_run=True)
    assert simulacao.execute(), simulacao.log.snapshot()["erro"]
    assert _contagens(target_engine) == antes

    # Migração: inválidos e órfãos ficam de fora, o resto entra.
    migracao = MigrationOrchestrator()
    assert migracao.execute(), migracao.log.snapshot()["erro"]
    assert _contagens(target_engine) == ESPERADO
    relatorio = migracao.log.snapshot()
    assert all(t["status"] == "OK" for t in relatorio["tabelas"])
    motivos = {
        (r["entidade"], r["legacy_id"]): r["motivo"] for r in relatorio["rejeitados"]
    }
    assert motivos == {
        ("usuario", 2): "E-mail inválido",
        ("usuario", 3): "CPF deve ter 11 dígitos",
        ("telefone", 2): "O usuario 2 não foi migrado",
        ("condominio", 2): motivos[("condominio", 2)],
        ("torre", 3): "O condominio 2 não foi migrado",
        ("morador", 3): "O condominio 2 não foi migrado",
    }
    assert motivos[("condominio", 2)].startswith("Recusado pelo banco")

    with target_engine.connect() as c:
        ana = c.execute(
            text(
                "SELECT u.nome_usuario, u.email_usuario, u.cpf, u.senha_hash, u.ativo, "
                "t.nome_tipo, e.estado, e.bairro "
                "FROM tb_usuarios u "
                "JOIN tb_lkp_tipos_usuarios t ON t.id_tipo_usuario = u.tipo_usuario_id "
                "JOIN tb_enderecos e ON e.id_endereco = u.endereco_id "
                "WHERE u.email_usuario = 'ana@email.com'"
            )
        ).one()
        assert tuple(ana) == (
            "Ana da Silva",
            "ana@email.com",
            "11122233344",
            "hash-ana",
            True,
            "Síndico",
            "SP",
            "Centro",
        )
        condominio = c.execute(
            text(
                "SELECT c.codigo_acesso, c.cnpj, s.usuario_id = u.id_usuario, m.total "
                "FROM tb_condominios c "
                "JOIN tb_sindicos s ON s.id_sindico = c.sindico_id "
                "JOIN tb_usuarios u ON u.email_usuario = 'ana@email.com' "
                "CROSS JOIN (SELECT COUNT(*) AS total FROM tb_moradores) m"
            )
        ).one()
        assert tuple(condominio) == ("ABC123", "12345678000190", True, 2)
        torre = c.execute(text("SELECT nome_torre FROM tb_torres")).scalar_one()
        assert torre == "Torre A"
        cooperativa = c.execute(
            text(
                "SELECT nome_cooperativa, cnpj_cooperativa, usuario_id IS NOT NULL FROM tb_cooperativas"
            )
        ).one()
        assert tuple(cooperativa) == (
            "Cooperativa Recicla Osasco",
            "11222333000144",
            True,
        )

    with target_engine.connect() as c:
        mapa = c.execute(
            text("SELECT COUNT(*) FROM tb_migracao_ids_map WHERE entidade = 'usuarios'")
        ).scalar()
        assert mapa == ESPERADO["tb_usuarios"]

    # Idempotência: rodar de novo não duplica.
    repeticao = MigrationOrchestrator()
    assert repeticao.execute()
    assert _contagens(target_engine) == ESPERADO
    assert all(t["migrados"] == 0 for t in repeticao.log.snapshot()["tabelas"])

    # Linha migrada apagada do destino: a reconciliação recusa e nada é gravado.
    with target_engine.begin() as c:
        c.execute(text("DELETE FROM tb_torres"))
    quebrada = MigrationOrchestrator()
    assert not quebrada.execute()
    assert "reconciliação não fechou" in quebrada.log.snapshot()["erro"]
