import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SAMPLE_850 = (
    "ISA*00*          *00*          *ZZ*WALMART        *ZZ*MYCOMPANY      *260928*1000*U*00401*000000001*0*P*>~\n"
    "GS*PO*WALMART*MYCOMPANY*20260928*1000*1*X*004010~\n"
    "ST*850*0001~\n"
    "BEG*00*SA*PO-998231**20260928~\n"
    "N1*ST*BUFFALO DISTRO CENTER~\n"
    "N4*BUFFALO*NY*14201~\n"
    "PO1*001*500*EA*12.50**VP*WIDGET-BLUE~\n"
    "PID*F*08***BLUE INDUSTRIAL WIDGET~\n"
    "CTT*1~\n"
    "SE*8*0001~\n"
    "GE*1*1~\n"
    "IEA*1*000000001~"
)

SAMPLE_AEROSPACE_850 = (
    "ST*850*0001~BEG*00*RL*508517*1001*20000506**NA*IEL~"
    "N1*BY*ABC Aerospace Corporation*9*123456789-0101~"
    "N3*1000 BOARDWALK DRIVE~N4*SOMEWHERE*CA*98898~"
    "PO1*1*48*EA*3*PE*MG*R5656-2~IT8*******B0~CTT*1~AMT*TT*144~SE*10*0001~"
)

SAMPLE_TAX_EXEMPT_850 = (
    "ST*850*0001~BEG*00*SA*XX-1234**20170301**NA~PER*BD*ED SMITH"
    "*TE*8001234567~TAX*53247765*SP*CA*********9~N1*BY*ABC AEROSPACE"
    "*9*1234567890101~N2*AIRCRAFT DIVISION~N3*2000 JET BLVD~"
    "N4*FIGHTER TOWN*CA*98898~PO1*1*25*EA*36*PE*MG*XYZ-1234~MEA*WT"
    "*WT*10*OZ~IT8*******B0~SCH*25*EA***106*20170615~CTT*1~AMT*TT*900~"
    "SE*15*0001~"
)

def test_parse_850_purchase_order():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_850.edi", SAMPLE_850, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "850"
    assert data["po_number"] == "PO-998231"
    assert data["ship_to"]["name"] == "BUFFALO DISTRO CENTER"
    assert len(data["line_items"]) == 1
    assert data["line_items"][0]["sku"] == "WIDGET-BLUE"
    assert data["line_items"][0]["price"] == 12.50

def test_parse_tax_exempt_850():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("tax_exempt.edi", SAMPLE_TAX_EXEMPT_850, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_type"] == "850"
    assert data["po_number"] == "XX-1234"
    assert data["tax_exempt_id"] == "53247765"
    assert data["buyer_contact"]["name"] == "ED SMITH"
    assert data["buyer_contact"]["phone"] == "8001234567"
    assert data["ship_to"]["division"] == "AIRCRAFT DIVISION"
    assert data["line_items"][0]["price"] == 36.0

def test_parse_aerospace_snippet_850():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("aerospace.edi", SAMPLE_AEROSPACE_850, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "850"
    assert data["po_number"] == "508517"
    assert data["ship_to"]["name"] == "ABC Aerospace Corporation"
    assert data["ship_to"]["address1"] == "1000 BOARDWALK DRIVE"
    assert data["line_items"][0]["sku"] == "R5656-2"
    assert data["line_items"][0]["quantity"] == 48
    assert data["line_items"][0]["price"] == 3.0