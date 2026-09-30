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

def test_generate_997_with_ak3_ak4_error_loops_and_special_status():
    payload = {
        "sender_id": "SENDER",
        "receiver_id": "RECV",
        "control_number": "99",
        "acknowledged_functional_group": "PO",
        "acknowledged_group_control_number": "12",
        "acknowledgment_status": "M",  # Hits line 60 (M/W branch)
        "transaction_set_acknowledgments": [
            {
                "transaction_type": "850",
                "control_number": "0001",
                "status": "R",
                "errors": [
                    {
                        "segment_id": "BEG",
                        "segment_position": 3,
                        "error_code": "1",
                        "element_errors": [
                            {
                                "element_position": 2,
                                "error_code": "5",
                                "bad_value": "BAD_VAL"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    generator = Generator997()
    raw = generator.generate(payload)

    # Verifies AK3, AK4, and AK9 for 'M' status
    assert "AK3*BEG*3**1" in raw
    assert "AK4*2**5*BAD_VAL" in raw
    assert "AK9*M" in raw