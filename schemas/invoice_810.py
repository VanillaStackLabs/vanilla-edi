from pydantic import Field
from typing import List, Optional
from schemas.base import BaseEDISchema

class AddressSchema(BaseEDISchema):
    name: str = Field(..., description="Entity name")
    address: Optional[str] = Field(None, description="Street address line")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="Two-letter state code")
    zip: Optional[str] = Field(None, description="Postal code")

class LineItem810Schema(BaseEDISchema):
    line_number: str = Field("1", description="Line sequence number")
    quantity: float = Field(..., description="Quantity shipped/invoiced")
    unit_of_measure: str = Field("EA", description="Unit of measure code")
    price: float = Field(..., description="Unit price")
    sku: str = Field(..., description="Vendor SKU / Product ID")
    description: Optional[str] = Field(None, description="Item description")

class Generate810Request(BaseEDISchema):
    sender_id: str = Field("MYDISTRO", description="ISA06 Sender ID")
    receiver_id: str = Field("WALMART", description="ISA08 Receiver ID")
    control_number: str = Field("1001", description="ISA13 Control Number")
    invoice_number: str = Field(..., description="Invoice reference number")
    invoice_date: Optional[str] = Field(None, description="Invoice date in YYYYMMDD format")
    po_number: Optional[str] = Field(None, description="Purchase order reference number")
    po_date: Optional[str] = Field(None, description="PO date in YYYYMMDD format")
    remit_to: Optional[AddressSchema] = None
    bill_to: Optional[AddressSchema] = None
    line_items: List[LineItem810Schema]
    total_amount: Optional[float] = Field(None, description="Total monetary amount (calculated automatically if omitted)")

class Generate810Response(BaseEDISchema):
    success: bool = True
    edi_content: str