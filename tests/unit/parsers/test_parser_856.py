import pytest
from main import app


SAMPLE_856 = (
    "ISA*00*          *00*          *ZZ*MYCOMPANY      *ZZ*WALMART        *260928*1000*U*00401*000000003*0*P*>~\n"
    "GS*SH*MYCOMPANY*WALMART*20260928*1000*1*X*004010~\n"
    "ST*856*0001~\n"
    "BSN*00*SHIP-8849*20260928*1000~\n"
    "TD5****FDEG~\n"
    "REF*CN*1Z9999999999999999~\n"
    "REF*ZZ*IGNOREME~\n"  # Added an unknown REF to cover the fallback branch
    "LIN*1**WIDGET-BLUE~\n"
    "SN1*1*500*EA~\n"
    "SE*8*0001~\n"
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
    "REF*PLA*AUTH2~"  # Changed from empty to an actual value to cover the array append
)

SAMPLE_MEGA_856 = (
    "ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *261001*2009*U*00401*000000001*0*P*>~\n"
    "GS*SH*SENDERID*RECEIVERID*20261001*2009*1*X*004010~\n"
    "ST*856*0001~\n"
    "BSN*00*ASN123456789*20261001*2009*0001~\n"
    "HL*1**S*1~\n"
    "TD1*PLT*2****G*1500*LB~\n"
    "TD5**2*EXLA*M~\n"
    "REF*BM*BOL987654321~\n"
    "DTM*011*20261001*2009~\n"
    "N1*SH*VANILLA STACK LABS*92*12345~\n"
    "N3*123 MAIN ST~\n"
    "N4*BUFFALO*NY*14201*US~\n"
    "N1*ST*MEGA CORP ENTERPRISES*92*54321~\n"
    "N3*999 WAREHOUSE BLVD~\n"
    "N4*DALLAS*TX*75001*US~\n"
    "HL*2*1*O*1~\n"
    "PRF*PO9988776655~\n"
    "REF*IV*INV554433~\n"
    "HL*3*2*T*1~\n"
    "MAN*GM*00000123456789012345~\n"
    "HL*4*3*P*1~\n"
    "MAN*GM*00000987654321098765~\n"
    "HL*5*4*I*0~\n"
    "LIN*1*UP*123456789012*VN*VSL-998~\n"
    "SN1**100*EA~\n"
    "PID*F****WIDGET SUPREME~\n"
    "HL*6*4*I*0~\n"
    "LIN*2*UP*123456789099*VN*VSL-999~\n"
    "SN1**50*EA~\n"
    "PID*F****GIZMO MAX~\n"
    "CTT*6~\n"
    "SE*30*0001~\n"
    "GE*1*1~\n"
    "IEA*1*000000001~"
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


def test_parse_856_pack_item_structure(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("test_856.edi", SAMPLE_PACK_ITEM_856, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    hierarchy = data.get("hierarchy", {})

    assert data["transaction_type"] == "856"
    assert data["shipment_id"] == "020609336001"

    # Traverse the hierarchy: Shipment(1) -> Order(2) -> Pack(3) -> Item(4)
    order_node = hierarchy.get("children", [])[0]
    pack_node_1 = order_node.get("children", [])[0]

    assert "cartons" in pack_node_1["details"]
    assert pack_node_1["details"]["cartons"][0]["sscc_18"] == "850440000000000021"

    item_node_1 = pack_node_1.get("children", [])[0]
    assert item_node_1["details"]["item"]["sku"] == "5597676"
    assert item_node_1["details"]["item"]["quantity_shipped"] == 2


def test_parse_856_non_shippable_software(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("software_856.edi", SAMPLE_NON_SHIPPABLE_856, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    hierarchy = data.get("hierarchy", {})

    assert data["transaction_type"] == "856"
    assert data["shipment_id"] == "020609336001"

    # Traverse the hierarchy: Shipment(1) -> Order(2) -> Item(3)
    order_node = hierarchy.get("children", [])[0]
    item_node = order_node.get("children", [])[0]

    assert "cartons" not in item_node["details"]
    assert item_node["details"]["item"]["vendor_part"] == "VENDSWL"
    assert item_node["details"]["item"]["quantity_shipped"] == 1


def test_parse_856_mega_structure(client):
    response = client.post(
        "/api/v1/parse",
        files={"file": ("mega_856.edi", SAMPLE_MEGA_856, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()

    # 1. Verify top-level extraction
    assert data["shipment_id"] == "ASN123456789"
    assert data["carrier_code"] == "EXLA"

    hierarchy = data.get("hierarchy", {})

    # Verify Level 1: Shipment
    assert hierarchy["level_code"] == "S"

    # Verify Level 2: Order
    order_node = hierarchy["children"][0]
    assert order_node["level_code"] == "O"
    assert order_node["details"]["po_number"] == "PO9988776655"

    # Verify Level 3: Tare (Pallet)
    tare_node = order_node["children"][0]
    assert tare_node["level_code"] == "T"
    assert tare_node["details"]["cartons"][0]["sscc_18"] == "00000123456789012345"

    # Verify Level 4: Pack (Carton)
    pack_node = tare_node["children"][0]
    assert pack_node["level_code"] == "P"
    assert pack_node["details"]["cartons"][0]["sscc_18"] == "00000987654321098765"

    #  Verify Level 5: Items (Ensuring both items are nested inside the Pack)
    items = pack_node["children"]
    assert len(items) == 2

    # First Item
    assert items[0]["level_code"] == "I"
    assert items[0]["details"]["item"]["sku"] == "123456789012"
    assert items[0]["details"]["item"]["quantity_shipped"] == 100

    # Second Item
    assert items[1]["level_code"] == "I"
    assert items[1]["details"]["item"]["sku"] == "123456789099"
    assert items[1]["details"]["item"]["quantity_shipped"] == 50