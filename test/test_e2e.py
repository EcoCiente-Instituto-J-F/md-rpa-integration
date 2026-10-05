"""
Migração de ponta a ponta em dois bancos PostgreSQL descartáveis.

    TEST_LEGACY_URL=postgresql://... TEST_TARGET_URL=postgresql://... pytest

ATENÇÃO: o teste APAGA e recria as tabelas nos dois bancos indicados.
"""

import os
from pathlib import Path

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.skipif(
    "TEST_LEGACY_URL" not in os.environ or "TEST_TARGET_URL" not in os.environ,
    reason="defina TEST_LEGACY_URL e TEST_TARGET_URL",
)

SEED = """
INSERT INTO endereco (rua, numero, cidade, estado, cep) VALUES
    ('Rua das Flores', '10', 'SÃO PAULO', 'SP', '01310-100'),
    ('Av. Brasil', '200', NULL, 'SP', '04000-000'),          -- sem cidade
    ('Rua do Sol', '5', 'campinas', 'SP', '13000-000');
INSERT INTO usuario (id_endereco, id_tipo_usuario, nome, email, status, data_cadastro) VALUES
    (1, 1, 'ANA DA SILVA', 'ANA@EMAIL.COM', 'Ativo', now()),
    (2, 1, 'Bruno Lima', 'bruno@email.com', 'ativo', now()), -- endereço rejeitado
    (3, 2, 'Carla Souza', 'carla-sem-arroba', 'ativo', now()), -- e-mail inválido
    (3, 2, 'Davi Rocha', 'ana@email.com', 'inativo', now()), -- e-mail duplicado
    (3, 2, 'Eva Dias', 'eva@email.com', NULL, NULL);
INSERT INTO condominio (nome, cnpj, id_endereco) VALUES
    ('Vila Verde', '12.345.678/0001-90', 1);
INSERT INTO sindico (cpf, id_usuario, id_condominio) VALUES
    ('111.222.333-44', 1, 1),
    ('555.666.777-88', 2, NULL);                             -- usuário rejeitado
"""


def _contagens(engine):
    with engine.connect() as c:
        return {
            t: c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            for t in ("tb_enderecos", "tb_usuarios", "tb_sindicos", "tb_condominios")
        }


def test_migracao_ponta_a_ponta():
    from config.database import legacy_engine, target_engine
    from rpa.orchestrator import MigrationOrchestrator

    schema = (Path(__file__).parent / "schema_teste.sql").read_text(encoding="utf-8")
    legado, destino = schema.split("-- destino")
    with legacy_engine.begin() as c:
        c.execute(text(legado))
        c.execute(text(SEED))
    with target_engine.begin() as c:
        c.execute(text(destino))

    vazio = {"tb_enderecos": 0, "tb_usuarios": 0, "tb_sindicos": 0, "tb_condominios": 0}
    esperado = {
        "tb_enderecos": 2,
        "tb_usuarios": 2,
        "tb_sindicos": 1,
        "tb_condominios": 1,
    }

    # Simulação: tudo roda, nada é gravado.
    simulacao = MigrationOrchestrator(dry_run=True)
    assert simulacao.execute()
    assert _contagens(target_engine) == vazio

    # Migração: inválidos e órfãos ficam de fora, o resto entra.
    migracao = MigrationOrchestrator()
    assert migracao.execute()
    assert _contagens(target_engine) == esperado
    relatorio = migracao.log.snapshot()
    assert all(t["status"] == "OK" for t in relatorio["tabelas"])
    motivos = {
        (r["entidade"], r["legacy_id"]): r["motivo"] for r in relatorio["rejeitados"]
    }
    assert motivos[("endereco", 2)] == "Campo obrigatório vazio"
    assert motivos[("usuario", 2)] == "O endereco 2 não foi migrado"
    assert motivos[("usuario", 3)] == "E-mail inválido"
    assert motivos[("usuario", 4)].startswith("Recusado pelo banco")
    assert motivos[("sindico", 2)] == "O usuario 2 não foi migrado"

    with target_engine.connect() as c:
        ana = c.execute(
            text(
                "SELECT nome_usuario, email_usuario, ativo FROM tb_usuarios ORDER BY 1 LIMIT 1"
            )
        ).one()
        assert tuple(ana) == ("Ana da Silva", "ana@email.com", True)
        assert c.execute(
            text(
                "SELECT sindico_id IS NOT NULL AND endereco_id IS NOT NULL FROM tb_condominios"
            )
        ).scalar()

    # Idempotência: rodar de novo não duplica.
    repeticao = MigrationOrchestrator()
    assert repeticao.execute()
    assert _contagens(target_engine) == esperado
    assert all(t["migrados"] == 0 for t in repeticao.log.snapshot()["tabelas"])

    # Linha migrada apagada do destino: a reconciliação recusa e nada é gravado.
    with target_engine.begin() as c:
        c.execute(text("DELETE FROM tb_condominios"))
    quebrada = MigrationOrchestrator()
    assert not quebrada.execute()
    assert "reconciliação não fechou" in quebrada.log.snapshot()["erro"]
