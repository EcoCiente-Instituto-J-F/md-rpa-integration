# Migration RPA System

## Integração RPA para Migração de Dados entre Banco Legado e Banco Normalizado

---

# Sobre o Projeto

O **Migration RPA System** é uma solução de automação desenvolvida em Python para realizar a migração segura de dados entre um banco de dados legado e um novo banco de dados normalizado.

O sistema utiliza conceitos de:

- RPA (Robotic Process Automation)
- ETL (Extract, Transform, Load)
- Engenharia de Dados
- Modelagem Relacional
- Controle Transacional
- Auditoria de Dados
- Tratamento de Falhas

O objetivo principal é garantir que a movimentação dos dados ocorra com:

✅ Integridade referencial  
✅ Rastreabilidade  
✅ Controle de erros  
✅ Possibilidade de reprocessamento  
✅ Validação pós-migração  

---

# 🎯 Objetivo

Realizar a integração entre:

```

Banco Legado
|
|
↓
Processo RPA / ETL
|
|
↓
Banco Normalizado

```

O processo é responsável por:

1. Extrair informações do sistema antigo.
2. Transformar os dados para o novo modelo.
3. Normalizar informações inconsistentes.
4. Carregar dados no novo banco.
5. Validar integridade.
6. Gerar relatórios de auditoria.

---

# 🏗️ Arquitetura da Solução

```

```

             RPA ORCHESTRATOR

                   |
                   |

    +--------------+--------------+

    |                             |

 EXTRACT                       LOAD

    |                             |

```

Banco Legado                 Banco Normalizado

```

    |

    ↓

```

Data Mapper

```

    |

    ↓

```

Normalization

```

    |

    ↓

```

Validation

```

    |

    ↓

```

Audit / Reports

```

---

# 🧩 Tecnologias Utilizadas

## Backend

- Python 3.12

## Banco de Dados

- PostgreSQL 16

## ORM / Conexão

- SQLAlchemy

## Configuração

- Pydantic Settings
- python-dotenv

## Testes

- Pytest

## Infraestrutura

- Docker
- Docker Compose

---

# 📂 Estrutura do Projeto

```

migration-rpa-project/

├── config/

│   ├── database.py

│   ├── settings.py

│   └── logging_config.py

├── src/

│   ├── extract/

│   │   ├── legacy_connector.py

│   │   ├── legacy_queries.py

│   │   └── extract_service.py

│

│   ├── transform/

│   │   ├── data_mapper.py

│   │   ├── normalization.py

│   │   └── validators.py

│

│   ├── load/

│   │   ├── insert_service.py

│   │   ├── target_connector.py

│   │   └── transaction_manager.py

│

│   ├── rpa/

│   │   ├── orchestrator.py

│   │   ├── retry_handler.py

│   │   └── scheduler.py

│

│   └── audit/

│       ├── migration_log.py

│       ├── error_report.py

│       └── reconciliation.py

├── tests/

├── logs/

├── reports/

├── main.py

├── Dockerfile

├── docker-compose.yml

├── requirements.txt

└── .env.example

```

---

# 🔄 Fluxo de Execução

## 1. Extração

Responsável por consultar o banco legado.

Exemplo:

```

Banco Antigo

usuario
material
endereco
condominio

```

    ↓

```

Extract Service

```

---

## 2. Transformação

O Data Mapper converte:

```

Modelo Antigo

```

    ↓

```

Modelo Novo

````

Exemplo:

Antes:

```json
{
 "nome_usuario":"João"
}
````

Depois:

```json
{
 "nome":"João"
}
```

---

## 3. Normalização

Tratamento dos dados:

Exemplo:

Entrada:

```
 JOAO@EMAIL.COM
```

Saída:

```
joao@email.com
```

Entrada:

```
(82) 99999-9999
```

Saída:

```
82999999999
```

---

## 4. Carga

Inserção no banco destino:

```
INSERT

↓

Commit

↓

Auditoria

```

Caso aconteça erro:

```
INSERT

↓

Erro

↓

Rollback

↓

Registro da falha

```

---

# Controle Transacional

O sistema utiliza transações ACID:

## Atomicidade

Ou tudo é salvo ou nada é salvo.

## Consistência

Relacionamentos permanecem válidos.

## Isolamento

Execuções não interferem umas nas outras.

## Durabilidade

Dados confirmados permanecem persistidos.

---

# Tratamento de Falhas

O sistema possui:

## Retry automático

Quando ocorre erro temporário:

```
Tentativa 1

↓

Falha

↓

Tentativa 2

↓

Falha

↓

Tentativa 3

↓

Abortar
```

## Registro de erros

Cada falha possui:

```
Tabela

Registro

Operação

Mensagem

Data

Status

```

---

# Auditoria

Após a execução é gerado:

```
RELATÓRIO DE MIGRAÇÃO


Tabela: usuario


Origem:
10000


Destino:
10000


Diferença:
0


Status:
OK

```

---

# Reconciliação

O sistema compara:

```
Banco Legado

        VS

Banco Normalizado

```

Validando:

- quantidade de registros;
- registros perdidos;
- divergências;
- integridade.

---

# Logs

Formato:

```
DATA | ARQUIVO | TIPO | MENSAGEM

```

Exemplo:

```
2026-09-13 20:30:00 | extract_service.py | INFO | Extração iniciada


2026-09-13 20:31:00 | insert_service.py | ERROR | Falha ao inserir usuário

```

Arquivos:

```
logs/

├── migration.log

└── errors.log

```

---

# Instalação Manual

## 1. Clonar projeto

```bash
git clone repositorio
```

## 2. Criar ambiente virtual

```bash
python -m venv venv
```

Ativar:

Windows:

```bash
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 4. Configurar ambiente

Copiar:

```
.env.example

para

.env

```

Preencher credenciais dos bancos.

---

# Executando com Docker

Construir:

```bash
docker compose up --build
```

O ambiente irá criar:

```
PostgreSQL Legado

        +

PostgreSQL Normalizado

        +

Aplicação RPA

```

---

# Executar Migração

Modo manual:

```bash
python main.py
```

Modo automático:

```bash
python scheduler_main.py
```

---

# 🧪 Executar Testes

```bash
pytest
```

Resultado esperado:

```
5 passed

```

---

# Padrões Aplicados

O projeto utiliza:

- Clean Architecture
- Separação de responsabilidades
- ETL Pipeline
- Dependency Injection
- Logging estruturado
- Testes automatizados
- Controle transacional

---

# Conclusão

O Migration RPA System fornece uma solução robusta para migração de dados entre sistemas legados e novas arquiteturas normalizadas, garantindo segurança, rastreabilidade e confiabilidade durante todo o processo.

```


