import pytest
from generators.po_850 import PO850Generator


@pytest.fixture
def sample_850_payload():
    return {
        "sender_id": "BUYERINC",
        "receiver_id": "SUPPLIERCO",
        "control_number": "3001",
        "po_number": "PO-99100",
        "po_date": "20260928",
        "requested_delivery_date": "20261015",
        "ship_to": {
            "name": "MAIN WAREHOUSE",
            "address": "500 SUPPLY CHAIN WAY",
            "city": "CHICAGO",
            "state": "IL",
            "zip": "60601",
        },
        "bill_to": {
            "name": "ACCOUNTS PAYABLE",
        },
        "line_items": [
            {
                "line_number": "1",
                "quantity": 200,
                "unit_of_measure": "EA",
                "price": 15.00,
                "sku": "ITEM-RED",
                "description": "Red Industrial Component",
            },
            {
                "line_number": "2",
                "quantity": 50,
                "unit_of_measure": "EA",
                "price": 40.00,
                "sku": "ITEM-BLUE",
                "description": "Blue Heavy Component",
            },
        ],
        "total_amount": 5000.00,
    }


def test_po_850_generation_structure(sample_850_payload):
    generator = PO850Generator(element_sep="*", segment_term="~\n")
    edi_output = generator.generate(sample_850_payload)

    # Split into clean segment lines and strip trailing segment terminators
    lines = [
        line.strip().rstrip("~")
        for line in edi_output.strip().split("~\n")
        if line.strip()
    ]

    # Verify Envelope Headers
    assert lines[0].startswith(
        "ISA*00*          *00*          *ZZ*BUYERINC       *ZZ*SUPPLIERCO     "
    )
    assert lines[1].startswith("GS*PO*BUYERINC*SUPPLIERCO*")

    # Verify ST & BEG
    assert lines[2] == "ST*850*3001"
    assert lines[3] == "BEG*00*SA*PO-99100**20260928"
    assert "DTM*002*20261015" in lines

    # Verify N1 Loops
    assert "N1*ST*MAIN WAREHOUSE" in lines
    assert "N3*500 SUPPLY CHAIN WAY" in lines
    assert "N4*CHICAGO*IL*60601" in lines
    assert "N1*BT*ACCOUNTS PAYABLE" in lines

    # Verify Line Items & Descriptions Dynamically (Bypassing exact currency trailing zero matches)
    po_line_1 = next(line for line in lines if line.startswith("PO1*1*200*EA*"))
    assert "VN*ITEM-RED" in po_line_1
    assert "PID*F****Red Industrial Component" in lines

    po_line_2 = next(line for line in lines if line.startswith("PO1*2*50*EA*"))
    assert "VN*ITEM-BLUE" in po_line_2

    # Verify Totals
    assert "CTT*2" in lines
    amt_line = next(line for line in lines if line.startswith("AMT*TT*"))
    assert len(amt_line) > 7

    # Verify SE Trailer Segment Count
    se_line = [line for line in lines if line.startswith("SE*")][0]
    se_parts = se_line.split("*")

    st_index = lines.index("ST*850*3001")
    se_index = lines.index(se_line)
    actual_segment_count = (se_index - st_index) + 1

    assert int(se_parts[1]) == actual_segment_count
    assert se_parts[2] == "3001"


def test_po_850_minimal_payload_branch_coverage():
    # Omits optional fields like delivery_date, ship_to, bill_to, and description
    # This forces the generator to skip the N1, N3, N4, and PID loops.
    minimal_payload = {
        "control_number": "999",
        "line_items": [
            {"price": 10.00}
        ]
    }
    generator = PO850Generator(element_sep="*", segment_term="~\n")
    edi_output = generator.generate(minimal_payload)

    assert "ST*850*0999" in edi_output
    assert "DTM*002" not in edi_output
    assert "N1" not in edi_output
    assert "PID" not in edi_output
    assert "AMT*TT*10" in edi_output


def test_po_850_partial_ship_to_branch():
    # Provides ship_to but omits address/city/state/zip to hit the N3/N4 false branches
    payload = {
        "ship_to": {"name": "JUST A NAME"}
    }
    generator = PO850Generator()
    edi_output = generator.generate(payload)

    assert "N1*ST*JUST A NAME" in edi_output
    assert "N3*" not in edi_output
    assert "N4*" not in edi_output