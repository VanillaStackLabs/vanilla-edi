from parsers.base import BaseParser
from utils.formatters import safe_int, safe_float


class Parser856(BaseParser):
    transaction_code = "856"

    def parse(self) -> dict:
        parsed_data = {
            **self.envelope,
            "transaction_type": "856",
            "shipment_id": "",
            "ship_date": "",
            "carrier_code": "",
            "tracking_number": "",
            "cartons": [],
            "shipped_items": []
        }

        current_item = None

        for segment in self.segments:
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # BSN - Beginning Segment for Ship Notice
            if tag == "BSN" and len(elements) >= 4:
                parsed_data["shipment_id"] = elements[2]
                parsed_data["ship_date"] = elements[3]

            # TD5 - Carrier Details
            elif tag == "TD5" and len(elements) >= 5:
                parsed_data["carrier_code"] = elements[3]

            # MAN - Carton Barcode / SSCC-18
            elif tag == "MAN" and len(elements) >= 3:
                parsed_data["cartons"].append({"sscc_18": elements[2]})

            elif tag == "REF" and len(elements) >= 3:
                ref_type = elements[1]
                ref_value = elements[2]

                if ref_type in ["2I", "CN"]:
                    parsed_data["tracking_number"] = ref_value
                elif ref_type == "SE" and current_item:
                    current_item["serial_numbers"].append(ref_value)
                elif ref_type in ["BB", "PLA"] and current_item:
                    if "authorization_codes" not in current_item:
                        current_item["authorization_codes"] = []
                    current_item["authorization_codes"].append(ref_value)

            # LIN - Item Identification
            elif tag == "LIN" and len(elements) >= 4:
                current_item = {
                    "line_number": elements[1],
                    "sku": elements[3],
                    "vendor_part": elements[5] if len(elements) >= 6 else "",
                    "quantity_shipped": 0,
                    "serial_numbers": []
                }
                parsed_data["shipped_items"].append(current_item)

            # SN1 - Item Detail (Quantity)
            elif tag == "SN1" and len(elements) >= 3 and current_item:
                current_item["quantity_shipped"] = safe_int(elements[2])

        return parsed_data