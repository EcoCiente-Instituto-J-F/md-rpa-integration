"""
Testes da etapa Extract.
"""

from unittest.mock import Mock

from src.extract.extract_service import ExtractService



def test_extract_table():

    service = ExtractService()


    service.connector = Mock()


    service.connector.execute_query.return_value = [

        {
            "id_usuario": 1,
            "nome": "Joao"
        }

    ]


    result = service.extract_table(
        "SELECT * FROM usuario"
    )


    assert len(result) == 1

    assert result[0]["nome"] == "Joao"