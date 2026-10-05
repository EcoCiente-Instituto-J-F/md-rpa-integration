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


class DataMapper:
    def __init__(self):
        self.id_mapping = {entidade.nome: {} for entidade in ENTIDADES}

    def map_usuario(self, usuario):
        ativo = usuario.get("ativo")
        return {
            "nome_usuario": usuario.get("nome"),
            "email_usuario": usuario.get("email"),
            # O legado não tem senha: o usuário redefine no primeiro acesso.
            "senha_hash": usuario.get("senha_hash") or "MIGRACAO_TEMP",
            "cpf": usuario.get("cpf"),
            "ativo": True if ativo is None else ativo,
            "registro_em": usuario.get("data_cadastro") or datetime.now(),
            "tipo_usuario_id": usuario.get("tipo_usuario_id"),
            "legacy_usuario_id": usuario.get("legacy_usuario_id"),
            "legacy_endereco_id": usuario.get("legacy_endereco_id"),
        }

    def map_endereco(self, endereco):
        return {
            "logradouro": endereco.get("logradouro"),
            "numero": endereco.get("numero"),
            "cidade": endereco.get("cidade"),
            "estado": endereco.get("estado"),
            "cep": endereco.get("cep"),
            "complemento": endereco.get("complemento"),
            "legacy_endereco_id": endereco.get("legacy_endereco_id"),
        }

    def map_sindico(self, sindico):
        return {
            "legacy_sindico_id": sindico.get("legacy_sindico_id"),
            "legacy_usuario_id": sindico.get("legacy_usuario_id"),
        }

    def map_condominio(self, condominio):
        return {
            "nome_condominio": condominio.get("nome"),
            "cnpj": condominio.get("cnpj"),
            "legacy_condominio_id": condominio.get("legacy_condominio_id"),
            "legacy_endereco_id": condominio.get("legacy_endereco_id"),
            "legacy_sindico_id": condominio.get("legacy_sindico_id"),
        }

    def transform_dataset(self, dataset):
        # No legado o síndico aponta para o condomínio; no destino é o inverso.
        # ponytail: com mais de um síndico por condomínio vale o de maior ID.
        sindico_do_condominio = {
            sindico.get("legacy_condominio_id"): sindico.get("legacy_sindico_id")
            for sindico in dataset.get("sindicos", [])
        }
        condominios = [
            {
                **condominio,
                "legacy_sindico_id": sindico_do_condominio.get(
                    condominio.get("legacy_condominio_id")
                ),
            }
            for condominio in dataset.get("condominios", [])
        ]
        transformed = {
            "enderecos": [self.map_endereco(r) for r in dataset.get("enderecos", [])],
            "usuarios": [self.map_usuario(r) for r in dataset.get("usuarios", [])],
            "sindicos": [self.map_sindico(r) for r in dataset.get("sindicos", [])],
            "condominios": [self.map_condominio(r) for r in condominios],
        }
        logger.info("Transformação concluída")
        return transformed

    def save_mapping(self, entity, old_id, new_id):
        if old_id is not None:
            self.id_mapping[entity][old_id] = new_id

    def get_new_id(self, entity, old_id):
        return self.id_mapping.get(entity, {}).get(old_id)
