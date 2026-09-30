import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_transaction_schema_endpoint():
    response = client.get("/api/v1/schemas/810")
    assert response.status_code == 200
    assert "properties" in response.json()

def test_get_transaction_schema_not_found():
    response = client.get("/api/v1/schemas/9999")
    assert response.status_code == 404