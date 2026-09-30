import pytest
from main import app


SAMPLE_EX1_ACCEPTED = "ST*997*0001~AK1*PO*11~AK9*A*3*3*3~SE*4*0001~"
SAMPLE_EX6_MAC_FAIL = "ST*997*0001~AK1*PO*11~AK9*M~SE*4*0001~"
SAMPLE_EX7_DECRYPT_FAIL = "ST*997*0001~AK1*PO*11~AK9*X*3*3*0~SE*4*0001~"

SAMPLE_CLEAN_997 = (
    "ST*997*0001~\n"
    "AK1*PO*000000001~\n"
    "AK2*850*0001~\n"
    "AK5*A~\n"
    "AK9*A*1*1*1~\n"
    "SE*6*0001~"
)

SAMPLE_REJECTED_997 = (
    "ST*997*0002~\n"
    "AK1*IN*000000002~\n"
    "AK2*810*0002~\n"
    "AK3*TDS*7**8~\n"
    "AK5*R~\n"
    "AK9*R*1*1*0~\n"
    "SE*7*0002~"
)

def test_parse_997_accepted_summary(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack.edi", SAMPLE_EX1_ACCEPTED, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "A"
    assert data["group_totals"]["accepted"] == 3


def test_parse_997_mac_failure(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack_mac.edi", SAMPLE_EX6_MAC_FAIL, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "M"
    assert data["group_totals"] == {}


def test_parse_997_decryption_failure(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack_decrypt.edi", SAMPLE_EX7_DECRYPT_FAIL, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "X"
    assert data["group_totals"]["accepted"] == 0

def test_parse_clean_997_acknowledgment(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack.edi", SAMPLE_CLEAN_997, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_type"] == "997"
    assert data["acknowledged_functional_group"] == "PO"
    assert data["acknowledgment_status"] == "A"
    assert data["acknowledgment_status_label"] == "Accepted"
    assert data["transaction_set_acknowledgments"][0]["transaction_type"] == "850"
    assert data["group_totals"]["accepted"] == 1


def test_parse_rejected_997_acknowledgment(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("reject.edi", SAMPLE_REJECTED_997, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_type"] == "997"
    assert data["acknowledgment_status"] == "R"
    assert data["acknowledgment_status_label"] == "Rejected"
    assert data["transaction_set_acknowledgments"][0]["errors"][0]["segment_id"] == "TDS"
    assert data["group_totals"]["accepted"] == 0