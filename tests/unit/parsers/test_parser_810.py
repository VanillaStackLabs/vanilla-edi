import pytest
from main import app


SAMPLE_810 = (
    "ISA*00*          *00*          *ZZ*MYCOMPANY      *ZZ*WALMART        *260928*1000*U*00401*000000002*0*P*>~\n"
    "GS*IN*MYCOMPANY*WALMART*20260928*1000*1*X*004010~\n"
    "ST*810*0001~\n"
    "BIG*20260928*INV-10049*20260928*PO-998231~\n"
    "N1*RE*ACME PAYMENTS LLC~\n"
    "IT1*001*500*EA*12.50**VP*WIDGET-BLUE~\n"
    "TDS*625000~\n"
    "SE*6*0001~\n"
    "GE*1*1~\n"
    "IEA*1*000000002~"
)

SAMPLE_AEROSPACE_810 = (
    "ST*810*0001~\n"
    "BIG*20000513*SG427254*20000506*508517*1001~\n"
    "N1*ST*ABC AEROSPACE CORPORATION*9*123456789-0101~\n"
    "N3*1000 BOARDWALK DRIVE~\n"
    "N4*SOMEWHERE*CA*98898~\n"
    "ITD*05*3*****30*******E~\n"
    "IT1*1*48*EA*3**MG*R5656-2~\n"
    "TDS*14400~\n"
    "CTT*1~\n"
    "SE*10*0001~"
)

SAMPLE_CREDIT_CARD_810 = (
    "ST*810*0001~\n"
    "BIG*20000513*39876980601170600*20000506*767124*6543214666601234**CI*00~\n"
    "N1*RI*US BANK*92*290448~\n"
    "ITD*05*3*****14~\n"
    "IT1*1*1*EA*170.6**VX*654321234002345~\n"
    "TDS*17060~\n"
    "CTT*1~\n"
    "SE*8*0001~"
)

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
    assert data["line_items"][0]["unit_price"] == 3.0

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