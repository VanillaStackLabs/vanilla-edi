import pytest
from pydantic import ValidationError
from schemas import (
    EDIDocumentSchema,
    Outbound997Request,
    Generate810Request,
    Generate856Request,
    Generate850Request
)


# --- Inbound Schema Tests ---

def test_edi_document_schema_allows_extra_fields():
    # Verifies the model_config ConfigDict allows arbitrary extra keys
    data = {
        "transaction_type": "850",
        "custom_erp_field": "ERP-9921",
        "unmapped_data": {"key": "value"}
    }
    schema = EDIDocumentSchema(**data)
    assert schema.transaction_type == "850"
    assert hasattr(schema, "custom_erp_field")
    assert schema.custom_erp_field == "ERP-9921"


def test_schema_missing_required_field():
    with pytest.raises(ValidationError):
        # transaction_type is strictly required
        EDIDocumentSchema(status="success")


# --- Outbound Schema Tests ---

def test_outbound_997_request_defaults():
    # Verifies the default_factory lambda for group_totals initializes correctly
    schema = Outbound997Request()
    assert schema.sender_id == "MYCOMPANY"
    assert schema.group_totals["included"] == 1
    assert schema.group_totals["accepted"] == 1


def test_generate_810_request_schema():
    # Verifies required fields and defaults for 810 generation
    data = {
        "invoice_number": "INV-123",
        "line_items": [{"quantity": 10.0, "price": 5.50, "sku": "WIDGET-1"}]
    }
    schema = Generate810Request(**data)

    assert schema.invoice_number == "INV-123"
    assert schema.sender_id == "MYDISTRO"  # Default sender ID
    assert schema.line_items[0].unit_of_measure == "EA"  # Default UOM


def test_generate_856_request_schema():
    # Verifies nested loops and defaults for 856 ASN generation
    data = {
        "shipment_id": "SH-999",
        "orders": [
            {
                "po_number": "PO-123",
                "shipped_items": [{"sku": "SKU-1", "quantity": 100}]
            }
        ]
    }
    schema = Generate856Request(**data)

    assert schema.shipment_id == "SH-999"
    assert schema.carrier_code == "FDEG"  # Default SCAC
    assert schema.orders[0].shipped_items[0].quantity == 100


def test_generate_850_request_schema():
    # Verifies 850 PO generator request schema constraints
    data = {
        "po_number": "PO-888",
        "line_items": [{"quantity": 50, "price": 10.0, "sku": "ITEM-8"}]
    }
    schema = Generate850Request(**data)

    assert schema.po_number == "PO-888"
    assert schema.control_number == "10001"  # Default control number
    assert schema.line_items[0].line_number == "1"  # Default line sequence
    assert schema.line_items[0].price == 10.0


def test_outbound_schema_validation_failures():
    # Verifies that missing required fields trigger validation errors
    with pytest.raises(ValidationError, match="invoice_number"):
        Generate810Request(line_items=[])

    with pytest.raises(ValidationError, match="shipment_id"):
        Generate856Request(orders=[])

    with pytest.raises(ValidationError, match="po_number"):
        Generate850Request(line_items=[])