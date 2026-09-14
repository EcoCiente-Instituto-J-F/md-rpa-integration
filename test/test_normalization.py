"""
Testes de normalização.
"""

from src.transform.normalization import DataNormalizer



def test_normalize_email():


    normalizer = DataNormalizer()


    email = (

        "  TESTE@EMAIL.COM "

    )


    result = normalizer.normalize_email(
        email
    )


    assert result == "teste@email.com"



def test_normalize_phone():


    normalizer = DataNormalizer()


    phone = (

        "(82) 99999-8888"

    )


    result = normalizer.normalize_phone(
        phone
    )


    assert result == "82999998888"