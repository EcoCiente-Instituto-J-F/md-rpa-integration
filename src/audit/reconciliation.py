"""
Reconciliação: confere legado x destino antes do COMMIT.

Para cada entidade a conta tem de fechar:
    registros no legado = migrados + já migrados + rejeitados
e todo ID mapeado tem de existir no destino.
"""

from sqlalchemy import text

from config.logging_config import get_logger
from entidades import ENTIDADES

logger = get_logger()


class Reconciliation:
    def __init__(self, legacy_engine):
        self.legacy_engine = legacy_engine

    def run(self, session, id_mapping, stats, rejected):
        results = []
        with self.legacy_engine.connect() as legacy:
            for entidade in ENTIDADES:
                legado = legacy.execute(
                    text(f"SELECT COUNT(*) FROM {entidade.tabela_legado}")
                ).scalar()
                new_ids = list(id_mapping[entidade.nome].values())
                no_destino = session.execute(
                    text(
                        f"SELECT COUNT(*) FROM {entidade.tabela_destino} "
                        f"WHERE {entidade.pk_destino} = ANY(:ids)"
                    ),
                    {"ids": new_ids},
                ).scalar()
                rejeitados = len(
                    {r["legacy_id"] for r in rejected if r["entidade"] == entidade.nome}
                )
                fechou = legado == len(new_ids) + rejeitados and no_destino == len(
                    new_ids
                )
                results.append(
                    {
                        "entidade": entidade.nome,
                        "tabela_legado": entidade.tabela_legado,
                        "tabela_destino": entidade.tabela_destino,
                        "legado": legado,
                        **stats[entidade.nome],
                        "rejeitados": rejeitados,
                        "no_destino": no_destino,
                        "status": "OK" if fechou else "DIVERGENCIA",
                    }
                )
                log = logger.info if fechou else logger.error
                log(
                    f"Reconciliação {entidade.tabela_legado} -> "
                    f"{entidade.tabela_destino}: {results[-1]['status']}"
                )
        return results
