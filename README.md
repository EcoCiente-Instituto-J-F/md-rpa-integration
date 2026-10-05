# Migration RPA System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub repo size](https://img.shields.io/github/repo-size/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)
![License](https://img.shields.io/github/license/EcoCiente-Instituto-J-F/md-rpa-integration?style=for-the-badge)

> Automação em Python (RPA/ETL) que migra os dados do banco legado do EcoCiente para o novo banco normalizado, com interface local, carga transacional, reconciliação antes do COMMIT e reexecução sem duplicar.

## Sobre

O projeto lê o banco legado (modelo do primeiro ano), normaliza e converte os registros para o modelo novo (`tb_*`) e carrega tudo em uma única transação no PostgreSQL de destino. Antes de gravar, confere se a conta fecha para cada tabela:

```
registros no legado = migrados + já migrados + rejeitados
```

Se não fechar, nada é gravado.

```mermaid
flowchart LR
    A[Verificação<br/>dos bancos] --> B[Extração]
    B --> C[Normalização]
    C --> D[Transformação]
    D --> E[Validação]
    E --> F[Carga]
    F --> G[Reconciliação]
    G -- fechou --> H[(COMMIT)]
    G -. não fechou .-> R[(ROLLBACK)]
```

### Estado atual

- [x] Interface local com simulação, migração, rejeitados e log
- [x] Carga de `tb_enderecos`, `tb_usuarios`, `tb_sindicos` e `tb_condominios`
- [x] Registro inválido ou órfão é rejeitado com motivo, sem derrubar a execução
- [x] Carga idempotente (rodar duas vezes não duplica)
- [x] Reconciliação dentro da transação
- [x] Execução via Docker
- [ ] CPF e mandato do síndico, telefones, moradores e cooperativas (dependem do schema de destino, que não está neste repositório)

## Pré-requisitos

- Python `3.12` ou superior
- PostgreSQL `16` (pode subir via Docker Compose)
- O schema do banco de destino aplicado (`ecociente_schema.sql`) e o banco legado populado

## Usando

### Interface (Windows)

Dê dois cliques em **`EcoCiente.bat`**. Na primeira vez ele cria o ambiente virtual, instala as dependências e copia `.env.example` para `.env`; depois abre a interface no navegador, em `http://127.0.0.1:8765`.

Ajuste as conexões no `.env` e clique em **Verificar conexões**.

- **Simular** roda todas as etapas e desfaz tudo no final. Use antes de migrar.
- **Migrar** pede confirmação e grava no destino.
- **Rejeitados** lista cada registro que ficou de fora, com o motivo.
- **Encerrar programa** para o servidor local.

Para gerar um executável único com a logo como ícone, rode **`build_exe.bat`**. O resultado é `dist\EcoCiente.exe`; o `.env` fica na mesma pasta do executável.

### Interface (Linux e macOS)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/ui.py
```

### Linha de comando

```bash
python src/main.py --simular   # roda sem gravar
python src/main.py             # migra
```

### Docker

```bash
docker compose up -d postgres_legacy postgres_target   # só os bancos (5432 e 5433)
docker compose run --rm migration_rpa                  # migração pela linha de comando
```

### Variáveis do `.env`

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `LEGACY_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/ecociente_legado` | Conexão com o banco legado |
| `TARGET_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5433/ecociente_normalizado` | Conexão com o banco de destino |
| `MAX_RETRIES` | `3` | Tentativas da carga quando a conexão com o destino cai |
| `LOG_LEVEL` | `INFO` | Nível de log |

### Testes

```bash
pytest
```

Os testes nunca usam os bancos do `.env`. O teste de ponta a ponta só roda quando dois bancos descartáveis são indicados (ele **apaga e recria** as tabelas neles):

```bash
TEST_LEGACY_URL=postgresql://... TEST_TARGET_URL=postgresql://... pytest
```

## Como funciona

| Etapa | Módulo | O que faz |
| --- | --- | --- |
| Extração | `src/extract/` | Consulta o legado e devolve os registros com os IDs antigos como `legacy_*_id` |
| Normalização | `src/transform/normalization.py` | Padroniza nome, e-mail, CPF/CNPJ, CEP e o status do usuário |
| Transformação | `src/transform/data_mapper.py` | Converte o modelo antigo no novo |
| Validação | `src/transform/validators.py` | Separa os registros inválidos e registra o motivo |
| Carga | `src/load/insert_service.py` | Insere na ordem das FKs e grava o mapa de IDs |
| Reconciliação | `src/audit/reconciliation.py` | Confere legado × destino antes do COMMIT |
| Auditoria | `src/audit/migration_log.py` | Etapas, contagens por tabela e status final |

A ordem das tabelas e as chaves estrangeiras ficam em `src/entidades.py`.

### Registros rejeitados

Um registro fica de fora, sem interromper a migração, quando:

- falha na validação (campo obrigatório vazio, e-mail, CPF, CNPJ ou CEP inválido);
- depende de um registro que não foi migrado (por exemplo, usuário de um endereço rejeitado);
- é recusado pelo banco de destino (por exemplo, e-mail duplicado).

Erros de estrutura, como coluna inexistente, abortam a execução e nada é gravado.

### Idempotência

A carga cria no destino a tabela de controle `migracao_id_map (entidade, legacy_id, novo_id)`. Registro que já está nela não é inserido de novo, então repetir a migração só leva o que faltava.

Se linhas migradas forem apagadas do destino, a reconciliação acusa a divergência. Apague também as linhas correspondentes de `migracao_id_map` para migrá-las outra vez.

### Decisões que valem conferir

- **Senha**: o legado não tem senha. Todo usuário entra com `senha_hash = 'MIGRACAO_TEMP'` e precisa redefinir no primeiro acesso.
- **Status do usuário**: `status` vazio no legado entra como ativo. Texto é comparado sem diferenciar maiúsculas com `sim`, `s`, `true`, `t`, `1`, `ativo` e `a`; ajuste a lista em `normalization.py` se o legado usar outro valor.
- **Síndico do condomínio**: no legado o síndico aponta para o condomínio; no destino é o inverso. Com mais de um síndico por condomínio, vale o de maior ID.
- **Colunas de `tb_condominios`**: vêm do `data_mapper` (`nome_condominio`, `cnpj`, `endereco_id`, `sindico_id`) e não foram conferidas com o schema oficial.

### Logs

`logs/migration.log` (tudo) e `logs/errors.log` (só erros), no formato `DATA | ARQUIVO | NÍVEL | MENSAGEM`.

## Estrutura do projeto

```
md-rpa-integration/
├── EcoCiente.bat                # abre a interface (Windows)
├── build_exe.bat                # gera dist\EcoCiente.exe
├── src/
│   ├── ui.py                    # servidor local da interface
│   ├── ui_static/index.html     # a interface
│   ├── main.py                  # linha de comando
│   ├── entidades.py             # tabelas, ordem e FKs
│   ├── config/                  # settings, banco e logging
│   ├── extract/                 # legacy_queries, extract_service
│   ├── transform/               # normalization, data_mapper, validators
│   ├── load/                    # insert_service
│   ├── rpa/                     # orchestrator
│   └── audit/                   # migration_log, reconciliation
├── test/                        # pytest (unidade e ponta a ponta)
├── assets/                      # logo e ícone
├── scripts/pr-bot/              # geração automática de PR
├── PRODUCT.md / DESIGN.md       # contexto de produto e de design da interface
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Colaboradores

Agradecemos às seguintes pessoas que contribuíram para este projeto:

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/shinitihm" title="Perfil no GitHub">
        <img src="https://github.com/shinitihm.png" width="100px;" alt="Foto de shinitihm no GitHub"/><br>
        <sub>
          <b>shinitihm</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

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
<div align="center">

Desenvolvido por:

<img src="assets/logo-ecociente.png" alt="EcoCiente - Dados que despertam a consciência" width="320"> </div>
