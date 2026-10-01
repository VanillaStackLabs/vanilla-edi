# Extending Schemas in VanillaEDI

VanillaEDI is designed around **Zero-Boilerplate Extensibility**. Because enterprise trading partners (Walmart, Target, Home Depot, Amazon) often require partner-specific EDI qualifiers, segments, or validation rules, you do not need to modify core engine files. 

Instead, you can extend any base schema using standard Pydantic V2 inheritance.

---

## 1. Quickstart: Overriding a Core Schema

To create a custom schema for a specific trading partner:

1. Import the base model from `schemas`.
2. Subclass the base model (and any nested models like `LineItem` if adding item-level fields).
3. Register your custom model using `@register_schema`.

```python
from pydantic import Field
from schemas.invoice_810 import Invoice810, LineItem
from core.registry import register_schema

# Step 1: Extend nested models if line-item fields change
class TargetLineItem(LineItem):
    dpci_number: str = Field(..., description="IT107: Target DPCI catalog number")

# Step 2: Extend the root schema
@register_schema(transaction_type="810", partner_id="TARGET")
class TargetInvoice810(Invoice810):
    vendor_number: str = Field(..., description="REF*IA segment: Internal Vendor ID")
    line_items: list[TargetLineItem]
```
---
## 2. Inheritance Use Cases
### A. Adding Top-Level Header Segments
If a trading partner requires additional reference numbers (e.g., `REF*DP` Department Number or `REF*IA` Internal Vendor Number):
```python
class Custom850(PurchaseOrder850):
    department_number: Optional[str] = Field(None, description="REF*DP segment")
    promo_code: Optional[str] = Field(None, description="REF*PD segment")
```
### B. Adding Line-Level (Loop) Segments
To capture additional qualifiers on line items (e.g., UPCs, Buyer Catalog Numbers, or Subline Items), subclass `LineItem` first, then assign it to the root model:
```python
class CustomLineItem(LineItem):
    upc_code: Optional[str] = Field(None, description="PO1/IT1 UP Qualifier")
    national_drug_code: Optional[str] = Field(None, description="PO1/IT1 ND Qualifier")

class Custom810(Invoice810):
    line_items: list[CustomLineItem]
```
### C. Adding Custom Field Validation
You can enforce strict business rules (e.g., verifying control numbers, or preventing negative unit prices) using Pydantic `@field_validator`:
```python
from pydantic import field_validator

class Strict850(PurchaseOrder850):
    @field_validator("po_number")
    @classmethod
    def validate_po_format(cls, v: str) -> str:
        if not v.startswith("PO-"):
            raise ValueError("PO number must begin with prefix 'PO-'")
        return v
```
---
## 3. How Partner Routing Works
When an incoming EDI file is streamed to `/api/v1/parse`:
1. VanillaEDI extracts the `ISA06` (Sender ID) and `GS08`/`ST01` (Transaction Type).
2. The engine queries the registry for `{SENDER_ID}:{TRANSACTION_TYPE}` (e.g., `WALMART:850`).
3. If a partner-specific schema is found, it validates against that custom schema.
4. If no partner match is registered, it falls back to the default `850` schema.
---
## 4. Automatic Schema Export & OpenAPI Docs
Every custom schema automatically inherits Pydantic v2 JSON-Schema generation.

Hitting `GET /schemas/WALMART:850` will output the exact JSON Schema for that partner override, enabling AI agents, front-end forms, and third-party integrations to inspect requirements dynamically.

