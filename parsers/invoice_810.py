from parsers.base import BaseParser
from utils.formatters import safe_int, safe_float

class Parser810(BaseParser):
    transaction_code = "810"

    def parse(self) -> dict:
        parsed_data = {
            **self.envelope,
            "transaction_type": "810",
            "invoice_number": "",
            "invoice_date": "",
            "po_number": "",
            "po_date": "",
            "release_number": "",
            "total_amount": 0.0,
            "payment_terms": {},
            "remit_to": {},
            "ship_to": {},
            "line_items": []
        }

        current_entity = None

        for segment in self.segments:
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # BIG - Beginning Segment for Invoice
            if tag == "BIG" and len(elements) >= 5:
                parsed_data["invoice_date"] = elements[1]
                parsed_data["invoice_number"] = elements[2]
                parsed_data["po_date"] = elements[3]
                parsed_data["po_number"] = elements[4]
                if len(elements) >= 6:
                    parsed_data["release_number"] = elements[5]

            # ITD - Terms of Sale / Deferred Terms
            elif tag == "ITD":
                parsed_data["payment_terms"] = {
                    "terms_type": elements[1] if len(elements) >= 2 else "",
                    "net_days": safe_int(elements[7]) if len(elements) >= 8 else 0
                }

            # N1 - Name (Remit To, Ship To, or Bill To)
            elif tag == "N1" and len(elements) >= 3:
                entity_type = elements[1]
                entity_name = elements[2]
                if entity_type in ["RE", "RI"]:
                    parsed_data["remit_to"]["name"] = entity_name
                    current_entity = parsed_data["remit_to"]
                elif entity_type in ["ST", "BY", "BT"]:
                    parsed_data["ship_to"]["name"] = entity_name
                    current_entity = parsed_data["ship_to"]

            # N3 - Street Address
            elif tag == "N3" and len(elements) >= 2 and current_entity is not None:
                current_entity["address1"] = elements[1]

            # N4 - City / State / ZIP
            elif tag == "N4" and len(elements) >= 4 and current_entity is not None:
                current_entity["city"] = elements[1]
                current_entity["state"] = elements[2]
                current_entity["zip"] = elements[3]

            # IT1 - Line Item Detail
            elif tag == "IT1" and len(elements) >= 5:
                line_item = {
                    "line_number": elements[1],
                    "quantity": safe_int(elements[2]),
                    "unit_price": safe_float(elements[4]),
                    "sku": elements[7] if len(elements) >= 8 else ""
                }
                parsed_data["line_items"].append(line_item)

            # TDS - Total Monetary Value Summary
            elif tag == "TDS" and len(elements) >= 2:
                raw_total = safe_float(elements[1])
                parsed_data["total_amount"] = round(raw_total / 100, 2) if raw_total > 0 else 0.0

        return parsed_data