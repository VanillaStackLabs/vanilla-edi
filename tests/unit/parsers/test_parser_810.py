import pytest
from main import app

# Standard envelopes required by stream.py validation
ENV_HEAD = (
    "ISA*00*          *00*          *ZZ*MYCOMPANY      *ZZ*WALMART        *260928*1000*U*00401*000000002*0*P*>~\n"
    "GS*IN*MYCOMPANY*WALMART*20260928*1000*1*X*004010~\n"
)
ENV_TAIL = "GE*1*1~\nIEA*1*000000002~"

SAMPLE_810 = ENV_HEAD + (
    "ST*810*0001~\n"
    "BIG*20260928*INV-10049*20260928*PO-998231~\n"
    "N1*RE*ACME PAYMENTS LLC~\n"
    "IT1*001*500*EA*12.50**VP*WIDGET-BLUE~\n"
    "TDS*625000~\n"
    "SE*6*0001~\n"
) + ENV_TAIL

SAMPLE_AEROSPACE_810 = ENV_HEAD + (
    "ST*810*0001~\n"
    "BIG*20000513*SG427254*20000506*508517*1001~\n"
    "N1*ST*ABC AEROSPACE CORPORATION*9*123456789-0101~\n"
    "N3*1000 BOARDWALK DRIVE~\n"
    "N4*SOMEWHERE*CA*98898~\n"
    "ITD*05*3*****30*******E~\n"
    "IT1*1*48*EA*3**MG*R5656-2~\n"
    "TDS*14400~\n"
    "CTT*1~\n"
    "SE*10*0001~\n"
) + ENV_TAIL

SAMPLE_CREDIT_CARD_810 = ENV_HEAD + (
    "ST*810*0001~\n"
    "BIG*20000513*39876980601170600*20000506*767124*6543214666601234**CI*00~\n"
    "N1*RI*US BANK*92*290448~\n"
    "ITD*05*3*****14~\n"
    "IT1*1*1*EA*170.6**VX*654321234002345~\n"
    "TDS*17060~\n"
    "CTT*1~\n"
    "SE*8*0001~\n"
) + ENV_TAIL

SAMPLE_UNKNOWN_N1_810 = ENV_HEAD + (
    "ST*810*0001~\n"
    "BIG*20260928*INV-UNKNOWN*20260928*PO-123~\n"
    "N1*ZZ*SOME OTHER ENTITY~\n"
    "IT1*1*1*EA*10**VP*SKU~\n"
    "TDS*1000~\n"
    "SE*6*0001~\n"
) + ENV_TAIL

SAMPLE_COMPLETE_810 = ENV_HEAD + (
    "ST*810*0001~\n"
    "BIG*20261001*INV-100%*20261001*PO-777~\n"
    "ITD~\n"  # Triggers empty ITD bounds fallback
    "N1*BT*BILLING DEPT CORP~\n"  # Hits bill_to block
    "N3*100 MAIN ST~\n"
    "N4*BUFFALO*NY*14202~\n"
    "IT1*1*10*EA*5.00**VP*SKU123~\n"
    "PID*F****WIDGET DESCRIPTION HERE~\n"  # Hits PID block
    "TDS*5000~\n"
    "SE*9*0001~\n"
) + ENV_TAIL


def test_parse_810_invoice(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_810.edi", SAMPLE_810, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "810"
    assert data["invoice_number"] == "INV-10049"
    assert data["po_number"] == "PO-998231"
    assert data["total_amount"] == 6250.00
    assert data["remit_to"]["name"] == "ACME PAYMENTS LLC"


def test_parse_aerospace_810_invoice(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("invoice.edi", SAMPLE_AEROSPACE_810, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "810"
    assert data["invoice_number"] == "SG427254"
    assert data["po_number"] == "508517"
    assert data["release_number"] == "1001"
    assert data["total_amount"] == 144.0
    assert data["payment_terms"]["net_days"] == 30
    assert data["ship_to"]["name"] == "ABC AEROSPACE CORPORATION"
    assert data["line_items"][0]["price"] == 3.0  # Fixed from unit_price


def test_parse_credit_card_810_invoice(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("cc_invoice.edi", SAMPLE_CREDIT_CARD_810, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "810"
    assert data["invoice_number"] == "39876980601170600"
    assert data["remit_to"]["name"] == "US BANK"
    assert data["payment_terms"]["net_days"] == 14
    assert data["total_amount"] == 170.60


def test_parse_810_unknown_n1_entity(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("unknown_n1.edi", SAMPLE_UNKNOWN_N1_810, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()

    # Proves the N1*ZZ segment was gracefully skipped
    assert data["invoice_number"] == "INV-UNKNOWN"
    assert data.get("remit_to") == {}
    assert data.get("ship_to") == {}

def test_parse_810_bill_to_and_pid_coverage(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("full_coverage.edi", SAMPLE_COMPLETE_810, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bill_to"]["name"] == "BILLING DEPT CORP"
    assert data["bill_to"]["address"] == "100 MAIN ST"
    assert data["line_items"][0]["description"] == "WIDGET DESCRIPTION HERE"