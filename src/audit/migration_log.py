"""
Auditoria da execução: etapas, contagens por tabela, rejeitados e status final.

A interface lê `snapshot()` enquanto a migração roda em outra thread, por isso
toda escrita passa pelo lock.
"""

import copy
import threading
from contextlib import contextmanager
from datetime import datetime

from config.logging_config import get_logger

logger = get_logger()

ETAPAS = (
    ("bancos", "Verificação dos bancos"),
    ("extracao", "Extração"),
    ("normalizacao", "Normalização"),
    ("transformacao", "Transformação"),
    ("validacao", "Validação"),
    ("carga", "Carga"),
    ("reconciliacao", "Reconciliação"),
)


class MigrationLog:
    def __init__(self, simulacao=False):
        self._lock = threading.Lock()
        self._report = {
            "status": "RUNNING",
            "simulacao": simulacao,
            "inicio": datetime.now().isoformat(timespec="seconds"),
            "fim": None,
            "erro": None,
            "etapas": [
                {"id": id_, "nome": nome, "status": "pendente"} for id_, nome in ETAPAS
            ],
            "tabelas": [],
            "rejeitados": [],
        }

    def update(self, **fields):
        with self._lock:
            self._report.update(fields)

    def _set_etapa(self, etapa_id, status):
        with self._lock:
            for etapa in self._report["etapas"]:
                if etapa["id"] == etapa_id:
                    etapa["status"] = status

    @contextmanager
    def etapa(self, etapa_id):
        nome = dict(ETAPAS)[etapa_id]
        logger.info(f"Etapa: {nome}")
        self._set_etapa(etapa_id, "rodando")
        try:
            yield
        except Exception:
            self._set_etapa(etapa_id, "falhou")
            raise
        self._set_etapa(etapa_id, "ok")

    def finish(self, erro=None):
        self.update(
            status="FAILED" if erro else "SUCCESS",
            erro=erro,
            fim=datetime.now().isoformat(timespec="seconds"),
        )
        logger.info(f"Auditoria finalizada: {self._report['status']}")

    def snapshot(self):
        with self._lock:
            return copy.deepcopy(self._report)
