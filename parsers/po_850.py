from parsers.base import BaseParser, safe_int, safe_float


class Parser850(BaseParser):
    transaction_code = "850"

    def parse(self) -> dict:
        parsed_data = {
            **self.envelope,
            "po_number": "",
            "po_date": "",
            "tax_exempt_id": "",
            "buyer_contact": {},
            "ship_to": {},
            "line_items": []
        }

        current_line_item = None

        for segment in self.segments:
            # Strip literal line breaks embedded inside transmission text
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # BEG - Beginning Segment for Purchase Order
            if tag == "BEG" and len(elements) >= 6:
                parsed_data["po_number"] = elements[3]
                parsed_data["po_date"] = elements[5]

            # PER - Administrative Contact Details
            elif tag == "PER" and len(elements) >= 3:
                parsed_data["buyer_contact"]["name"] = elements[2]
                if len(elements) >= 5 and elements[3] == "TE":
                    parsed_data["buyer_contact"]["phone"] = elements[4]

            # TAX - Tax Information
            elif tag == "TAX" and len(elements) >= 2:
                parsed_data["tax_exempt_id"] = elements[1]

            # N1 - Name (Ship To or Buyer)
            elif tag == "N1" and len(elements) >= 3 and elements[1] in ["ST", "BY"]:
                parsed_data["ship_to"]["name"] = elements[2]

            # N2 - Additional Name / Division
            elif tag == "N2" and len(elements) >= 2:
                parsed_data["ship_to"]["division"] = elements[1]

            # N3 - Street Address
            elif tag == "N3" and len(elements) >= 2:
                parsed_data["ship_to"]["address1"] = elements[1]

            # N4 - Geographic Location
            elif tag == "N4" and len(elements) >= 4:
                parsed_data["ship_to"]["city"] = elements[1]
                parsed_data["ship_to"]["state"] = elements[2]
                parsed_data["ship_to"]["zip"] = elements[3]

            # PO1 - Line Item Data
            elif tag == "PO1" and len(elements) >= 5:
                current_line_item = {
                    "line_number": elements[1],
                    "quantity": safe_int(elements[2]),
                    "price": safe_float(elements[4]),
                    "sku": elements[7] if len(elements) >= 8 else "",
                    "description": ""
                }
                parsed_data["line_items"].append(current_line_item)

            # PID - Product Description
            elif tag == "PID" and len(elements) >= 5 and current_line_item:
                current_line_item["description"] = elements[5]

        return parsed_data