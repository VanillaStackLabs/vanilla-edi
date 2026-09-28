from parsers.base import BaseParser, safe_int

ACK_STATUS_MAP = {
    "A": "Accepted",
    "E": "Accepted with Errors",
    "R": "Rejected",
    "P": "Partially Accepted",
    "M": "Rejected, Message Authentication Code Failed",
    "W": "Rejected, Unsatisfactory Position",
    "X": "Rejected, Decryption Failed",
}


class Parser997(BaseParser):
    transaction_code = "997"

    def parse(self) -> dict:
        parsed_data = {
            **self.envelope,
            "transaction_type": "997",
            "acknowledged_functional_group": "",
            "acknowledged_group_control_number": "",
            "acknowledgment_status": "",
            "acknowledgment_status_label": "",
            "transaction_set_acknowledgments": [],
            "group_totals": {},
        }

        current_tx_ack = None

        for segment in self.segments:
            clean_segment = segment.replace("\n", " ").replace("\r", "").strip()
            elements = [e.strip() for e in clean_segment.split(self.element_sep)]
            tag = elements[0]

            # AK1 - Functional Group Response Header
            if tag == "AK1" and len(elements) >= 3:
                parsed_data["acknowledged_functional_group"] = elements[1]
                parsed_data["acknowledged_group_control_number"] = elements[2]

            # AK2 - Transaction Set Response Header
            elif tag == "AK2" and len(elements) >= 3:
                current_tx_ack = {
                    "transaction_type": elements[1],
                    "control_number": elements[2],
                    "status": "",
                    "status_label": "",
                    "errors": [],
                }
                parsed_data["transaction_set_acknowledgments"].append(current_tx_ack)

            # AK3 - Data Segment Note (Segment level error)
            elif tag == "AK3" and len(elements) >= 2 and current_tx_ack:
                error_note = {
                    "segment_id": elements[1],
                    "segment_position": safe_int(elements[2]) if len(elements) >= 3 else 0,
                    "error_code": elements[4] if len(elements) >= 5 else "",
                    "element_errors": []
                }
                current_tx_ack["errors"].append(error_note)

            # AK4 - Data Element Note (Element level error)
            elif tag == "AK4" and len(elements) >= 2 and current_tx_ack and current_tx_ack["errors"]:
                last_segment_error = current_tx_ack["errors"][-1]
                element_note = {
                    "element_position": safe_int(elements[1]),
                    "error_code": elements[3] if len(elements) >= 4 else "",
                    "bad_value": elements[4] if len(elements) >= 5 else ""
                }
                last_segment_error["element_errors"].append(element_note)

            # AK5 - Transaction Set Response Trailer
            elif tag == "AK5" and len(elements) >= 2 and current_tx_ack:
                status_code = elements[1]
                current_tx_ack["status"] = status_code
                current_tx_ack["status_label"] = ACK_STATUS_MAP.get(status_code, "Unknown")

            # AK9 - Functional Group Response Trailer
            elif tag == "AK9" and len(elements) >= 2:
                status_code = elements[1]
                parsed_data["acknowledgment_status"] = status_code
                parsed_data["acknowledgment_status_label"] = ACK_STATUS_MAP.get(status_code, "Unknown")

                # Only populate count totals if elements are present
                if len(elements) >= 5:
                    parsed_data["group_totals"] = {
                        "included": safe_int(elements[2]),
                        "received": safe_int(elements[3]),
                        "accepted": safe_int(elements[4]),
                    }

        return parsed_data