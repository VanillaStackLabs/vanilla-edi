from fastapi import APIRouter, HTTPException
from typing import Any

# Import your existing Pydantic models
from schemas.invoice_810 import Invoice810
from schemas.po_850 import PurchaseOrder850
from schemas.asn_856 import ASN856

router = APIRouter()

SCHEMA_REGISTRY = {
    "810": Invoice810,
    "850": PurchaseOrder850,
    "856": ASN856
}


@router.get("/schemas/{transaction_type}", response_model=dict[str, Any])
def get_transaction_schema(transaction_type: str):
    """
    Returns the JSON schema for a specific X12 transaction set.
    Allows AI agents and front-end clients to validate payloads locally.
    """
    model = SCHEMA_REGISTRY.get(transaction_type)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Schema for transaction type '{transaction_type}' not found."
        )

    # Export the Pydantic V2 native schema
    return model.model_json_schema()