from transform.normalization import DataNormalizer

n = DataNormalizer()


def test_normalize_email():
    assert n.normalize_email("  TESTE@EMAIL.COM ") == "teste@email.com"


def test_normalize_name_mantem_particulas_minusculas():
    assert n.normalize_name("  JOÃO   DA SILVA ") == "João da Silva"


def test_normalize_zipcode():
    assert n.normalize_zipcode("1310-100") == "01310100"


def test_normalize_boolean_aceita_texto_do_legado():
    assert n.normalize_boolean("Ativo") is True
    assert n.normalize_boolean("inativo") is False
    assert n.normalize_boolean(None) is None


def test_dataset_nao_descarta_condominios_nem_sindicos():
    out = n.normalize_dataset(
        {
            "condominios": [{"nome": " Vila  Verde ", "cnpj": "12.345.678/0001-90"}],
            "sindicos": [{"legacy_sindico_id": 1}],
        }
    )
    assert out["condominios"] == [{"nome": "Vila Verde", "cnpj": "12345678000190"}]
    assert out["sindicos"] == [{"legacy_sindico_id": 1}]
