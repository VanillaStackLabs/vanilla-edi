import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_full_round_trip():
    print("[INFO] Starting VanillaEDI End-to-End Test...")

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
    print("[INFO] POST /generate/810/raw...")
    gen_response = requests.post(f"{BASE_URL}/generate/810/raw", json=source_json)
    assert gen_response.status_code == 200, f"Generation failed: {gen_response.text}"

    raw_edi = gen_response.text
    print("[SUCCESS] Generated raw EDI.")

    # Parse the EDI document back to JSON
    print("[INFO] POST /parse...")
    files = {"file": ("e2e_test.edi", raw_edi, "text/plain")}
    parse_response = requests.post(f"{BASE_URL}/parse", files=files)
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"

    # Verify the data matches
    parsed_json = parse_response.json()
    assert parsed_json["invoice_number"] == source_json["invoice_number"]
    assert parsed_json["sender_id"] == source_json["sender_id"]

    print("[SUCCESS] Parsed EDI back to JSON.")
    print("[SUCCESS] Round-trip E2E test completed without errors.")


if __name__ == "__main__":
    test_full_round_trip()