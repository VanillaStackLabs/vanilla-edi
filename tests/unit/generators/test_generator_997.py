from generators.ack_997 import Generator997
from main import app

def test_roundtrip_997_generation(client):
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


def test_generate_997_with_rejected_ak2_loop(client):
    payload = {
        "sender_id": "TESTSENDER",
        "receiver_id": "TESTRECV",
        "control_number": "101",
        "acknowledged_functional_group": "PO",
        "acknowledged_group_control_number": "55",
        "acknowledgment_status": "R",
        "transaction_set_acknowledgments": [
            {
                "transaction_set_control_number": "0001",
                "status": "R",
                "error_code": "5"
            }
        ],
        "group_totals": {"included": 1, "received": 1, "accepted": 0}
    }

    generator = Generator997()
    raw_x12 = generator.generate(payload)

    assert "AK2" in raw_x12
    assert "AK5*R*5" in raw_x12