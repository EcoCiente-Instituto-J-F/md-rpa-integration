"""
Teste de reconciliação.
"""

from src.audit.reconciliation import Reconciliation



def test_reconciliation_result():


    result = {


        "source_count":100,


        "target_count":100,


        "difference":0,


        "status":"OK"

    }



    assert result["difference"] == 0

    assert result["status"] == "OK"