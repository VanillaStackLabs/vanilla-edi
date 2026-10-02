from parsers.base import BaseParser
from utils.formatters import safe_int, safe_float

class Parser850(BaseParser):
    transaction_code = "850"

    def parse(self) -> dict:
        parsed_data = {
            **self.envelope,
            "transaction_type": "850",
            "po_number": "",
            "po_date": "",
            "requested_delivery_date": "",
            "tax_exempt_id": "",
            "buyer_contact": {},
            "ship_to": {},
            "bill_to": {},
            "line_items": [],
            "total_amount": 0.0
        }

        current_entity = None
        current_line_item = None

        for segment in self.segments:
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # BEG - Beginning Segment for Purchase Order
            if tag == "BEG" and len(elements) >= 6:
                parsed_data["po_number"] = elements[3]
                parsed_data["po_date"] = elements[5]

            # DTM - Requested Delivery Date
            elif tag == "DTM" and len(elements) >= 3 and elements[1] == "002":
                parsed_data["requested_delivery_date"] = elements[2]

            # PER - Administrative Contact Details (Only capture header contact)
            elif tag == "PER" and len(elements) >= 3 and not parsed_data["buyer_contact"]:
                parsed_data["buyer_contact"]["name"] = elements[2]
                if len(elements) >= 5 and elements[3] == "TE":
                    parsed_data["buyer_contact"]["phone"] = elements[4]

            # TAX - Tax Information
            elif tag == "TAX" and len(elements) >= 2:
                parsed_data["tax_exempt_id"] = elements[1]

            # N1 - Name (Ship To or Bill To/Buyer)
            elif tag == "N1" and len(elements) >= 3:
                entity_type = elements[1]
                entity_name = elements[2]
                if entity_type == "ST":
                    parsed_data["ship_to"]["name"] = entity_name
                    current_entity = parsed_data["ship_to"]
                elif entity_type in ["BY", "BT"]:
                    parsed_data["bill_to"]["name"] = entity_name
                    current_entity = parsed_data["bill_to"]
                else:
                    # CRITICAL: Disown unhandled entities (like VN) so N3/N4 don't leak
                    current_entity = None

            # N3 - Street Address
            elif tag == "N3" and len(elements) >= 2 and current_entity is not None:
                current_entity["address"] = elements[1]  # Matches Pydantic AddressSchema 'address'

            # N4 - Geographic Location
            elif tag == "N4" and len(elements) >= 4 and current_entity is not None:
                current_entity["city"] = elements[1]
                current_entity["state"] = elements[2]
                current_entity["zip"] = elements[3]

            # PO1 - Line Item Data
            elif tag == "PO1" and len(elements) >= 5:
                current_line_item = {
                    "line_number": elements[1],
                    "quantity": safe_int(elements[2]),
                    "unit_of_measure": elements[3] if len(elements) >= 4 else "EA",
                    "price": safe_float(elements[4]),
                    "sku": elements[7] if len(elements) >= 8 else "",
                    "description": None
                }
                parsed_data["line_items"].append(current_line_item)

            # PID - Product Description
            elif tag == "PID" and len(elements) >= 6 and current_line_item is not None:
                current_line_item["description"] = elements[5]

            # AMT - Total Order Amount Summary
            elif tag == "AMT" and len(elements) >= 3 and elements[1] == "TT":
                parsed_data["total_amount"] = safe_float(elements[2])

        return parsed_data