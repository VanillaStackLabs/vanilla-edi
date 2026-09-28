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
                "shipped_items": [
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