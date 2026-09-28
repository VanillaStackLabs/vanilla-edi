import pytest
from pydantic import ValidationError
from schemas import EDIDocumentSchema, Outbound997Request

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

def test_outbound_997_request_defaults():
    # Verifies the default_factory lambda for group_totals initializes correctly
    schema = Outbound997Request()
    assert schema.sender_id == "MYCOMPANY"
    assert schema.group_totals["included"] == 1
    assert schema.group_totals["accepted"] == 1

def test_schema_missing_required_field():
    with pytest.raises(ValidationError):
        # transaction_type is strictly required
        EDIDocumentSchema(status="success")