from pydantic import Field
from typing import List, Optional, Dict, Any
from schemas.base import BaseEDISchema

class Outbound997Request(BaseEDISchema):
    transaction_code: str = "997"
    sender_id: str = Field("MYCOMPANY", description="ISA06 - Outbound sender ID")
    receiver_id: str = Field("TRADINGPARTNER", description="ISA08 - Outbound receiver ID")
    control_number: str = Field("000000001", description="ISA13 - Outbound interchange control number")
    acknowledged_functional_group: str = Field("PO", description="AK101 - Functional group ID being acknowledged (e.g., PO, IN, SH)")
    acknowledged_group_control_number: str = Field("11", description="AK102 - Group control number being acknowledged")
    acknowledgment_status: str = Field("A", description="AK901 - Acknowledgment code (A=Accepted, R=Rejected, P=Partially Accepted)")
    transaction_set_acknowledgments: Optional[List[Dict[str, Any]]] = Field(
        [], description="Optional AK2 loop details for individual transaction set responses"
    )
    group_totals: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {"included": 1, "received": 1, "accepted": 1},
        description="AK902–AK905 - Group level transaction counts"
    )