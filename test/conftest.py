"""
Os testes nunca usam os bancos do .env.

Sem TEST_LEGACY_URL / TEST_TARGET_URL, os testes de unidade rodam e o teste
de ponta a ponta é pulado.
"""

import os

_NENHUM = "postgresql://ninguem@127.0.0.1:1/nenhum"
os.environ["LEGACY_DATABASE_URL"] = os.environ.get("TEST_LEGACY_URL", _NENHUM)
os.environ["TARGET_DATABASE_URL"] = os.environ.get("TEST_TARGET_URL", _NENHUM)
