"""
Testes da etapa Load.
"""

from unittest.mock import Mock

from src.load.insert_service import InsertService



def test_insert_usuario():


    mapper = Mock()


    service = InsertService(
        mapper
    )


    session = Mock()


    session.execute.return_value.fetchone.return_value = [

        100

    ]


    usuario = {


        "nome":
        "Maria",


        "email":
        "maria@email.com"

    }



    result = service.insert(

        "usuario",

        usuario,

        session

    )


    assert result == 100