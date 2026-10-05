"""
Carga no banco destino, dentro da transação aberta pelo orquestrador.

A tabela `tb_migracao_ids_map` (criada pelo schema do destino) guarda
legado -> novo ID de tudo que já foi migrado. É ela que torna a carga
idempotente: registro já mapeado não é inserido de novo. A coluna `entidade`
recebe o nome no plural (usuarios, condominios...), como o schema documenta.
"""

from sqlalchemy import text
from sqlalchemy.exc import DataError, IntegrityError

from config.logging_config import get_logger
from entidades import ENTIDADES
from transform.validators import rejection

logger = get_logger()

_NOME_POR_DATASET = {e.dataset: e.nome for e in ENTIDADES}


class InsertService:
    def __init__(self, data_mapper):
        self.data_mapper = data_mapper
        self.rejected = []
        self.stats = {}

    def _load_id_mapping(self, session):
        mapping = self.data_mapper.id_mapping
        for ids in mapping.values():
            ids.clear()
        rows = session.execute(
            text("SELECT entidade, legacy_id, novo_id FROM tb_migracao_ids_map")
        )
        for dataset, legacy_id, novo_id in rows:
            if dataset in _NOME_POR_DATASET:
                mapping[_NOME_POR_DATASET[dataset]][legacy_id] = novo_id

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

    def _existing_id(self, entidade, record, session):
        """Tabela de domínio: reaproveita a linha do destino com o mesmo nome."""
        if not entidade.chave_natural:
            return None
        return session.execute(
            text(
                f"SELECT {entidade.pk_destino} FROM {entidade.tabela_destino} "
                f"WHERE lower({entidade.chave_natural}) = lower(:valor) "
                f"ORDER BY {entidade.pk_destino} LIMIT 1"
            ),
            {"valor": record[entidade.chave_natural]},
        ).scalar()

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
                        new_id = self._existing_id(entidade, record, session)
                        existia = new_id is not None
                        if not existia:
                            new_id = self.insert(entidade, record, session)
                        session.execute(
                            text(
                                "INSERT INTO tb_migracao_ids_map "
                                "(entidade, legacy_id, novo_id) "
                                "VALUES (:entidade, :legacy_id, :novo_id)"
                            ),
                            {
                                "entidade": entidade.dataset,
                                "legacy_id": legacy_id,
                                "novo_id": new_id,
                            },
                        )
                except (IntegrityError, DataError) as error:
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
                ja_migrados += existia
                migrados += not existia

            self.stats[entidade.nome] = {
                "migrados": migrados,
                "ja_migrados": ja_migrados,
            }
            logger.info(
                f"{entidade.tabela_destino}: {migrados} migrados, "
                f"{ja_migrados} já migrados"
            )
