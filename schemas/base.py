from pydantic import BaseModel
from typing import Optional, Type


class BaseEDISchema(BaseModel):
    """Base class for all VanillaEDI top-level transaction requests."""

    transaction_code: str = ""

    @classmethod
    def get_schema_for(cls, transaction_type: str) -> Optional[Type['BaseEDISchema']]:
        """Recursively finds the subclass registered for a transaction code."""
        for subclass in cls.__subclasses__():
            if getattr(subclass, "transaction_code", "") == transaction_type:
                return subclass
        return None