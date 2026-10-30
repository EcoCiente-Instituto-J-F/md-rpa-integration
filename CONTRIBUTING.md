# Contribuindo com o md-rpa-integration

Ao participar, você concorda em seguir o [Código de Conduta](CODE_OF_CONDUCT.md). Para reportar um problema de segurança, **não** abra uma issue — siga o [SECURITY.md](SECURITY.md).

## Idioma

Documentação, issues, Pull Requests e mensagens da interface em português do Brasil.

## Configurando o ambiente

1. Instale Python 3.12+ e PostgreSQL 16 (ou use o Docker Compose).
2. Clone e instale as dependências:
   ```bash
   git clone https://github.com/EcoCiente-Instituto-J-F/md-rpa-integration.git
   cd md-rpa-integration
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env                                # Windows: copy .env.example .env
   ```
3. Suba os bancos locais, se precisar: `docker compose up -d postgres_legacy postgres_target`.

## Testando sua mudança

```bash
pytest
```

Toda mudança de comportamento deve vir com teste (em `test/`) que falharia sem ela. Os testes nunca usam os bancos do `.env`; o teste de ponta a ponta só roda com `TEST_LEGACY_URL` e `TEST_TARGET_URL` apontando para bancos **descartáveis**, que ele apaga por inteiro. Não use rede, APIs pagas nem dados de produção.

## Regras do projeto

- Nenhum segredo no repositório: o `.env` é ignorado pelo Git; o `.env.example` só leva valores de desenvolvimento.
- Nenhum dado pessoal real em testes, fixtures ou exemplos.
- Nenhuma dependência nova sem discussão prévia (as versões ficam fixadas em `requirements.txt`).
- A configuração é lida em um só lugar: `src/config/settings.py`. Novas variáveis entram também no `.env.example` e no README.
- Tabelas, ordem de carga e chaves estrangeiras ficam em `src/entidades.py`.
- A carga continua em uma única transação, idempotente (via `tb_migracao_ids_map`) e com reconciliação antes do COMMIT.
- Registro inválido é rejeitado com motivo, sem interromper a execução.
- Formatação com `black`.

## Pull requests

1. Crie uma branch a partir da `main` (ex.: `feat/nome-da-mudanca`).
2. Faça commits focados com prefixos `feat:`, `fix:`, `chore:`, `docs:`, `test:` ou `refactor:`.
3. Abra a PR para a `main`. O bot do projeto preenche a descrição automaticamente (PRs de forks não recebem esse recurso).
4. Rode `pytest` antes de pedir revisão; um mantenedor revisa antes do merge.

## Reportando bugs e propondo funcionalidades

Abra uma issue com o comportamento esperado, o observado, os passos para reproduzir e o ambiente (SO, Python, PostgreSQL). Use dados fictícios. Para vulnerabilidades, siga o [SECURITY.md](SECURITY.md).
