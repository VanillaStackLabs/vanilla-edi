from pydantic import BaseModel, Field
from typing import ClassVar, Dict, Type, Optional


class BaseEDISchema(BaseModel):
    # Exclude from OpenAPI documentation since this is endpoint query metadata
    transaction_code: ClassVar[str] = ""
    partner_id: ClassVar[str] = "DEFAULT"

    _registry: ClassVar[Dict[str, Type["BaseEDISchema"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        txn_code = getattr(cls, "transaction_code", "")
        partner = getattr(cls, "partner_id", "DEFAULT")

        if txn_code:
            key = f"{partner}:{txn_code}" if partner != "DEFAULT" else txn_code
            BaseEDISchema._registry[key] = cls

    @classmethod
    def get_schema_for(cls, transaction_type: str, partner_id: str = "DEFAULT") -> Optional[Type["BaseEDISchema"]]:
        partner_key = f"{partner_id}:{transaction_type}"
        return cls._registry.get(partner_key) or cls._registry.get(transaction_type)