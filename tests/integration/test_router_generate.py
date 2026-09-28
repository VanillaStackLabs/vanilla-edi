import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --- 997 Endpoint Tests ---
def test_generate_997_endpoint():
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
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "TESTSENDER" in response.text
    assert "AK1*PO*99~" in response.text

# --- 810 Endpoint Tests ---
def test_api_generate_810_success(sample_810_payload):
    response = client.post("/api/v1/generate/810", json=sample_810_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "BIG*20260928*INV-9901*20260925*PO-88210" in data["edi_content"]
    assert "TDS*205000" in data["edi_content"]

def test_api_generate_810_raw(sample_810_payload):
    response = client.post("/api/v1/generate/810/raw", json=sample_810_payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "ST*810*1001" in response.text

# --- 856 Endpoint Tests ---
def test_api_generate_856_success(sample_856_payload):
    response = client.post("/api/v1/generate/856", json=sample_856_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "BSN*00*SH-99201*20260928*1430" in data["edi_content"]
    assert "HL*1**S" in data["edi_content"]

def test_api_generate_856_raw(sample_856_payload):
    response = client.post("/api/v1/generate/856/raw", json=sample_856_payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "ST*856*5001" in response.text

# --- 850 Endpoint Tests ---
def test_api_generate_850_success(sample_850_payload):
    response = client.post("/api/v1/generate/850", json=sample_850_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "BEG*00*SA*PO-99100**20260928" in data["edi_content"]

def test_api_generate_850_raw(sample_850_payload):
    response = client.post("/api/v1/generate/850/raw", json=sample_850_payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "ST*850*1001" in response.text
    assert "AMT*TT*1150" in response.text