"""
Carga no banco destino, dentro da transação aberta pelo orquestrador.

A tabela de controle `migracao_id_map` guarda legado -> novo ID de tudo que já
foi migrado. É ela que torna a carga idempotente: registro já mapeado não é
inserido de novo.
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from config.logging_config import get_logger
from entidades import ENTIDADES
from transform.validators import rejection

logger = get_logger()

CONTROLE_DDL = """
    CREATE TABLE IF NOT EXISTS tb_migracao_ids_map (
        entidade   text        NOT NULL,
        legacy_id  bigint      NOT NULtL,
        novo_id    bigint      NOT NULL,
        migrado_em timestamptz NOT NULL DEFAULT now(),
        PRIMARY KEY (entidade, legacy_id)
    )
"""


class InsertService:
    def __init__(self, data_mapper):
        self.data_mapper = data_mapper
        self.rejected = []
        self.stats = {}

    def _load_id_mapping(self, session):
        session.execute(text(CONTROLE_DDL))
        mapping = self.data_mapper.id_mapping
        for ids in mapping.values():
            ids.clear()
        rows = session.execute(
            text("SELECT entidade, legacy_id, novo_id FROM migracao_id_map")
        )
        for entidade, legacy_id, novo_id in rows:
            mapping.setdefault(entidade, {})[legacy_id] = novo_id

    def _resolve_fks(self, entidade, record):
        """Preenche as FKs com os novos IDs. Rejeita o registro se o pai não migrou."""
        for coluna, pai, obrigatoria in entidade.fks:
            campo = f"legacy_{pai}_id"
            legacy_pai = record.get(campo)
            novo_id = self.data_mapper.get_new_id(pai, legacy_pai)
            if novo_id is None and (obrigatoria or legacy_pai is not None):
                motivo = (
                    f"Sem {pai} no legado"
                    if legacy_pai is None
                    else f"O {pai} {legacy_pai} não foi migrado"
                )
                self.rejected.append(rejection(entidade.nome, record, campo, motivo))
                return False
            record[coluna] = novo_id
        return True

    def insert(self, entidade, record, session):
        data = {k: v for k, v in record.items() if not k.startswith("legacy_")}
        columns = ", ".join(data)
        values = ", ".join(f":{column}" for column in data)
        query = (
            f"INSERT INTO {entidade.tabela_destino} ({columns}) "
            f"VALUES ({values}) RETURNING {entidade.pk_destino}"
        )
        return session.execute(text(query), data).scalar()

    def load_dataset(self, dataset, session):
        self.rejected = []
        self.stats = {}
        self._load_id_mapping(session)

        for entidade in ENTIDADES:
            migrados = ja_migrados = 0
            for record in dataset.get(entidade.dataset, []):
                legacy_id = record[f"legacy_{entidade.nome}_id"]
                if legacy_id in self.data_mapper.id_mapping[entidade.nome]:
                    ja_migrados += 1
                    continue
                if not self._resolve_fks(entidade, record):
                    continue
                try:
                    # SAVEPOINT: uma linha recusada pelo banco não aborta a transação.
                    with session.begin_nested():
                        new_id = self.insert(entidade, record, session)
                        session.execute(
                            text(
                                "INSERT INTO migracao_id_map "
                                "(entidade, legacy_id, novo_id) "
                                "VALUES (:entidade, :legacy_id, :novo_id)"
                            ),
                            {
                                "entidade": entidade.nome,
                                "legacy_id": legacy_id,
                                "novo_id": new_id,
                            },
                        )
                except IntegrityError as error:
                    motivo = str(error.orig).strip().splitlines()[0]
                    self.rejected.append(
                        rejection(
                            entidade.nome,
                            record,
                            None,
                            f"Recusado pelo banco: {motivo}",
                        )
                    )
                    continue
                self.data_mapper.save_mapping(entidade.nome, legacy_id, new_id)
                migrados += 1

            self.stats[entidade.nome] = {
                "migrados": migrados,
                "ja_migrados": ja_migrados,
            }
            logger.info(
                f"{entidade.tabela_destino}: {migrados} migrados, "
                f"{ja_migrados} já migrados"
            )
