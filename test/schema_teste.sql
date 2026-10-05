-- Schema MÍNIMO para o teste de ponta a ponta, inferido das consultas em
-- src/extract/legacy_queries.py e das colunas gravadas pelo data_mapper.
-- NÃO é o schema oficial (ecociente_schema.sql), que não está neste repositório.

-- legado
DROP TABLE IF EXISTS sindico, condominio, usuario, endereco CASCADE;
CREATE TABLE endereco (
    id_endereco serial PRIMARY KEY, rua text, numero text, bairro text,
    cidade text, estado text, cep text, complemento text
);
CREATE TABLE usuario (
    id_usuario serial PRIMARY KEY, id_endereco int, id_tipo_usuario int,
    nome text, email text, status text, data_cadastro timestamp
);
CREATE TABLE condominio (
    id_condominio serial PRIMARY KEY, nome text, cnpj text, id_endereco int
);
CREATE TABLE sindico (
    id_sindico serial PRIMARY KEY, cpf text, data_inicio_mandato date,
    data_fim_mandato date, id_usuario int, id_condominio int
);

-- destino
DROP TABLE IF EXISTS tb_condominios, tb_sindicos, tb_usuarios, tb_enderecos,
    migracao_id_map CASCADE;
CREATE TABLE tb_enderecos (
    id_endereco serial PRIMARY KEY, logradouro text, numero text,
    cidade text NOT NULL, estado text, cep text, complemento text
);
CREATE TABLE tb_usuarios (
    id_usuario serial PRIMARY KEY, nome_usuario text NOT NULL,
    email_usuario text UNIQUE, senha_hash text NOT NULL, cpf text,
    ativo boolean NOT NULL, registro_em timestamp NOT NULL,
    tipo_usuario_id int NOT NULL,
    endereco_id int NOT NULL REFERENCES tb_enderecos
);
CREATE TABLE tb_sindicos (
    id_sindico serial PRIMARY KEY,
    usuario_id int NOT NULL REFERENCES tb_usuarios
);
CREATE TABLE tb_condominios (
    id_condominio serial PRIMARY KEY, nome_condominio text NOT NULL, cnpj text,
    endereco_id int REFERENCES tb_enderecos,
    sindico_id int REFERENCES tb_sindicos
);
