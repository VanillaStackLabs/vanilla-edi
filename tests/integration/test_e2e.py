from fastapi.testclient import TestClient
from main import app  # Ensure this points to where your FastAPI 'app' is instantiated

client = TestClient(app)


def test_810_full_round_trip():
    # 1. Define the source data
    source_json = {
        "invoice_number": "INV-E2E-001",
        "sender_id": "MYCOMPANY",
        "receiver_id": "WALMART",
        "line_items": [
            {"line_number": "1", "quantity": 500, "price": 12.5, "sku": "WIDGET-BLUE"}
        ]
    }

    # Generate the EDI document
    gen_response = client.post("/api/v1/generate/810/raw", json=source_json)
    assert gen_response.status_code == 200, f"Generation failed: {gen_response.text}"
    raw_edi = gen_response.text

    # Parse the EDI document back to JSON
    files = {"file": ("test_roundtrip.edi", raw_edi, "text/plain")}
    parse_response = client.post("/api/v1/parse", files=files)
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"

    parsed_json = parse_response.json()

    # Assertions
    assert parsed_json["invoice_number"] == source_json["invoice_number"]
    assert parsed_json["sender_id"] == source_json["sender_id"]
    assert parsed_json["receiver_id"] == source_json["receiver_id"]
    assert len(parsed_json["line_items"]) == 1
    assert parsed_json["line_items"][0]["sku"] == "WIDGET-BLUE"
    assert parsed_json["line_items"][0]["quantity"] == 500
    assert float(parsed_json["line_items"][0]["unit_price"]) == 12.5