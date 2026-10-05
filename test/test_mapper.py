from transform.data_mapper import DataMapper
from transform.validators import DataValidator


def test_map_usuario():
    result = DataMapper().map_usuario(
        {
            "nome": "Carlos",
            "email": "carlos@email.com",
            "ativo": None,
            "data_cadastro": None,
            "legacy_usuario_id": 7,
        }
    )
    assert result["nome_usuario"] == "Carlos"
    assert result["email_usuario"] == "carlos@email.com"
    assert result["ativo"] is True  # status vazio no legado: entra ativo
    assert result["registro_em"] is not None
    assert result["legacy_usuario_id"] == 7


def test_condominio_recebe_o_sindico_do_legado():
    out = DataMapper().transform_dataset(
        {
            "sindicos": [{"legacy_sindico_id": 5, "legacy_condominio_id": 2}],
            "condominios": [{"legacy_condominio_id": 2, "nome": "Vila Verde"}],
        }
    )
    assert out["condominios"][0]["legacy_sindico_id"] == 5


def test_validacao_rejeita_e_explica():
    validator = DataValidator()
    valid = validator.validate_dataset(
        {
            "usuarios": [
                {
                    "legacy_usuario_id": 1,
                    "nome_usuario": "Ana",
                    "tipo_usuario_id": 1,
                    "email_usuario": "ana@email.com",
                },
                {
                    "legacy_usuario_id": 2,
                    "nome_usuario": "Bia",
                    "tipo_usuario_id": 1,
                    "email_usuario": "bia-sem-arroba",
                },
            ]
        }
    )
    assert [u["legacy_usuario_id"] for u in valid["usuarios"]] == [1]
    assert validator.errors == [
        {
            "entidade": "usuario",
            "legacy_id": 2,
            "campo": "email_usuario",
            "valor": "bia-sem-arroba",
            "motivo": "E-mail inválido",
        }
    ]


def test_cpf_do_sindico_vai_para_o_usuario():
    out = DataMapper().transform_dataset(
        {
            "usuarios": [{"legacy_usuario_id": 1, "nome": "Ana"}],
            "sindicos": [
                {"legacy_sindico_id": 5, "legacy_usuario_id": 1, "cpf": "11122233344"}
            ],
        }
    )
    assert out["usuarios"][0]["cpf"] == "11122233344"
    assert out["sindicos"] == [{"legacy_sindico_id": 5, "legacy_usuario_id": 1}]
