import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_810_full_round_trip():
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
    assert float(parsed_json["line_items"][0]["price"]) == 12.5

def test_850_full_round_trip():
    source_json = {
        "po_number": "PO-E2E-999",
        "sender_id": "BUYERINC",
        "receiver_id": "SUPPLIERCO",
        "ship_to": {"name": "MAIN WAREHOUSE"},
        "line_items": [
            {"line_number": "1", "quantity": 100, "price": 45.0, "sku": "ITEM-A"}
        ]
    }

    # Generate the EDI
    gen_response = client.post("/api/v1/generate/850/raw", json=source_json)
    assert gen_response.status_code == 200

    # Parse it back
    files = {"file": ("test_850.edi", gen_response.text, "text/plain")}
    parse_response = client.post("/api/v1/parse", files=files)
    assert parse_response.status_code == 200

    parsed = parse_response.json()
    assert parsed["po_number"] == source_json["po_number"]
    assert parsed["line_items"][0]["sku"] == "ITEM-A"
    assert float(parsed["line_items"][0]["price"]) == 45.0


def test_856_full_round_trip():
    source_json = {
        "shipment_id": "ASN-E2E-777",
        "sender_id": "DISTRO",
        "receiver_id": "STORE",
        "orders": [
            {
                "po_number": "PO-12345",
                "shipped_items": [
                    {"sku": "SKU-99", "quantity": 50, "unit_of_measure": "EA"}
                ]
            }
        ]
    }

    # Generate the EDI
    gen_response = client.post("/api/v1/generate/856/raw", json=source_json)
    assert gen_response.status_code == 200

    # Parse it back
    files = {"file": ("test_856.edi", gen_response.text, "text/plain")}
    parse_response = client.post("/api/v1/parse", files=files)
    assert parse_response.status_code == 200

    parsed = parse_response.json()
    assert parsed["shipment_id"] == source_json["shipment_id"]
    assert parsed["shipped_items"][0]["sku"] == "SKU-99"
    assert parsed["shipped_items"][0]["quantity_shipped"] == 50