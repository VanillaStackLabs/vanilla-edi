from datetime import datetime
from typing import Dict, Any, List
from generators.base import BaseGenerator
from utils.formatters import pad_left_zero


class Invoice810Generator(BaseGenerator):
    """Generates ANSI X12 810 Invoice transaction sets."""

    def __init__(self, element_sep: str = "*", segment_term: str = "~\n"):
        super().__init__(element_sep, segment_term)

    def generate(self, payload: Dict[str, Any]) -> str:
        """Generates a complete 810 interchange string from payload data."""
        dt = datetime.now()
        sender_id = payload.get("sender_id", "SENDER")
        receiver_id = payload.get("receiver_id", "RECEIVER")
        control_num = str(payload.get("control_number", "1"))

        # Envelope Headers
        output = []
        output.append(self.build_isa_header(sender_id, receiver_id, control_num, dt))
        output.append(self.build_gs_header("IN", sender_id, receiver_id, control_num, dt))

        # Transaction Set (ST loop)
        st_control_num = pad_left_zero(control_num, 4)
        tx_segments = []

        # ST - Header
        tx_segments.append(f"ST{self.element_sep}810{self.element_sep}{st_control_num}")

        # BIG - Beginning Segment for Invoice (Safe fallbacks for None values)
        invoice_date = payload.get("invoice_date") or dt.strftime("%Y%m%d")
        invoice_num = payload.get("invoice_number") or ""
        po_date = payload.get("po_date") or ""
        po_num = payload.get("po_number") or ""

        big_elements = ["BIG", invoice_date, invoice_num, po_date, po_num]
        tx_segments.append(self.element_sep.join(big_elements))

        # N1 Loops - Addresses
        if remit_to := payload.get("remit_to"):
            tx_segments.append(f"N1{self.element_sep}RE{self.element_sep}{remit_to.get('name', '')}")
            if addr := remit_to.get("address"):
                tx_segments.append(f"N2{self.element_sep}{addr}")
            city_state = f"N3{self.element_sep}{remit_to.get('city', '')}{self.element_sep}{remit_to.get('state', '')}{self.element_sep}{remit_to.get('zip', '')}"
            tx_segments.append(city_state)

        if bill_to := payload.get("bill_to"):
            tx_segments.append(f"N1{self.element_sep}BT{self.element_sep}{bill_to.get('name', '')}")
            if addr := bill_to.get("address"):
                tx_segments.append(f"N2{self.element_sep}{addr}")
            city_state = f"N3{self.element_sep}{bill_to.get('city', '')}{self.element_sep}{bill_to.get('state', '')}{self.element_sep}{bill_to.get('zip', '')}"
            tx_segments.append(city_state)

        # IT1 Loops - Line Items
        line_items: List[Dict[str, Any]] = payload.get("line_items", [])
        total_invoice_amount = 0.0

        for item in line_items:
            line_num = str(item.get("line_number", "1"))
            qty = str(item.get("quantity", 0))
            unit = item.get("unit_of_measure", "EA")
            price_val = float(item.get("price", 0.0))
            price_str = f"{price_val:.2f}"
            sku = item.get("sku", "")

            # Accumulate total for TDS segment
            total_invoice_amount += float(qty) * price_val

            it1_elements = ["IT1", line_num, qty, unit, price_str, "", "VN", sku]
            tx_segments.append(self.element_sep.join(it1_elements))

            if desc := item.get("description"):
                tx_segments.append(f"PID{self.element_sep}F{self.element_sep}{self.element_sep}{self.element_sep}{self.element_sep}{desc}")

        # TDS - Total Monetary Value Summary (Safe fallback for None total)
        provided_total = payload.get("total_amount")
        final_total = provided_total if provided_total is not None else total_invoice_amount

        tds_amount = str(int(round(final_total * 100)))
        tx_segments.append(f"TDS{self.element_sep}{tds_amount}")

        # CTT - Transaction Totals
        tx_segments.append(f"CTT{self.element_sep}{len(line_items)}")

        # SE - Trailer (Count includes ST and SE)
        segment_count = len(tx_segments) + 1
        tx_segments.append(f"SE{self.element_sep}{segment_count}{self.element_sep}{st_control_num}")

        # Append formatted ST segments
        for seg in tx_segments:
            output.append(seg + self.segment_term)

        # Envelope Trailers
        output.append(self.build_ge_trailer(1, control_num))
        output.append(self.build_iea_trailer(1, control_num))

        return "".join(output)