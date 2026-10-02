from pydantic import Field
from typing import List, Optional, ClassVar
from schemas.invoice_810 import AddressSchema
from schemas.base import BaseEDISchema

class ShippedItemSchema(BaseEDISchema):
    line_number: Optional[str] = Field(None, description="LIN01 Line Item Number")
    sku: str = Field(..., description="Vendor SKU or Product ID")
    vendor_part: Optional[str] = Field(None, description="Vendor Part Number")
    quantity: int = Field(1, description="Quantity shipped")
    unit_of_measure: str = Field("EA", description="Unit of measure code")

class PackSchema(BaseEDISchema):
    cartons: Optional[List[dict]] = Field(None, description="List of SSCC-18 barcodes (MAN segments)")
    items: List[ShippedItemSchema] = Field(default_factory=list, description="Items inside this pack/carton")

class TareSchema(BaseEDISchema):
    pallets: Optional[List[dict]] = Field(None, description="Pallet tracking/barcodes")
    packs: List[PackSchema] = Field(default_factory=list, description="Packs/Cartons loaded on this pallet")

class OrderSchema(BaseEDISchema):
    po_number: str = Field(..., description="Purchase order reference number (PRF01)")
    tares: Optional[List[TareSchema]] = Field(default_factory=list, description="Pallets in this order")
    packs: Optional[List[PackSchema]] = Field(default_factory=list, description="Packs in this order (if no pallets are used)")
    items: Optional[List[ShippedItemSchema]] = Field(default_factory=list, description="Loose items (if no packaging is specified)")

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