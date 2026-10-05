"""
Data Mapper: converte o modelo legado no modelo normalizado e guarda o mapa
de IDs legado -> novo.

Os campos `legacy_*` seguem no registro até a carga, que os usa para resolver
as chaves estrangeiras e os remove antes do INSERT.
"""

from datetime import datetime

from config.logging_config import get_logger
from entidades import ENTIDADES

logger = get_logger()


def _ativo(value):
    return True if value is None else value


def _legacy(record, *entidades):
    return {f"legacy_{e}_id": record.get(f"legacy_{e}_id") for e in entidades}


class DataMapper:
    def __init__(self):
        self.id_mapping = {entidade.nome: {} for entidade in ENTIDADES}

    def map_tipo(self, tipo, entidade):
        return {
            "nome_tipo": tipo.get("nome_tipo"),
            "descricao": tipo.get("descricao"),
            **_legacy(tipo, entidade),
        }

    def map_tipo_usuario(self, tipo):
        return self.map_tipo(tipo, "tipo_usuario")

    def map_tipo_condominio(self, tipo):
        return self.map_tipo(tipo, "tipo_condominio")

    def map_endereco(self, endereco):
        numero = endereco.get("numero")
        return {
            "logradouro": endereco.get("logradouro"),
            "numero": None if numero is None else str(numero),
            "bairro": endereco.get("bairro"),
            "cidade": endereco.get("cidade"),
            "estado": endereco.get("estado"),
            "cep": endereco.get("cep"),
            "complemento": endereco.get("complemento"),
            **_legacy(endereco, "endereco"),
        }

    def map_usuario(self, usuario):
        return {
            "nome_usuario": usuario.get("nome"),
            "email_usuario": usuario.get("email"),
            # O senha_hash do legado é INTEGER, não é um hash utilizável:
            # o usuário redefine a senha no primeiro acesso.
            "senha_hash": "MIGRACAO_TEMP",
            "cpf": usuario.get("cpf"),
            "ativo": _ativo(usuario.get("ativo")),
            "registro_em": usuario.get("data_cadastro") or datetime.now(),
            **_legacy(usuario, "usuario", "tipo_usuario", "endereco"),
        }

    def map_telefone(self, telefone):
        return {
            "numero_contato": telefone.get("numero"),
            **_legacy(telefone, "telefone", "usuario"),
        }

    def map_sindico(self, sindico):
        return _legacy(sindico, "sindico", "usuario")

    def map_condominio(self, condominio):
        return {
            "nome_condominio": condominio.get("nome"),
            "cnpj": condominio.get("cnpj"),
            "codigo_acesso": condominio.get("token"),
            "ativo": _ativo(condominio.get("ativo")),
            **_legacy(
                condominio, "condominio", "tipo_condominio", "endereco", "sindico"
            ),
        }

    def map_torre(self, torre):
        return {
            "nome_torre": torre.get("nome"),
            **_legacy(torre, "torre", "condominio"),
        }

    def map_morador(self, morador):
        return _legacy(morador, "morador", "usuario", "condominio")

    def map_cooperativa(self, cooperativa):
        return {
            "cnpj_cooperativa": cooperativa.get("cnpj"),
            "nome_cooperativa": cooperativa.get("nome"),
            "email_cooperativa": cooperativa.get("email"),
            **_legacy(cooperativa, "cooperativa", "usuario"),
        }

    def transform_dataset(self, dataset):
        sindicos = dataset.get("sindicos", [])
        # No destino o CPF fica no usuário; no legado só o síndico tem CPF.
        cpf_do_usuario = {s.get("legacy_usuario_id"): s.get("cpf") for s in sindicos}
        # No legado o síndico aponta para o condomínio; no destino é o inverso.
        # ponytail: com mais de um síndico por condomínio vale o de maior ID.
        sindico_do_condominio = {
            s.get("legacy_condominio_id"): s.get("legacy_sindico_id") for s in sindicos
        }
        enriquecido = {
            **dataset,
            "usuarios": [
                {**u, "cpf": cpf_do_usuario.get(u.get("legacy_usuario_id"))}
                for u in dataset.get("usuarios", [])
            ],
            "condominios": [
                {
                    **c,
                    "legacy_sindico_id": sindico_do_condominio.get(
                        c.get("legacy_condominio_id")
                    ),
                }
                for c in dataset.get("condominios", [])
            ],
        }
        transformed = {
            e.dataset: [
                getattr(self, f"map_{e.nome}")(record)
                for record in enriquecido.get(e.dataset, [])
            ]
            for e in ENTIDADES
        }
        logger.info("Transformação concluída")
        return transformed

    def save_mapping(self, entity, old_id, new_id):
        if old_id is not None:
            self.id_mapping[entity][old_id] = new_id

    def get_new_id(self, entity, old_id):
        return self.id_mapping.get(entity, {}).get(old_id)
