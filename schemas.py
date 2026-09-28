from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict

class LineItem(BaseModel):
    line_number: str = Field(..., description="Line item ID")
    quantity: int = Field(0, description="Quantity")
    price: float = Field(0.0, description="Price per unit")
    sku: Optional[str] = Field("", description="SKU or Part Number")
    description: Optional[str] = Field("", description="Product description")

class EDIDocumentSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # Modern Pydantic V2 syntax
    transaction_type: str = Field(..., description="e.g., 850, 810, 856")
    sender_id: Optional[str] = Field("", description="ISA06 - Sender ID")
    receiver_id: Optional[str] = Field("", description="ISA08 - Receiver ID")
    control_number: Optional[str] = Field("", description="ISA13 - Control Number")
    status: Optional[str] = Field("success", description="Status code or error indicator")
    message: Optional[str] = Field(None, description="Detailed status message")
    ship_to: Optional[Dict[str, Any]] = None
    remit_to: Optional[Dict[str, Any]] = None
    po_number: Optional[str] = None
    po_date: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    shipment_id: Optional[str] = None
    ship_date: Optional[str] = None
    carrier_code: Optional[str] = None
    tracking_number: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = []
    shipped_items: Optional[List[Dict[str, Any]]] = []

class Outbound997Request(BaseModel):
    sender_id: str = Field("MYCOMPANY", description="ISA06 Sender ID")
    receiver_id: str = Field("TRADINGPARTNER", description="ISA08 Receiver ID")
    control_number: str = Field("000000001", description="Control number")
    acknowledged_functional_group: str = Field("PO", description="Group type being acknowledged")
    acknowledged_group_control_number: str = Field("11", description="GS Control number being acknowledged")
    acknowledgment_status: str = Field("A", description="A=Accepted, R=Rejected, P=Partial, E=Errors")
    transaction_set_acknowledgments: Optional[List[Dict[str, Any]]] = []
    group_totals: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {"included": 1, "received": 1, "accepted": 1}
    )