from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict


class LineItem(BaseModel):
    line_number: str = Field(..., description="PO101 - Line item sequence identifier")
    quantity: int = Field(0, description="PO102 - Quantity ordered or invoiced")
    price: float = Field(0.0, description="PO104 - Unit price")
    sku: Optional[str] = Field("", description="PO107 / Vendor Part Number or SKU")
    description: Optional[str] = Field("", description="PID05 - Item description")


class EDIDocumentSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    transaction_type: str = Field(..., description="ST01 - Transaction set identifier code (e.g., 850, 810, 856, 997)")
    sender_id: Optional[str] = Field("", description="ISA06 - Interchange sender ID")
    receiver_id: Optional[str] = Field("", description="ISA08 - Interchange receiver ID")
    control_number: Optional[str] = Field("", description="ISA13 - Interchange control number")
    status: Optional[str] = Field("success", description="Processing status indicator (e.g., 'success', 'unsupported_transaction_set')")
    message: Optional[str] = Field(None, description="Detailed status, warning, or error message")

    ship_to: Optional[Dict[str, Any]] = Field(None, description="N1*ST / N1*BY - Shipping address and contact information")
    remit_to: Optional[Dict[str, Any]] = Field(None, description="N1*RE / N1*RI - Remittance and payment destination address")

    po_number: Optional[str] = Field(None, description="BEG03 / BIG04 - Purchase order reference number")
    po_date: Optional[str] = Field(None, description="BEG05 / BIG03 - Purchase order date (CCYYMMDD or YYMMDD)")
    invoice_number: Optional[str] = Field(None, description="BIG02 - Invoice reference number")
    invoice_date: Optional[str] = Field(None, description="BIG01 - Invoice date")
    total_amount: Optional[float] = Field(None, description="TDS01 - Total invoice monetary amount")

    shipment_id: Optional[str] = Field(None, description="BSN02 - Shipment identification number")
    ship_date: Optional[str] = Field(None, description="BSN03 - Date shipped")
    carrier_code: Optional[str] = Field(None, description="TD503 - Standard Carrier Alpha Code (SCAC)")
    tracking_number: Optional[str] = Field(None, description="REF*CN / REF*2I - Bill of lading or tracking number")

    line_items: Optional[List[Dict[str, Any]]] = Field([], description="List of line items for 850 POs or 810 Invoices")
    shipped_items: Optional[List[Dict[str, Any]]] = Field([], description="List of shipped items for 856 Advance Ship Notices")


class Outbound997Request(BaseModel):
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
