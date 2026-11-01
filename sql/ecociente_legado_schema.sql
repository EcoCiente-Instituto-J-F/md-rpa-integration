-- Armazena os endereços utilizados pelas entidades do sistema.
CREATE TABLE endereco (
	id_endereco INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	cep VARCHAR(8) NOT NULL CHECK(LENGTH(cep) = 8),
	cidade VARCHAR(100) NOT NULL,
	estado CHAR(2) NOT NULL CHECK(LENGTH(estado) = 2),
	bairro VARCHAR (100),
	rua VARCHAR(100) NOT NULL,
	numero VARCHAR(12) NOT NULL,
	complemento VARCHAR(100)
);

-- Armazena os tipos de usuários disponíveis no sistema.
CREATE TABLE tipo_usuario(
	id_tipo_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome_tipo VARCHAR(50) NOT NULL,
	descricao VARCHAR(100)
);

-- Armazena os tipos de condomínios cadastráveis.
CREATE TABLE tipo_condominio(
	id_tipo_condominio INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome_tipo VARCHAR(50) NOT NULL,
	descricao VARCHAR(100)
);

-- Armazena os dados dos usuários do sistema.
CREATE TABLE usuario(
	id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	cpf VARCHAR(11) UNIQUE CHECK(LENGTH(cpf)=11),
	email VARCHAR(150) NOT NULL UNIQUE,
	senha_hash VARCHAR(255) NOT NULL,
	data_cadastro DATE NOT NULL DEFAULT CURRENT_DATE,
	status BOOLEAN NOT NULL DEFAULT TRUE,
	id_endereco INT,
	id_tipo_usuario INT NOT NULL,
	
	CONSTRAINT fk_usuario_endereco
		FOREIGN KEY(id_endereco)
		REFERENCES endereco(id_endereco),
	
	CONSTRAINT fk_usuario_tipo
		FOREIGN KEY(id_tipo_usuario)
		REFERENCES tipo_usuario(id_tipo_usuario)
); 

-- Armazena os telefones associados aos usuários.
CREATE TABLE telefone(
	id_telefone INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	numero VARCHAR(11) NOT NULL CHECK(LENGTH(numero)>= 9 and LENGTH(numero)<=11),
	id_usuario INT NOT NULL,
	
	CONSTRAINT fk_telefone_usuario
		FOREIGN KEY(id_usuario)
		REFERENCES usuario(id_usuario)
);

-- Armazena os condomínios cadastrados.
CREATE TABLE condominio(
	id_condominio INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	cnpj VARCHAR(14) NOT NULL UNIQUE CHECK(LENGTH(cnpj) = 14),
	status BOOLEAN NOT NULL DEFAULT TRUE,
	numero_unidades INT CHECK(numero_unidades > 0),
	area_m2 NUMERIC(12,2) CHECK(area_m2 > 0),
	token VARCHAR(255) UNIQUE,
	id_endereco INT NOT NULL,
	id_tipo_condominio INT,
	
	CONSTRAINT ck_condominio_unidades_ou_area
		CHECK(numero_unidades IS NULL OR area_m2 IS NULL),
	
	CONSTRAINT fk_condominio_endereco
		FOREIGN KEY (id_endereco)
		REFERENCES endereco(id_endereco),
	
	CONSTRAINT fk_condominio_tipo
		FOREIGN KEY (id_tipo_condominio)
		REFERENCES tipo_condominio(id_tipo_condominio)
);

-- Armazena os síndicos responsáveis pelos condomínios.
CREATE TABLE sindico(
	id_sindico INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	data_inicio_mandato DATE,
	data_fim_mandato DATE,
	id_usuario INT NOT NULL UNIQUE,
	id_condominio INT NOT NULL,
	
	CONSTRAINT fk_sindico_usuario 
		FOREIGN KEY(id_usuario)
		REFERENCES usuario(id_usuario),
	
	CONSTRAINT fk_sindico_condominio
		FOREIGN KEY(id_condominio)
		REFERENCES condominio(id_condominio)
);

-- Armazena os moradores dos condomínios.
CREATE TABLE morador (
    id_morador INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_apartamento VARCHAR(10),
    id_usuario INTEGER NOT NULL UNIQUE,
    torre VARCHAR(30),
    id_condominio INT NOT NULL,

	CONSTRAINT fk_morador_condominio
		FOREIGN KEY (id_condominio)
		REFERENCES condominio (id_condominio),

	CONSTRAINT fk_morador_usuario
		FOREIGN KEY (id_usuario)
		REFERENCES usuario (id_usuario)
);

-- Armazena as cooperativas cadastradas no sistema.
CREATE TABLE cooperativa (
	id_cooperativa INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	nome_cooperativa VARCHAR(100) NOT NULL,
	cnpj VARCHAR(14) NOT NULL UNIQUE check (LENGTH(cnpj) = 14),
	id_usuario INT NOT NULL UNIQUE,
	
	CONSTRAINT fk_cooperativa_usuario 
		FOREIGN KEY (id_usuario)
		REFERENCES usuario (id_usuario)
);

-- Representa o relacionamento entre condomínios e cooperativas.
CREATE TABLE parceira (
	id_parceira INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	data_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
	data_fim DATE CHECK (data_fim IS NULL OR data_fim >= data_inicio),
	id_condominio INT NOT NULL,
	id_cooperativa INT NOT NULL,
	
	CONSTRAINT uq_parceira_vinculo
		UNIQUE (id_condominio, id_cooperativa, data_inicio),
	
	CONSTRAINT fk_parceira_condominio
		FOREIGN KEY (id_condominio)
		REFERENCES condominio (id_condominio),
	
	CONSTRAINT fk_parceira_cooperativa
		FOREIGN KEY (id_cooperativa)
		REFERENCES cooperativa (id_cooperativa)
);

-- Armazena os planos de assinatura disponíveis para cobrança.
CREATE TABLE plano (
	id_plano INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	codigo VARCHAR(20) NOT NULL UNIQUE,
	nome VARCHAR(60) NOT NULL,
	descricao VARCHAR(100),
	unidade VARCHAR(20) NOT NULL CHECK(unidade IN ('unidade', 'm2')),
	preco_mensal NUMERIC(10,2) NOT NULL CHECK(preco_mensal > 0),
	preco_anual NUMERIC(10,2) NOT NULL CHECK(preco_anual > 0),
	ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Armazena as assinaturas contratadas por usuários e condomínios.
CREATE TABLE assinatura (
	id_assinatura INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	ciclo VARCHAR(10) NOT NULL CHECK(ciclo IN ('mensal', 'anual')),
	quantidade NUMERIC(12,2) NOT NULL CHECK(quantidade > 0),
	valor_cobrado NUMERIC(12,2) NOT NULL CHECK(valor_cobrado > 0),
	status VARCHAR(10) NOT NULL DEFAULT 'pendente' CHECK(status IN ('pendente', 'ativa', 'cancelada')),
	data_inicio DATE,
	proxima_cobranca DATE,
	data_cadastro DATE NOT NULL DEFAULT CURRENT_DATE,
	id_usuario INT NOT NULL UNIQUE,
	id_condominio INT UNIQUE,
	id_plano INT NOT NULL,
	
	CONSTRAINT ck_assinatura_ativa_com_inicio
	CHECK(status != 'ativa' OR data_inicio IS NOT NULL),
	
	CONSTRAINT ck_assinatura_cobranca_apos_inicio
		CHECK(proxima_cobranca IS NULL OR data_inicio IS NULL OR proxima_cobranca >= data_inicio),
	
	CONSTRAINT fk_assinatura_usuario
		FOREIGN KEY (id_usuario)
		REFERENCES usuario (id_usuario),
	
	CONSTRAINT fk_assinatura_condominio
		FOREIGN KEY (id_condominio)
		REFERENCES condominio (id_condominio),
	
	CONSTRAINT fk_assinatura_plano
		FOREIGN KEY (id_plano)
		REFERENCES plano (id_plano)
);