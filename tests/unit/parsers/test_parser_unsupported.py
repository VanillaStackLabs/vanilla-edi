import pytest
from main import app


def test_unsupported_transaction(client):
    unsupported_edi = "ISA*...~\nST*999*0001~\nSE*2*0001~\nIEA*1*000000001~"
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_unsupported.edi", unsupported_edi, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "999"
    assert data["status"] == "unsupported_transaction_set"



