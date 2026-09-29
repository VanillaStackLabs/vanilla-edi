from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_parse_edi_exception_handling():
    """Forces a decoding exception by sending invalid bytes."""
    response = client.post(
        "/api/v1/parse",
        files={"file": ("bad.edi", b"\xff\xfe\xfd", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Failed to parse EDI payload" in response.json()["detail"]

def test_parse_edi_with_webhook():
    """Verifies that providing a webhook_url triggers background dispatching."""
    sample_edi = "ST*850*0001~\nBEG*00*SA*PO-123**20260928~\nSE*3*0001~"
    webhook_target = "https://internal-erp.local/api/edi-inbound"

    with patch("routers.parse.dispatch_webhook") as mock_dispatch:
        response = client.post(
            "/api/v1/parse",
            files={"file": ("test.edi", sample_edi, "text/plain")},
            data={"webhook_url": webhook_target}
        )

        assert response.status_code == 200
        mock_dispatch.assert_called_once()

        args, _ = mock_dispatch.call_args
        assert args[0] == webhook_target
        assert args[1]["transaction_type"] == "850"
        assert args[1]["po_number"] == "PO-123"


def test_parse_stream_endpoint():
    """Verifies the streaming endpoint correctly yields JSON-Lines."""
    edi_text = (
        "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260929*1000*U*00401*000000001*0*P*>~\n"
        "ST*850*0001~\n"
        "SE*2*0001~"
    )

    response = client.post(
        "/api/v1/parse/stream",
        files={"file": ("test_stream.edi", edi_text, "text/plain")}
    )

    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers["content-type"]

    # Split the response text by line to verify the chunks
    lines = response.text.strip().split("\n")
    assert len(lines) == 3
    assert '{"event": "transaction_start", "type": "850"}' in lines[1]
    assert '{"event": "transaction_end"}' in lines[2]