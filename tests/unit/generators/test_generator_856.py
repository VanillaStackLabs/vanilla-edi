import pytest
from generators.asn_856 import ASN856Generator


@pytest.fixture
def sample_856_payload():
    return {
        "sender_id": "MYDISTRO",
        "receiver_id": "WALMART",
        "control_number": "5001",
        "shipment_id": "SH-99201",
        "ship_date": "20260928",
        "ship_time": "1430",
        "carrier_code": "FDEG",
        "tracking_number": "TRK987654321",
        "ship_from": {"name": "DISTRIBUTION CENTER 1"},
        "ship_to": {"name": "WALMART STORE 100"},
        "orders": [
            {
                "po_number": "PO-88210",
                "items": [
                    {"sku": "WIDGET-A", "quantity": 100, "unit_of_measure": "EA"},
                    {"sku": "WIDGET-B", "quantity": 50, "unit_of_measure": "EA"}
                ]
            }
        ]
    }


def test_asn_856_generation_structure(sample_856_payload):
    generator = ASN856Generator(element_sep="*", segment_term="~\n")
    edi_output = generator.generate(sample_856_payload)

    # Split into clean segment lines and strip trailing tildes
    lines = [line.strip().rstrip("~") for line in edi_output.strip().split("~\n") if line.strip()]

    # Envelope verification
    assert lines[0].startswith("ISA*00*          *00*          *ZZ*MYDISTRO       *ZZ*WALMART        ")
    assert lines[1].startswith("GS*SH*MYDISTRO*WALMART*")

    # ST & BSN Header
    assert lines[2] == "ST*856*5001"
    assert lines[3] == "BSN*00*SH-99201*20260928*1430"

    # HL Level 1: Shipment
    assert lines[4] == "HL*1**S"
    assert "TD5*B*2*FDEG" in lines
    assert "REF*CN*TRK987654321" in lines
    assert "N1*SF*DISTRIBUTION CENTER 1" in lines
    assert "N1*ST*WALMART STORE 100" in lines

    # HL Level 2: Order (Parent is HL 1)
    assert "HL*2*1*O" in lines
    assert "PRF*PO-88210" in lines

    # HL Level 3: Items (Parent is HL 2)
    assert "HL*3*2*I" in lines
    assert "LIN**VN*WIDGET-A" in lines
    assert "SN1**100*EA" in lines

    assert "HL*4*2*I" in lines
    assert "LIN**VN*WIDGET-B" in lines
    assert "SN1**50*EA" in lines

    # CTT should reflect total HL loops (4 in this case)
    assert "CTT*4" in lines

    # Verify SE Trailer Segment Count
    se_line = [line for line in lines if line.startswith("SE*")][0]
    se_parts = se_line.split("*")

    st_index = lines.index("ST*856*5001")
    se_index = lines.index(se_line)
    actual_segment_count = (se_index - st_index) + 1

    assert int(se_parts[1]) == actual_segment_count
    assert se_parts[2] == "5001"


def test_asn_856_minimal_payload_branch_coverage():
    # Omits tracking_number, ship_from, and ship_to to test skipped branches
    minimal_payload = {
        "control_number": "999",
        "orders": [
            {
                "po_number": "PO-123",
                "items": [
                    {"sku": "TEST-SKU", "quantity": 1}
                ]
            }
        ]
    }
    generator = ASN856Generator(element_sep="*", segment_term="~\n")
    edi_output = generator.generate(minimal_payload)

    assert "ST*856*0999" in edi_output
    assert "REF*CN*" not in edi_output  # No tracking
    assert "N1*SF*" not in edi_output  # No Ship From
    assert "N1*ST*" not in edi_output  # No Ship To
    assert "LIN**VN*TEST-SKU" in edi_output

def test_asn_856_tare_pack_item_hierarchy():
    # Tests the S -> O -> T -> P -> I structure (Palletized)
    payload = {
        "control_number": "1000",
        "orders": [{
            "po_number": "PO-TARE",
            "tares": [{
                "pallets": [{"sscc": "PALLET123"}],
                "packs": [{
                    "cartons": [{"sscc": "CARTON456"}],
                    "items": [{"sku": "SKU-TPI", "quantity": 10}]
                }]
            }]
        }]
    }
    generator = ASN856Generator(element_sep="*", segment_term="~\n")
    output = generator.generate(payload)
    lines = [line.strip().rstrip("~") for line in output.strip().split("~\n") if line.strip()]

    # Verify hierarchical sequence: S(1) -> O(2) -> T(3) -> P(4) -> I(5)
    assert "HL*1**S" in lines
    assert "HL*2*1*O" in lines
    assert "HL*3*2*T" in lines
    assert "MAN*GM*PALLET123" in lines  # Pallet barcode
    assert "HL*4*3*P" in lines
    assert "MAN*GM*CARTON456" in lines  # Carton barcode
    assert "HL*5*4*I" in lines
    assert "LIN**VN*SKU-TPI" in lines
    assert "CTT*5" in lines


def test_asn_856_pack_item_hierarchy():
    # Tests the S -> O -> P -> I structure (Cartonized, no Pallet)
    payload = {
        "control_number": "1001",
        "orders": [{
            "po_number": "PO-PACK",
            "packs": [{
                "cartons": [{"tracking": "CARTON789"}], # Tests the tracking fallback key
                "items": [{"sku": "SKU-PI", "quantity": 20}]
            }]
        }]
    }
    generator = ASN856Generator(element_sep="*", segment_term="~\n")
    output = generator.generate(payload)
    lines = [line.strip().rstrip("~") for line in output.strip().split("~\n") if line.strip()]

    # Verify hierarchical sequence: S(1) -> O(2) -> P(3) -> I(4)
    assert "HL*1**S" in lines
    assert "HL*2*1*O" in lines
    assert "HL*3*2*P" in lines
    assert "MAN*GM*CARTON789" in lines  # Tracking fallback mapped to MAN
    assert "HL*4*3*I" in lines
    assert "LIN**VN*SKU-PI" in lines
    assert "CTT*4" in lines