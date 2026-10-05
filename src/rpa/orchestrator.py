"""
Orquestrador da migração.

Fluxo: verificação dos bancos -> extração -> normalização -> transformação ->
validação -> carga -> reconciliação -> COMMIT.

A carga e a reconciliação rodam na mesma transação: se a conta não fechar,
nada é gravado. Em simulação (`dry_run`) a transação é sempre desfeita.
"""

from sqlalchemy.exc import OperationalError
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_fixed

from audit.migration_log import MigrationLog
from audit.reconciliation import Reconciliation
from config.database import TargetSession, database_health_check, legacy_engine
from config.logging_config import get_logger
from config.settings import settings
from entidades import ENTIDADES
from extract.extract_service import ExtractService
from load.insert_service import InsertService
from transform.data_mapper import DataMapper
from transform.normalization import DataNormalizer
from transform.validators import DataValidator

logger = get_logger()


class MigrationOrchestrator:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.log = MigrationLog(simulacao=dry_run)
        self.extract_service = ExtractService()
        self.normalizer = DataNormalizer()
        self.mapper = DataMapper()
        self.validator = DataValidator()
        self.insert_service = InsertService(self.mapper)
        self.reconciliation = Reconciliation(legacy_engine)

    def check_databases(self):
        for nome, banco in database_health_check().items():
            if banco["erro"]:
                raise ConnectionError(
                    f"Sem conexão com o banco {nome} ({banco['alvo']}): "
                    f"{banco['erro']}. Confira o .env e se o PostgreSQL está no ar."
                )

    def load(self, data):
        """Carga + reconciliação em uma transação. Só grava se a conta fechar."""
        with TargetSession() as session:  # sair sem commit desfaz tudo
            with self.log.etapa("carga"):
                self.insert_service.load_dataset(data, session)

            with self.log.etapa("reconciliacao"):
                rejeitados = self.validator.errors + self.insert_service.rejected
                tabelas = self.reconciliation.run(
                    session,
                    self.mapper.id_mapping,
                    self.insert_service.stats,
                    rejeitados,
                )
                self.log.update(tabelas=tabelas, rejeitados=rejeitados)
                divergentes = [
                    t["tabela_destino"] for t in tabelas if t["status"] != "OK"
                ]
                if divergentes:
                    raise RuntimeError(
                        f"A reconciliação não fechou em {', '.join(divergentes)}. "
                        "Nada foi gravado. Se linhas migradas foram apagadas do "
                        "destino, apague também as linhas correspondentes de "
                        "migracao_id_map."
                    )

            if self.dry_run:
                session.rollback()
                logger.info("Simulação: transação desfeita, nada foi gravado")
            else:
                session.commit()
                logger.info("Transação confirmada (COMMIT)")

    def execute(self):
        logger.info("Iniciando " + ("simulação" if self.dry_run else "migração"))
        try:
            with self.log.etapa("bancos"):
                self.check_databases()

            with self.log.etapa("extracao"):
                data = self.extract_service.extract_all()
                self.log.update(
                    tabelas=[
                        {
                            "entidade": e.nome,
                            "tabela_legado": e.tabela_legado,
                            "tabela_destino": e.tabela_destino,
                            "legado": len(data[e.dataset]),
                        }
                        for e in ENTIDADES
                    ]
                )

            with self.log.etapa("normalizacao"):
                data = self.normalizer.normalize_dataset(data)

            with self.log.etapa("transformacao"):
                data = self.mapper.transform_dataset(data)

            with self.log.etapa("validacao"):
                data = self.validator.validate_dataset(data)
                self.log.update(rejeitados=list(self.validator.errors))

            # Só queda de conexão vale nova tentativa; erro de dados se repete igual.
            Retrying(
                retry=retry_if_exception_type(OperationalError),
                stop=stop_after_attempt(settings.MAX_RETRIES),
                wait=wait_fixed(5),
                reraise=True,
            )(self.load, data)

            self.log.finish()
            return True

        except Exception as error:
            logger.exception(f"Migração falhou: {error}")
            self.log.finish(erro=str(error))
            return False
