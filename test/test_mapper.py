"""
Testes do Data Mapper.
"""

from src.transform.data_mapper import DataMapper



def test_map_usuario():


    mapper = DataMapper()


    usuario = {

        "nome": "Carlos",

        "email": "carlos@email.com",

        "telefone": "999999999"

    }


    result = mapper.map_usuario(
        usuario
    )


    assert result["nome"] == "Carlos"

    assert result["email"] == "carlos@email.com"

    assert result["ativo"] is True