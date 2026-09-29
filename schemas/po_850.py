from pydantic import Field
from typing import List, Optional
from schemas.invoice_810 import AddressSchema
from schemas.base import BaseEDISchema

class LineItem850Schema(BaseEDISchema):
    line_number: str = Field("1", description="PO101 Line sequence number")
    quantity: int = Field(..., description="PO102 Quantity ordered")
    unit_of_measure: str = Field("EA", description="PO103 Unit of measure code")
    price: float = Field(..., description="PO104 Unit price")
    sku: str = Field(..., description="PO107 Vendor Part Number / SKU")
    description: Optional[str] = Field(None, description="PID05 Item description")

class Generate850Request(BaseEDISchema):
    sender_id: str = Field("BUYERCO", description="ISA06 Sender ID")
    receiver_id: str = Field("VENDORCO", description="ISA08 Receiver ID")
    control_number: str = Field("10001", description="ISA13 Control Number")
    po_number: str = Field(..., description="BEG03 Purchase order reference number")
    po_date: Optional[str] = Field(None, description="BEG05 Date in YYYYMMDD format")
    requested_delivery_date: Optional[str] = Field(None, description="DTM02 Date in YYYYMMDD format")
    ship_to: Optional[AddressSchema] = None
    bill_to: Optional[AddressSchema] = None
    line_items: List[LineItem850Schema] = Field(..., description="List of ordered items")
    total_amount: Optional[float] = Field(None, description="Total order amount (calculated automatically if omitted)")

class Generate850Response(BaseEDISchema):
    success: bool = True
    edi_content: str