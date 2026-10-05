"""
Migração de ponta a ponta em dois bancos PostgreSQL descartáveis, com o
schema oficial do destino (sql/ecociente_schema.sql).

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
    ('Rua das Flores', 10, 'Centro', 'SÃO PAULO', 'sp', '01310-100'),
    ('Av. Brasil', 200, 'Centro', 'São Paulo', 'São Paulo', '04000-000'), -- estado não cabe em CHAR(2)
    ('Rua do Sol', 5, 'Cambuí', 'campinas', 'SP', '13000-000'),
    ('Rua da Coleta', 77, 'Distrito', 'Osasco', 'SP', '06000-000');
INSERT INTO usuario (id_endereco, id_tipo_usuario, nome, email, senha_hash, status, data_cadastro) VALUES
    (1, 2, 'ANA DA SILVA', 'ANA@EMAIL.COM', 123, true, '2024-03-01'),
    (2, 1, 'Bruno Lima', 'bruno@email.com', 123, true, '2024-03-02'),  -- endereço rejeitado
    (3, 1, 'Carla Souza', 'carla-sem-arroba', 123, true, '2024-03-03'), -- e-mail inválido
    (3, 1, 'Davi Rocha', 'davi@email.com', 123, false, '2024-03-04'),
    (3, 1, 'Eva Dias', 'eva@email.com', 123, NULL, NULL),
    (4, 3, 'Recicla Osasco', 'contato@recicla.org', 123, true, '2024-03-05');
INSERT INTO telefone_usuario (numero, id_usuario) VALUES
    ('(11) 99999-0000', 1),
    ('(11) 98888-0000', 2);                                   -- usuário rejeitado
INSERT INTO condominio (nome, cnpj, status, token, id_endereco, id_tipo_condominio) VALUES
    ('Vila Verde', '12.345.678/0001-90', true, 'ABC123', 1, 1);
INSERT INTO sindico (cpf, id_usuario, id_condominio) VALUES
    ('111.222.333-44', 1, 1),
    ('555.666.777-88', 2, NULL);                              -- usuário rejeitado
INSERT INTO torre (nome, numero_unidades, id_condominio) VALUES ('Torre A', 40, 1);
INSERT INTO morador (numero_apartamento, id_usuario, id_torre) VALUES
    ('12', 4, 1),
    ('34', 5, NULL);                                          -- sem torre, sem condomínio
INSERT INTO cooperativa (cnpj, id_usuario) VALUES ('11.222.333/0001-44', 6);
"""

ESPERADO = {
    "tb_lkp_tipos_usuarios": 3,
    "tb_lkp_tipos_condominios": 1,
    "tb_enderecos": 3,
    "tb_usuarios": 4,
    "tb_telefones": 1,
    "tb_sindicos": 1,
    "tb_condominios": 1,
    "tb_torres": 1,
    "tb_moradores": 1,
    "tb_cooperativas": 1,
}


def _contagens(engine):
    with engine.connect() as c:
        return {
            t: c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in ESPERADO
        }


def _aplicar_schema_oficial(engine):
    # Conexão crua: o script tem BEGIN/COMMIT, funções em $$ e ':' que o
    # text() do SQLAlchemy tentaria ler como parâmetro.
    raw = engine.raw_connection()
    try:
        raw.autocommit = True
        with raw.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            cursor.execute(
                (RAIZ / "sql" / "ecociente_schema.sql").read_text(encoding="utf-8")
            )
    finally:
        raw.close()


def test_migracao_ponta_a_ponta():
    from config.database import legacy_engine, target_engine
    from rpa.orchestrator import MigrationOrchestrator

    legado = (RAIZ / "test" / "schema_legado_teste.sql").read_text(encoding="utf-8")
    with legacy_engine.begin() as c:
        c.execute(text(legado))
        c.execute(text(SEED))
    _aplicar_schema_oficial(target_engine)
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
    assert set(motivos) == {
        ("endereco", 2),
        ("usuario", 2),
        ("usuario", 3),
        ("telefone", 2),
        ("sindico", 2),
        ("morador", 2),
    }
    assert motivos[("endereco", 2)].startswith("Recusado pelo banco")
    assert motivos[("usuario", 2)] == "O endereco 2 não foi migrado"
    assert motivos[("usuario", 3)] == "E-mail inválido"
    assert motivos[("morador", 2)] == "Sem condominio no legado"

    with target_engine.connect() as c:
        ana = c.execute(
            text(
                "SELECT u.nome_usuario, u.email_usuario, u.cpf, u.ativo, t.nome_tipo, e.estado, e.bairro "
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
        assert tuple(condominio) == ("ABC123", "12345678000190", True, 1)
        cooperativa = c.execute(
            text(
                "SELECT nome_cooperativa, cnpj_cooperativa, usuario_id IS NOT NULL FROM tb_cooperativas"
            )
        ).one()
        assert tuple(cooperativa) == ("Recicla Osasco", "11222333000144", True)

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
