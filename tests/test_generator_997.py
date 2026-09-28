from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_roundtrip_997_generation():
    payload = {
        "sender_id": "TESTSENDER",
        "receiver_id": "TESTRECV",
        "control_number": "101",
        "acknowledged_functional_group": "PO",
        "acknowledged_group_control_number": "55",
        "acknowledgment_status": "A",
        "group_totals": {"included": 1, "received": 1, "accepted": 1}
    }

    # Generate outbound 997 EDI
    gen_response = client.post("/api/v1/generate/997", json=payload)
    assert gen_response.status_code == 200
    raw_edi = gen_response.text

    # Feed generated EDI back into our parser endpoint
    parse_response = client.post(
        "/api/v1/parse",
        files={"file": ("ack.edi", raw_edi, "text/plain")}
    )
    assert parse_response.status_code == 200
    parsed = parse_response.json()

    # Assert values match roundtrip
    assert parsed["sender_id"] == "TESTSENDER"
    assert parsed["receiver_id"] == "TESTRECV"
    assert parsed["acknowledged_functional_group"] == "PO"
    assert parsed["acknowledgment_status"] == "A"