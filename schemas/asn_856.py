from pydantic import Field
from typing import List, Optional
from schemas.invoice_810 import AddressSchema
from schemas.base import BaseEDISchema

class ShippedItemSchema(BaseEDISchema):
    sku: str = Field(..., description="Vendor SKU or Product ID")
    quantity: int = Field(1, description="Quantity shipped")
    unit_of_measure: str = Field("EA", description="Unit of measure code")

class OrderSchema(BaseEDISchema):
    po_number: str = Field(..., description="Purchase order reference number")
    shipped_items: List[ShippedItemSchema] = Field(..., description="List of items included in this order")

class Generate856Request(BaseEDISchema):
    transaction_code: ClassVar[str] = "856"
    sender_id: str = Field("MYDISTRO", description="ISA06 Sender ID")
    receiver_id: str = Field("WALMART", description="ISA08 Receiver ID")
    control_number: str = Field("5001", description="ISA13 Control Number")
    shipment_id: str = Field(..., description="BSN02 Shipment Identification Number")
    ship_date: Optional[str] = Field(None, description="Ship date in YYYYMMDD format")
    ship_time: Optional[str] = Field(None, description="Ship time in HHMM format")
    carrier_code: Optional[str] = Field("FDEG", description="TD503 Carrier Alpha Code (SCAC)")
    tracking_number: Optional[str] = Field(None, description="Bill of Lading or Tracking Number")
    ship_from: Optional[AddressSchema] = None
    ship_to: Optional[AddressSchema] = None
    orders: List[OrderSchema] = Field(..., description="List of orders contained in this shipment")

class Generate856Response(BaseEDISchema):
    success: bool = True
    edi_content: str