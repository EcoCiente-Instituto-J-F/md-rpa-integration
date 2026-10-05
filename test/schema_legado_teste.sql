-- Tabelas do banco legado usadas pela migração, conforme docs/banco-legado-er.png.
-- Só para o teste de ponta a ponta.
DROP TABLE IF EXISTS cooperativa, morador, torre, sindico, condominio,
    telefone_usuario, usuario, endereco, tipo_condominio, tipo_usuario CASCADE;

CREATE TABLE tipo_usuario (
    id_tipo_usuario serial PRIMARY KEY, nome_tipo varchar, descricao varchar
);
CREATE TABLE tipo_condominio (
    id_tipo_condominio serial PRIMARY KEY, nome_tipo varchar, descricao varchar
);
CREATE TABLE endereco (
    id_endereco serial PRIMARY KEY, cep varchar, cidade varchar, estado varchar,
    bairro varchar, rua varchar, numero integer, complemento varchar
);
CREATE TABLE usuario (
    id_usuario serial PRIMARY KEY, nome varchar, email varchar,
    senha_hash integer, data_cadastro date, status boolean,
    id_endereco integer REFERENCES endereco,
    id_tipo_usuario integer REFERENCES tipo_usuario
);
CREATE TABLE telefone_usuario (
    id_telefone serial PRIMARY KEY, numero varchar,
    id_usuario integer REFERENCES usuario
);
CREATE TABLE condominio (
    id_condominio serial PRIMARY KEY, nome varchar, cnpj varchar,
    status boolean, token varchar,
    id_endereco integer REFERENCES endereco,
    id_tipo_condominio integer REFERENCES tipo_condominio
);
CREATE TABLE sindico (
    id_sindico serial PRIMARY KEY, cpf varchar, data_inicio_mandato date,
    data_fim_mandato date, id_usuario integer REFERENCES usuario,
    id_condominio integer REFERENCES condominio
);
CREATE TABLE torre (
    id_torre serial PRIMARY KEY, nome varchar, numero_unidades integer,
    id_condominio integer REFERENCES condominio
);
CREATE TABLE morador (
    id_morador serial PRIMARY KEY, numero_apartamento varchar,
    nivel_engajamento varchar, id_usuario integer REFERENCES usuario,
    id_torre integer REFERENCES torre
);
CREATE TABLE cooperativa (
    id_cooperativa serial PRIMARY KEY, cnpj varchar,
    id_usuario integer REFERENCES usuario
);
