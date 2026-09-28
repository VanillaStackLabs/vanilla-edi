from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    # Verifies the root health check endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "message": "VanillaEDI server is running."}


def test_generate_997_endpoint():
    # Tests the outbound 997 generation using default schema values
    payload = {
        "sender_id": "TESTSENDER",
        "receiver_id": "TESTRECEIVER",
        "control_number": "123456789",
        "acknowledged_functional_group": "PO",
        "acknowledged_group_control_number": "99",
        "acknowledgment_status": "A"
    }
    response = client.post("/api/v1/generate/997", json=payload)

    assert response.status_code == 200
    # Verifies the response uses the plain text media type
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "TESTSENDER" in response.text
    assert "AK1*PO*99~" in response.text


def test_parse_edi_exception_handling():
    # Forces a decoding exception by sending invalid UTF-8 bytes
    response = client.post(
        "/api/v1/parse",
        files={"file": ("bad.edi", b"\xff\xfe\xfd", "application/octet-stream")}
    )
    # The endpoint should catch the failure and return a 400 HTTP exception
    assert response.status_code == 400
    assert "Failed to parse EDI payload" in response.json()["detail"]


def test_parse_edi_with_webhook():
    sample_edi = "ST*850*0001~\nBEG*00*SA*PO-123**20260928~\nSE*3*0001~"
    webhook_target = "https://internal-erp.local/api/edi-inbound"

    # We patch the webhook function inside main.py so we don't fire real HTTP requests during testing
    with patch("main.dispatch_webhook") as mock_dispatch:
        response = client.post(
            "/api/v1/parse",
            files={"file": ("test.edi", sample_edi, "text/plain")},
            data={"webhook_url": webhook_target}  # Send the URL as form data
        )

        assert response.status_code == 200

        mock_dispatch.assert_called_once()

        args, kwargs = mock_dispatch.call_args
        assert args[0] == webhook_target
        # Verify the parsed JSON payload (args[1]) contains our transaction data
        assert args[1]["transaction_type"] == "850"
        assert args[1]["po_number"] == "PO-123"