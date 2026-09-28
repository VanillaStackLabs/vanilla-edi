import pytest

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
            "address": "123 INDUSTRIAL PKWY"
        },
        "bill_to": {
            "name": "WALMART HQ"
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
                "sku": "WIDGET-B"
            }
        ],
        "total_amount": 2050.00
    }

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

@pytest.fixture
def sample_850_payload():
    return {
        "sender_id": "BUYERCO",
        "receiver_id": "VENDORCO",
        "control_number": "1001",
        "po_number": "PO-99100",
        "po_date": "20260928",
        "requested_delivery_date": "20261005",
        "ship_to": {"name": "WAREHOUSE A", "address": "55 SUPPLY RD", "city": "DALLAS", "state": "TX", "zip": "75201"},
        "line_items": [
            {"line_number": "1", "quantity": 50, "unit_of_measure": "EA", "price": 12.00, "sku": "ITEM-X", "description": "Widget Type X"},
            {"line_number": "2", "quantity": 100, "unit_of_measure": "EA", "price": 5.50, "sku": "ITEM-Y"}
        ]
    }