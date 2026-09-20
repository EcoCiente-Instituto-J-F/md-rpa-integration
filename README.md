# Migration RPA System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub repo size](https://img.shields.io/github/repo-size/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)
![License](https://img.shields.io/github/license/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)

> Automação em Python (RPA/ETL) que migra os dados do banco legado do EcoCiente para o novo banco normalizado, com carga transacional, retry, auditoria e reconciliação pós-migração.

## Sobre

O projeto lê o banco legado (modelo do primeiro ano), normaliza e converte os registros para o modelo novo (`tb_*`) e carrega tudo em uma única transação no PostgreSQL de destino. Ao final, confere se o que foi migrado bate com a origem.

Cada execução passa por estas etapas:

```mermaid
flowchart LR
    A[Health check<br/>dos bancos] --> B[1. Extração]
    B --> C[2. Normalização]
    C --> D[3. Transformação<br/>Data Mapper]
    D --> E[4. Validação]
    E --> F[5. Carga<br/>transação + retry]
    F --> G[6. Reconciliação]
    G --> H[Auditoria<br/>SUCCESS / FAILED]
    F -. erro .-> R[(ROLLBACK)]
```

### Ajustes e melhorias

O projeto ainda está em desenvolvimento. Estado atual:

- [x] Extração do legado (usuários, endereços, condomínios, síndicos)
- [x] Normalização (nome, e-mail, CPF, CEP, telefone, datas)
- [x] Data Mapper com mapeamento de IDs legado → novo
- [x] Validação (e-mail, CPF, CEP, campos obrigatórios)
- [x] Carga transacional com retry e rollback
- [x] Carga de `tb_enderecos`, `tb_usuarios` e `tb_sindicos`
- [x] Reconciliação por execução (compara só os IDs criados na rodada)
- [x] Auditoria e logs (`logs/migration.log`, `logs/errors.log`)
- [ ] Carga de condomínios, moradores, telefones e cooperativas
- [ ] Carga idempotente (rodar duas vezes não duplicar dados)
- [ ] Corrigir execução via Docker (ver aviso abaixo)
- [ ] Scheduler de execução automática

## Pré-requisitos

Antes de começar, verifique se você tem:

- Python `3.12` ou superior
- PostgreSQL `16` (pode subir via Docker Compose)
- Docker e Docker Compose, se for usar os bancos em contêiner
- O schema do banco de destino aplicado (`ecociente_schema.sql`) e o banco legado populado
- Windows, Linux ou macOS (o projeto foi desenvolvido e testado no Windows)

## Instalando

Clone o repositório:

```bash
git clone https://github.com/EcoCiente-Instituto-J-F/md-rpa-integration.git
cd md-rpa-integration
```

Crie e ative o ambiente virtual:

Linux e macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

No Windows: `copy .env.example .env`.

<details>
<summary>Variáveis do <code>.env</code></summary>

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `LEGACY_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/ecociente_legado` | Conexão com o banco legado |
| `TARGET_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5433/ecociente_normalizado` | Conexão com o banco de destino |
| `LEGACY_DB_*` / `TARGET_DB_*` | ver `.env.example` | Host, porta, nome, usuário e senha de cada banco |
| `BATCH_SIZE` | `500` | Tamanho do lote na extração em batches |
| `MAX_RETRIES` | `3` | Tentativas da carga antes de falhar de vez |
| `TIMEOUT_SECONDS` | `60` | Timeout das operações |
| `MIGRATION_MODE` | `FULL` | Modo de migração (`FULL`, `INCREMENTAL`, `RETRY`) |
| `LOG_LEVEL` | `INFO` | Nível de log |

</details>

Para subir só os dois bancos com Docker:

```bash
docker compose up -d postgres_legacy postgres_target
```

O legado fica na porta `5432` e o destino na `5433`.

## Usando

Com os bancos no ar e o `.env` preenchido, a partir da raiz do projeto:

```bash
python src/main.py
```

Um log de uma execução bem-sucedida termina assim:

```
reconciliation.py | INFO | Tabela validada: usuario
reconciliation.py | INFO | Tabela validada: endereco
reconciliation.py | INFO | Tabela validada: sindico
orchestrator.py   | INFO | MIGRAÇÃO FINALIZADA COM SUCESSO
migration_log.py  | INFO | Auditoria finalizada: SUCCESS
```

> [!WARNING]
> A carga **ainda não é idempotente**. Cada execução bem-sucedida faz COMMIT e insere tudo de novo. Se rodar duas vezes, os dados ficam duplicados no destino. Antes de repetir uma migração, apague o que a execução anterior inseriu (os IDs criados aparecem no log como `Mapeamento criado ...`).

> [!NOTE]
> A reconciliação compara a contagem do legado com os IDs criados **nesta execução**, e não com o `COUNT(*)` total da tabela de destino. Assim ela funciona mesmo quando o destino já tem dados de outras origens.

### Testes

```bash
pytest
```

### Docker

```bash
docker compose up --build
```

> [!CAUTION]
> O `Dockerfile` e o serviço `migration_rpa` executam `python main.py`, mas o ponto de entrada fica em `src/main.py`. Até isso ser corrigido, rode a aplicação localmente e use o Docker Compose só para os bancos.

## Como funciona

### Etapas do pipeline

| Etapa | Módulo | O que faz |
| --- | --- | --- |
| Extração | `src/extract/` | Consulta o legado (`legacy_queries.py`) e devolve os registros com os IDs antigos como `legacy_*_id` |
| Normalização | `src/transform/normalization.py` | Padroniza texto, e-mail, CPF/CNPJ, CEP e datas, preservando os campos `legacy_*` |
| Transformação | `src/transform/data_mapper.py` | Converte o modelo antigo no modelo novo e controla o mapa de IDs legado → novo |
| Validação | `src/transform/validators.py` | Descarta e registra registros inválidos |
| Carga | `src/load/insert_service.py` | Insere na ordem das FKs: endereços → usuários → síndicos |
| Reconciliação | `src/audit/reconciliation.py` | Confere legado × destino |
| Auditoria | `src/audit/migration_log.py` | Resumo por tabela e status final |

### Chaves estrangeiras

As FKs do destino só existem depois que o pai é inserido. Por isso o `usuario.endereco_id` e o `sindico.usuario_id` são resolvidos **na hora da carga**, a partir do mapa de IDs preenchido pelos inserts anteriores. Os campos `legacy_*` servem só para esse controle e são removidos antes do `INSERT`.

### Transação e retry

- Toda a carga roda em uma única transação: ou entra tudo, ou nada (`ROLLBACK`).
- Se a carga falha, o `RetryHandler` tenta de novo até `MAX_RETRIES` vezes antes de abortar.
- O erro é registrado em `logs/errors.log`.

### Logs

Formato: `DATA | ARQUIVO | NÍVEL | MENSAGEM`

```
2026-09-20 18:21:34 | orchestrator.py | INFO | ETAPA 5 - CARGA
```

## Estrutura do projeto

```
md-rpa-integration/
├── config/
│   └── migration_order.py
├── src/
│   ├── main.py                  # ponto de entrada
│   ├── config/                  # settings, banco e logging
│   ├── extract/                 # legacy_queries, legacy_connector, extract_service
│   ├── transform/               # normalization, data_mapper, validators
│   ├── load/                    # insert_service, transaction_manager, primary_keys
│   ├── rpa/                     # orchestrator, retry_handler, scheduler
│   └── audit/                   # migration_log, error_report, reconciliation
├── test/                        # testes com pytest
├── scripts/pr-bot/              # geração automática de PR
├── logs/                        # migration.log e errors.log
├── reports/
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Contribuindo

Para contribuir com o projeto, siga estas etapas:

1. Bifurque este repositório.
2. Crie um branch: `git checkout -b <nome_branch>`.
3. Faça suas alterações e confirme-as: `git commit -m '<mensagem_commit>'`
4. Envie para o branch original: `git push origin <nome_branch>`
5. Crie a solicitação de pull.

Como alternativa, consulte a documentação do GitHub em [como criar uma solicitação pull](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## 📝 Licença

Esse projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
