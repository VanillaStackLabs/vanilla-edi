import pytest
from datetime import datetime
from generators.invoice_810 import Invoice810Generator


@pytest.fixture
def sample_810_payload():
    return {
        "sender_id": "MYDISTRO",
        "receiver_id": "WALMART",
        "control_number": "1001",
        "invoice_number": "INV-9901",
        "invoice_date": "20260928",
        "po_number": "PO-88210",
        "po_date": "20260925",
        "remit_to": {
            "name": "ACME DISTRIBUTORS",
            "address": "123 INDUSTRIAL PKWY",
            "city": "BUFFALO",
            "state": "NY",
            "zip": "14201"
        },
        "bill_to": {
            "name": "WALMART HQ",
            "address": "702 SW 8TH ST",
            "city": "BENTONVILLE",
            "state": "AR",
            "zip": "72716"
        },
        "line_items": [
            {
                "line_number": "1",
                "quantity": 100,
                "unit_of_measure": "EA",
                "price": 10.50,
                "sku": "WIDGET-A",
                "description": "Standard Industrial Widget"
            },
            {
                "line_number": "2",
                "quantity": 50,
                "unit_of_measure": "EA",
                "price": 20.00,
                "sku": "WIDGET-B",
                "description": "Heavy Duty Widget"
            }
        ],
        "total_amount": 2050.00
    }


def test_invoice_810_generation_structure(sample_810_payload):
    generator = Invoice810Generator(element_sep="*", segment_term="~\n")
    edi_output = generator.generate(sample_810_payload)

    # Split into clean segment lines and strip any trailing segment terminators
    lines = [line.strip().rstrip("~") for line in edi_output.strip().split("~\n") if line.strip()]

    # Verify Envelope Headers
    assert lines[0].startswith("ISA*00*          *00*          *ZZ*MYDISTRO       *ZZ*WALMART        ")
    assert lines[1].startswith("GS*IN*MYDISTRO*WALMART*")

    # Verify ST Loop
    assert lines[2] == "ST*810*1001"
    assert lines[3] == "BIG*20260928*INV-9901*20260925*PO-88210"

    # Verify Address Loops
    assert "N1*RE*ACME DISTRIBUTORS" in lines
    assert "N2*123 INDUSTRIAL PKWY" in lines
    assert "N1*BT*WALMART HQ" in lines

    # Verify Line Items & Descriptions
    assert "IT1*1*100*EA*10.50**VN*WIDGET-A" in lines
    assert "PID*F****Standard Industrial Widget" in lines
    assert "IT1*2*50*EA*20.00**VN*WIDGET-B" in lines

    # Verify Totals
    # TDS value formatted in cents: 2050.00 -> 205000
    assert "TDS*205000" in lines
    assert "CTT*2" in lines

    # Verify Trailer & Segment Count
    se_line = [line for line in lines if line.startswith("SE*")][0]
    se_parts = se_line.split("*")

    st_index = lines.index("ST*810*1001")
    se_index = lines.index(se_line)
    actual_segment_count = (se_index - st_index) + 1

    assert int(se_parts[1]) == actual_segment_count
    assert se_parts[2] == "1001"

    # Verify Envelope Trailers
    assert lines[-2] == "GE*1*1001"
    assert lines[-1] == "IEA*1*000001001"


def test_invoice_810_automatic_amount_calculation():
    payload = {
        "sender_id": "TEST",
        "receiver_id": "TEST",
        "control_number": "2",
        "line_items": [
            {"line_number": "1", "quantity": 10, "price": 5.00}
        ]
    }
    generator = Invoice810Generator()
    edi_output = generator.generate(payload)

    # 10 * 5.00 = 50.00 -> 5000 cents
    assert "TDS*5000" in edi_output