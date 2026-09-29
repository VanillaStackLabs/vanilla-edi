from pydantic import BaseModel
from typing import Optional, Type, Dict

# schemas/base.py
from pydantic import BaseModel
from typing import Optional, Type, Dict, ClassVar


class BaseEDISchema(BaseModel):
    """
    Base class for all VanillaEDI schemas.
    Automatically registers any subclass for dynamic runtime discovery.
    """
    transaction_code: str = ""
    partner_id: str = "DEFAULT"

    # ClassVar prevents Pydantic from converting this into a ModelPrivateAttr
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
        """Looks up a registered schema by partner ID and transaction code, falling back to DEFAULT."""
        partner_key = f"{partner_id}:{transaction_type}"
        return cls._registry.get(partner_key) or cls._registry.get(transaction_type)