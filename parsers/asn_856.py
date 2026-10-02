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
            "hierarchy": {}
        }

        # State tracking for HL segments
        nodes = {}
        current_hl_id = None

        for segment in self.segments:
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # BSN - Beginning Segment for Ship Notice
            if tag == "BSN" and len(elements) >= 4:
                parsed_data["shipment_id"] = elements[2]
                parsed_data["ship_date"] = elements[3]

            # HL - Hierarchical Level (The Engine)
            elif tag == "HL" and len(elements) >= 4:
                hl_id = elements[1]
                parent_id = elements[2] if elements[2] else None
                level_code = elements[3]

                # Initialize the current node
                nodes[hl_id] = {
                    "level_code": level_code,
                    "details": {},
                    "children": []
                }
                current_hl_id = hl_id

                # Link this node to its parent, or set it as the root
                if parent_id and parent_id in nodes:
                    nodes[parent_id]["children"].append(nodes[hl_id])
                elif not parent_id:
                    parsed_data["hierarchy"] = nodes[hl_id]  # Root node (Shipment)

            # PRF - Purchase Order Reference (Belongs to Order Level)
            elif tag == "PRF" and len(elements) >= 2 and current_hl_id:
                nodes[current_hl_id]["details"]["po_number"] = elements[1]

            # TD5 - Carrier Details
            elif tag == "TD5" and len(elements) >= 5:
                parsed_data["carrier_code"] = elements[3]

            # MAN - Carton Barcode (Belongs to Tare/Pack Level)
            elif tag == "MAN" and len(elements) >= 3 and current_hl_id:
                if "cartons" not in nodes[current_hl_id]["details"]:
                    nodes[current_hl_id]["details"]["cartons"] = []
                nodes[current_hl_id]["details"]["cartons"].append({"sscc_18": elements[2]})

            # LIN - Item Identification (Belongs to Item Level)
            elif tag == "LIN" and len(elements) >= 4 and current_hl_id:
                nodes[current_hl_id]["details"]["item"] = {
                    "line_number": elements[1],
                    "sku": elements[3],
                    "vendor_part": elements[5] if len(elements) >= 6 else "",
                    "quantity_shipped": 0
                }

            # SN1 - Item Detail / Quantity (Belongs to Item Level)
            elif tag == "SN1" and len(elements) >= 3 and current_hl_id:
                if "item" in nodes[current_hl_id]["details"]:
                    nodes[current_hl_id]["details"]["item"]["quantity_shipped"] = safe_int(elements[2])

        return parsed_data