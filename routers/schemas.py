from fastapi import APIRouter, HTTPException
from typing import Any
from schemas.base import BaseEDISchema

router = APIRouter(prefix="/schemas", tags=["Schemas"])

@router.get("/schemas/{transaction_type}", response_model=dict[str, Any])
def get_transaction_schema(transaction_type: str, partner_id: str = "DEFAULT"):
    model = BaseEDISchema.get_schema_for(transaction_type, partner_id=partner_id)
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Schema for transaction type '{transaction_type}' not found."
        )
    return model.model_json_schema()