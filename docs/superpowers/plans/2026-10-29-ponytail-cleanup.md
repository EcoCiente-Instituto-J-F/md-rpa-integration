# Limpeza ponytail — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remover o código morto e as abstrações de um uso só apontados pela auditoria ponytail de 2026-10-29, sem mudar o comportamento da migração.

**Architecture:** Duas tarefas. A primeira só apaga arquivos que nada importa, mais os testes quebrados. A segunda faz três refatorações pequenas (reconciliação, logger e mapper), protegidas por testes escritos antes.

**Tech Stack:** Python 3.14, SQLAlchemy 2, pydantic-settings, pytest (`pytest.ini` com `pythonpath = src`, `testpaths = test`).

**Spec:** não há documento separado. A especificação é a lista "Spec — achados da auditoria" logo abaixo, já filtrada: só o que está nela entra.

## Spec — achados da auditoria

Entram (verificados com grep: nenhum import em `src/`, `test/`, `.bat`, `Dockerfile`):

1. Apagar os módulos sem importador: `src/extract/legacy_connector.py`, `src/extract/extractor.py`, `src/audit/error_report.py`, `src/load/transaction_manager.py`, `src/load/loader.py`, `src/load/primary_keys.py`, `src/rpa/scheduler.py`, `src/rpa/retry_handler.py`, `src/transform/transformer.py`, `src/transform/table_mapping.py`, `src/transform/id_mapper.py`.
2. Apagar os pacotes inteiros sem uso: `src/connections/`, `src/mapping/`, `src/utils/`, `src/models/`, `src/reporting/`, `src/validation/`, `config/` (só tem `migration_order.py`).
3. Apagar os testes obsoletos: `test/test_extract.py` e `test/test_load.py` (falham com AttributeError contra a API atual), `test/test_integrity.py` (só confere um dict escrito à mão) e `test/schema_teste.sql` (nada o referencia).
4. Tirar `pydantic==2.13.5` do `requirements.txt`: não é importado direto e já vem com `pydantic-settings`.
5. Trocar a classe `Reconciliation` (um método, um chamador) por uma função `reconcile`.
6. Trocar `get_logger()`, que só chama `_build_logger()`, pelo próprio construtor com o nome `get_logger`.
7. Trocar `map_tipo_usuario` e `map_tipo_condominio`, que só delegam, por `functools.partialmethod`.
8. Tirar o parâmetro `engine` de `ExtractService.__init__`: só o `test_extract.py` (item 3) o usava.

Ficam de fora (Ruling do controlador, registrado no ledger):
- `tenacity`: um laço `for` com `sleep` não é mais simples que o `Retrying(...)` atual, que está certo.
- `black`: é dependência de desenvolvimento e pode estar em uso manual.
- `LOG_PATH`: tirá-lo só muda a linha de lugar.
- `main()` inline: ganha 4 linhas e perde a função testável.
- `enriquecido` em `transform_dataset`: o ganho não compensa a perda de legibilidade.
- `todo.md`: é rascunho histórico, não é atualizado.

## Global Constraints

- Nenhuma dependência nova. Nenhuma alteração em `sql/`, `.env`, `.env.example`, `todo.md`, `src/ui_static/` ou `scripts/`.
- Comentários e docstrings em português, no mesmo tom curto dos arquivos vizinhos.
- Comando de teste: `.venv/Scripts/python.exe -m pytest -q`, a partir da raiz do repositório.
- NUNCA rode `test/test_e2e.py` com `TEST_LEGACY_URL`/`TEST_TARGET_URL` definidas: o teste APAGA os dois bancos. Sem essas variáveis ele é pulado, e esse é o resultado esperado.
- Não abra nem imprima o `.env` (tem credenciais).
- Commits no padrão do repositório (`chore: ...`), terminando com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. Executável PyInstaller (`build_exe.bat`, entrada `src\ui.py`, `--paths src`): apagar pacotes não pode quebrar a cadeia de imports da interface. O smoke de imports da Task 1 cobre isso.
2. `get_logger()` chamado por todos os módulos ao importar: o guarda `if logger.handlers` precisa continuar, senão cada import duplica as linhas de log. Coberto por `test_get_logger_nao_duplica_handlers` (Task 2).
3. `transform_dataset` chama os mappers por `getattr(self, f"map_{e.nome}")`: o `partialmethod` tem de funcionar por esse caminho, e não só na chamada direta. Coberto por `test_tipos_passam_pelo_transform_dataset` (Task 2).
4. A orquestração tem de continuar chamando a reconciliação dentro da mesma sessão da carga. Coberto pelo smoke da Task 2 e pela simulação final que o controlador roda.

---

### Task 1: Apagar código morto e testes obsoletos

**Files:**
- Delete: todos os arquivos e pastas dos itens 1, 2 e 3 da Spec
- Modify: `requirements.txt` (remover a linha `pydantic==2.13.5`)

**Interfaces:**
- Consumes: nada.
- Produces: árvore `src/` com apenas `__init__.py`, `entidades.py`, `main.py`, `ui.py`, `ui_static/`, `audit/{__init__,migration_log,reconciliation}.py`, `config/`, `extract/{__init__,extract_service,legacy_queries}.py`, `load/{__init__,insert_service}.py`, `rpa/{__init__,orchestrator}.py`, `transform/{__init__,data_mapper,normalization,validators}.py`. (`src/config/` é outro pacote e fica. Quem sai é o `config/` da raiz.)

- [ ] **Step 1: Registrar a linha de base**

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: `2 failed, 11 passed, 1 skipped` (as falhas são `test_extract_table` e `test_insert_usuario`)

- [ ] **Step 2: Confirmar que nada importa o que vai sair**

Run: `grep -rnE "legacy_connector|extractor|error_report|transaction_manager|load\.loader|primary_keys|scheduler|retry_handler|transformer|table_mapping|id_mapper|connections|from utils|import utils|migration_order|schema_teste" src test README.md Dockerfile build_exe.bat EcoCiente.bat`
Expected: só ocorrências dentro dos próprios arquivos que vão ser apagados. Qualquer outra ocorrência: pare e reporte como BLOCKED.

- [ ] **Step 3: Apagar com `git rm -r`** os caminhos dos itens 1, 2 e 3 da Spec, e tirar `pydantic==2.13.5` do `requirements.txt`. Pastas não rastreadas que sobrarem vazias (`__pycache__`) podem ser removidas do disco.

- [ ] **Step 4: Smoke de imports da interface e da CLI**

Run: `cd src && ../.venv/Scripts/python.exe -c "import ui, main, rpa.orchestrator; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Rodar os testes**

Run: `.venv/Scripts/python.exe -m pytest -q`
Expected: `10 passed, 1 skipped`, sem falhas.

- [ ] **Step 6: Commit**

```bash
git add -A src test config requirements.txt
git commit -m "chore: remove dead modules and stale tests"
```

### Task 2: Reconciliação como função, logger sem wrapper, mapper com partialmethod

**Files:**
- Modify: `src/audit/reconciliation.py`, `src/rpa/orchestrator.py`, `src/config/logging_config.py`, `src/transform/data_mapper.py`, `src/extract/extract_service.py`
- Test: `test/test_mapper.py`, `test/test_logging.py` (novo)

**Interfaces:**
- Consumes: a árvore deixada pela Task 1.
- Produces:
  - `audit.reconciliation.reconcile(session, id_mapping, stats, rejected) -> list[dict]`: mesmo corpo e mesmo retorno do antigo `Reconciliation.run`. Usa `legacy_engine`, importado de `config.database`.
  - `config.logging_config.get_logger() -> logging.Logger`: o antigo `_build_logger`, renomeado e com o guarda `if logger.handlers: return logger` mantido.
  - `DataMapper.map_tipo_usuario` e `DataMapper.map_tipo_condominio` como `functools.partialmethod(map_tipo, entidade="tipo_usuario" | "tipo_condominio")`.
  - `ExtractService()` sem parâmetros. `extract_all()` usa `legacy_engine` direto.

- [ ] **Step 1: Escrever os testes que fixam o comportamento atual**

Em `test/test_mapper.py`:

```python
def test_tipos_passam_pelo_transform_dataset():
    out = DataMapper().transform_dataset(
        {
            "tipos_usuarios": [{"legacy_tipo_usuario_id": 3, "nome_tipo": "Morador"}],
            "tipos_condominios": [{"legacy_tipo_condominio_id": 1, "nome_tipo": "Residencial"}],
        }
    )
    assert out["tipos_usuarios"] == [
        {"nome_tipo": "Morador", "descricao": None, "legacy_tipo_usuario_id": 3}
    ]
    assert out["tipos_condominios"] == [
        {"nome_tipo": "Residencial", "descricao": None, "legacy_tipo_condominio_id": 1}
    ]
```

Em `test/test_logging.py` (novo):

```python
from config.logging_config import get_logger


def test_get_logger_nao_duplica_handlers():
    primeiro = get_logger()
    handlers = len(primeiro.handlers)
    assert get_logger() is primeiro
    assert len(primeiro.handlers) == handlers
```

- [ ] **Step 2: Rodar os testes novos contra o código atual**

Run: `.venv/Scripts/python.exe -m pytest -q test/test_mapper.py test/test_logging.py`
Expected: PASS. É uma refatoração: os testes fixam o comportamento antes da mudança. Se algum falhar agora, o teste está errado. Corrija o teste, não o código.

- [ ] **Step 3: Refatorar**

- `reconciliation.py`: troque a classe pela função `reconcile` descrita em Interfaces e mantenha a docstring do módulo.
- `orchestrator.py`: tire `self.reconciliation`, chame `reconcile(session, ...)` dentro de `load` e remova o `legacy_engine` do import de `config.database` se ele ficar sem uso.
- `logging_config.py`: aplique o rename descrito em Interfaces.
- `data_mapper.py`: aplique os `partialmethod` descritos em Interfaces, com `import functools` ou `from functools import partialmethod`, no estilo de import do arquivo.
- `extract_service.py`: tire o parâmetro `engine`.

- [ ] **Step 4: Rodar os testes e o smoke**

Run: `.venv/Scripts/python.exe -m pytest -q` e `cd src && ../.venv/Scripts/python.exe -c "import ui, main; from audit.reconciliation import reconcile; print('ok')"`
Expected: `12 passed, 1 skipped` e `ok`

- [ ] **Step 5: Commit**

```bash
git add src test
git commit -m "chore: simplify reconciliation, logger and type mappers"
```
