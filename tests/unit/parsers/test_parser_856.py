import pytest
from main import app


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

def test_parse_856_ship_notice(client):
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

def test_parse_856_pack_item_structure(client):
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

def test_parse_856_non_shippable_software(client):
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