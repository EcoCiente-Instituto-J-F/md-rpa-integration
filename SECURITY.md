# Política de Segurança

O md-rpa-integration lê um banco legado e grava em um banco de destino que contêm dados pessoais (nome, e-mail, CPF/CNPJ, telefone e endereço), e usa as URLs de conexão dos dois bancos, definidas no `.env`.

## Versões suportadas

| Versão | Suporte |
| --- | --- |
| `main` (mais recente) | Sim |
| Demais branches | Não |

## Reportando uma vulnerabilidade

**Não abra issue, Pull Request ou discussão pública** para relatar vulnerabilidades.

Use o relato privado do GitHub: <https://github.com/EcoCiente-Instituto-J-F/md-rpa-integration/security/advisories/new> (Security → Advisories → Report a vulnerability).

> Mantenedores: ative *Private vulnerability reporting* em Settings → Code security.

Inclua no relato:

- o impacto da falha;
- os passos para reproduzir, usando **dados fictícios**;
- o commit testado e a configuração;
- se possível, uma ideia de correção.

Depois do relato: confirmaremos o recebimento, corrigiremos de forma privada e publicaremos um advisory com crédito a quem reportou, se desejado. Pedimos um prazo razoável para a correção antes de qualquer divulgação pública.

## Escopo

**Dentro do escopo**

- Acesso à interface local (`src/ui.py`) por outra origem ou máquina, incluindo DNS rebinding e CSRF
- Injeção SQL nas consultas do legado ou na carga
- Vazamento de dados pessoais ou das URLs de conexão em logs (`logs/`), relatórios de rejeitados ou respostas da interface
- Segredos commitados (`.env`)
- Falhas no workflow do bot de PR (`pr-bot.yml`) que exponham segredos

**Fora do escopo**

- Bugs sem impacto de segurança
- Credenciais de desenvolvimento do `docker-compose.yaml` (`postgres:postgres`) usadas localmente
- Falhas em serviços de terceiros (PostgreSQL, GitHub)
- Negação de serviço na máquina que executa a migração

## Como o sistema protege os dados

| Camada | Onde | O que faz |
| --- | --- | --- |
| Interface local | `src/ui.py` | Escuta só em `127.0.0.1:8765` e aceita apenas requisições cujo `Host` seja `127.0.0.1` ou `localhost` (barra DNS rebinding) |
| Segredos | `.gitignore`, `.env.example` | `.env` não é versionado; o exemplo traz só valores de desenvolvimento |
| Senhas | `src/transform/data_mapper.py` | Nenhuma senha é migrada: todo usuário recebe `MIGRACAO_TEMP` e precisa redefinir no primeiro acesso |
| Integridade | `src/audit/reconciliation.py`, `src/load/` | Carga em uma única transação, com reconciliação antes do COMMIT (ROLLBACK se não fechar) |
| Testes | `test/` | Não usam os bancos do `.env`; o teste de ponta a ponta só roda com bancos descartáveis informados |

## Checklist de deploy

- Trocar as credenciais `postgres:postgres` por usuários próprios, com o mínimo de permissões (leitura no legado; escrita só nas tabelas de destino).
- Manter o `.env` fora do repositório, da imagem e de compartilhamentos.
- Executar a migração em máquina protegida e restringir o acesso à pasta `logs/` e aos relatórios de rejeitados, que podem conter dados pessoais.
- Garantir que todo usuário migrado (`senha_hash = 'MIGRACAO_TEMP'`) seja forçado a redefinir a senha antes de qualquer login.
- Não expor a interface local (`127.0.0.1:8765`) em rede.
