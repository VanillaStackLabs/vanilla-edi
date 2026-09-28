import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Sample EDI Payloads
SAMPLE_EX1_ACCEPTED = "ST*997*0001~AK1*PO*11~AK9*A*3*3*3~SE*4*0001~"
SAMPLE_EX6_MAC_FAIL = "ST*997*0001~AK1*PO*11~AK9*M~SE*4*0001~"
SAMPLE_EX7_DECRYPT_FAIL = "ST*997*0001~AK1*PO*11~AK9*X*3*3*0~SE*4*0001~"

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

SAMPLE_856 = (
    "ISA*00*          *00*          *ZZ*MYCOMPANY      *ZZ*WALMART        *260928*1000*U*00401*000000003*0*P*>~\n"
    "GS*SH*MYCOMPANY*WALMART*20260928*1000*1*X*004010~\n"
    "ST*856*0001~\n"
    "BSN*00*SHIP-8849*20260928*1000~\n"
    "TD5****FDEG~\n"
    "REF*CN*1Z9999999999999999~\n"
    "LIN*1**WIDGET-BLUE~\n"
    "SN1*1*500*EA~\n"
    "SE*7*0001~\n"
    "GE*1*1~\n"
    "IEA*1*000000003~"
)

SAMPLE_PACK_ITEM_856 = (
    "BSN*00*020609336001*20060425*2210*0001~\n"
    "DTM*011*20060425*1015*ET~\n"
    "HL*1**S~\n"
    "TD5**2*FDE**FedEx Ground*******CG~\n"
    "N1*SF*VENDOR NAME~\n"
    "N2*ADDITIONAL NAME~\n"
    "N3*VENDOR STREET ADDRESS1*VENDOR STREET ADDRESS2~\n"
    "N4*CITY*ST*10011*USA~\n"
    "N1*ST*INSIGHT CUSTOMER NAME*92*0000123456~\n"
    "N2*ADDITIONAL NAME~\n"
    "N3*INSIGHT CUSTOMER STREET ADDRESS~\n"
    "N4*CITY*ST*10011*USA~\n"
    "HL*2*1*O~\n"
    "PRF*4999999***20060513***DS~\n"
    "HL*3*2*P~\n"
    "PO4**4*EA**G*20*LB***24*48*60*IN~\n"
    "REF*2I*12345678~\n"
    "MAN*GM*850440000000000021~\n"
    "HL*4*3*I~\n"
    "LIN*00001*BP*5597676*VP*PY993UA#ABA~\n"
    "SN1**2*EA~\n"
    "REF*SE*211UA6140H4V~\n"
    "REF*SE*212UA6140H4V~\n"
    "HL*5*3*I~\n"
    "LIN*00002*BP*5022945*VP*PF803AA#ABA~\n"
    "SN1**2*EA~\n"
    "REF*SE*211CNC6092C8S~\n"
    "REF*SE*212CNC6092C8S~\n"
    "HL*6*2*P~\n"
    "PO4**2*EA**G*10*LB***12*24*30*IN~\n"
    "REF*2I*12345678~\n"
    "MAN*GM*850440000000000022~\n"
    "HL*7*6*I~\n"
    "LIN*00001*BP*5597676*VP*PY993UA#ABA~\n"
    "SN1**1*EA~\n"
    "REF*SE*2212UA6140H4W~\n"
    "HL*8*6*I~\n"
    "LIN*00002*BP*5022945*VP*PF803AA#ABA~\n"
    "SN1**1*EA~\n"
    "REF*SE*221CNC6092C8T~\n"
    "CTT*4~"
)

SAMPLE_NON_SHIPPABLE_856 = (
    "BSN*00*020609336001*20060425*2210*0001~\n"
    "DTM*011*20060425*1015*ET~\n"
    "HL*1**S~\n"
    "TD5************ZZ~\n"
    "N1*SF*VENDOR NAME~\n"
    "N2*ADDITIONAL NAME~\n"
    "N3*VENDOR STREET ADDRESS1*VENDOR STREET ADDRESS2~\n"
    "N4*CITY*ST*10011*USA~\n"
    "N1*ST*INSIGHT CUSTOMER NAME*92*0000123456~\n"
    "N2*ADDITIONAL NAME~\n"
    "N3*INSIGHT CUSTOMER STREET ADDRESS~\n"
    "N4*CITY*ST*10011*USA~\n"
    "HL*2*1*O~\n"
    "PRF*6999999***20060513***DS~\n"
    "HL*3*2*I~\n"
    "LIN*00001*BP*555SWL`*VP*VENDSWL~\n"
    "SN1**1*EA~\n"
    "REF*BB*AUTH1~\n"
    "REF*PLA*~"
)

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

# Test Cases
def test_parse_997_accepted_summary():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack.edi", SAMPLE_EX1_ACCEPTED, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "A"
    assert data["group_totals"]["accepted"] == 3


def test_parse_997_mac_failure():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack_mac.edi", SAMPLE_EX6_MAC_FAIL, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "M"
    assert data["group_totals"] == {}


def test_parse_997_decryption_failure():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("ack_decrypt.edi", SAMPLE_EX7_DECRYPT_FAIL, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["acknowledgment_status"] == "X"
    assert data["group_totals"]["accepted"] == 0

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

def test_parse_810_invoice():
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

def test_parse_aerospace_810_invoice():
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

def test_parse_credit_card_810_invoice():
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

def test_parse_856_ship_notice():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_856.edi", SAMPLE_856, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "856"
    assert data["shipment_id"] == "SHIP-8849"
    assert data["tracking_number"] == "1Z9999999999999999"
    assert data["shipped_items"][0]["quantity_shipped"] == 500

def test_parse_856_pack_item_structure():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_856.edi", SAMPLE_PACK_ITEM_856, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_type"] == "856"
    assert data["shipment_id"] == "020609336001"
    assert len(data["cartons"]) == 2
    assert data["cartons"][0]["sscc_18"] == "850440000000000021"
    assert len(data["shipped_items"]) == 4
    assert "211UA6140H4V" in data["shipped_items"][0]["serial_numbers"]

def test_parse_856_non_shippable_software():
    response = client.post(
        "/api/v1/parse",
        files={"file": ("software_856.edi", SAMPLE_NON_SHIPPABLE_856, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_type"] == "856"
    assert data["shipment_id"] == "020609336001"
    assert len(data["cartons"]) == 0
    assert len(data["shipped_items"]) == 1
    assert data["shipped_items"][0]["vendor_part"] == "VENDSWL"
    assert data["shipped_items"][0]["quantity_shipped"] == 1

def test_unsupported_transaction():
    unsupported_edi = "ISA*...~\nST*999*0001~\nSE*2*0001~\nIEA*1*000000001~"
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_unsupported.edi", unsupported_edi, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_type"] == "999"
    assert data["status"] == "unsupported_transaction_set"

def test_parse_clean_997_acknowledgment():
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


def test_parse_rejected_997_acknowledgment():
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

