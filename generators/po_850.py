from datetime import datetime
from typing import Dict, Any, List
from generators.base import BaseGenerator
from utils.formatters import pad_left_zero, format_currency

class PO850Generator(BaseGenerator):
    """Generates ANSI X12 850 Purchase Order transaction sets."""

    def __init__(self, element_sep: str = "*", segment_term: str = "~\n"):
        super().__init__(element_sep, segment_term)

    def generate(self, payload: Dict[str, Any]) -> str:
        """Generates a complete 850 interchange string from payload data."""
        dt = datetime.now()
        sender_id = payload.get("sender_id", "SENDER")
        receiver_id = payload.get("receiver_id", "RECEIVER")
        control_num = str(payload.get("control_number", "1"))

        # Envelope Headers
        output = []
        output.append(self.build_isa_header(sender_id, receiver_id, control_num, dt))
        output.append(self.build_gs_header("PO", sender_id, receiver_id, control_num, dt))

        st_control_num = pad_left_zero(control_num, 4)
        tx_segments = []

        # ST - Header
        tx_segments.append(f"ST{self.element_sep}850{self.element_sep}{st_control_num}")

        # BEG - Beginning Segment for Purchase Order
        # BEG01: Transaction Set Purpose Code (00 = Original)
        # BEG02: Purchase Order Type Code (SA = Stand Alone Order)
        # BEG03: Purchase Order Number
        # BEG05: Date (YYYYMMDD)
        po_num = payload.get("po_number", "PO-1001")
        po_date = payload.get("po_date", dt.strftime("%Y%m%d"))
        tx_segments.append(f"BEG{self.element_sep}00{self.element_sep}SA{self.element_sep}{po_num}{self.element_sep}{self.element_sep}{po_date}")

        # DTM - Requested Delivery Date (002 = Requested Delivery)
        if req_delivery := payload.get("requested_delivery_date"):
            tx_segments.append(f"DTM{self.element_sep}002{self.element_sep}{req_delivery}")

        # N1 Loops - Ship To (ST), Bill To (BT), etc.
        if ship_to := payload.get("ship_to"):
            tx_segments.append(f"N1{self.element_sep}ST{self.element_sep}{ship_to.get('name', '')}")
            if addr := ship_to.get("address"):
                tx_segments.append(f"N3{self.element_sep}{addr}")
            if any(k in ship_to for k in ("city", "state", "zip")):
                tx_segments.append(
                    f"N4{self.element_sep}{ship_to.get('city', '')}{self.element_sep}{ship_to.get('state', '')}{self.element_sep}{ship_to.get('zip', '')}"
                )

        if bill_to := payload.get("bill_to"):
            tx_segments.append(f"N1{self.element_sep}BT{self.element_sep}{bill_to.get('name', '')}")

        # PO1 Loop - Baseline Item Data
        line_items: List[Dict[str, Any]] = payload.get("line_items", [])
        calculated_total = 0.0

        for idx, item in enumerate(line_items, start=1):
            line_num = str(item.get("line_number", idx))
            qty = str(item.get("quantity", 1))
            uom = item.get("unit_of_measure", "EA")
            price = float(item.get("price", 0.0))
            price_str = format_currency(price)
            sku = item.get("sku", "")

            calculated_total += float(qty) * price

            # PO101: Line, PO102: Qty, PO103: UOM, PO104: Price, PO106: VN (Vendor Part), PO107: SKU
            tx_segments.append(f"PO1{self.element_sep}{line_num}{self.element_sep}{qty}{self.element_sep}{uom}{self.element_sep}{price_str}{self.element_sep}{self.element_sep}VN{self.element_sep}{sku}")

            # PID - Product Description
            if desc := item.get("description"):
                tx_segments.append(f"PID{self.element_sep}F{self.element_sep}{self.element_sep}{self.element_sep}{self.element_sep}{desc}")

        # CTT - Transaction Totals
        tx_segments.append(f"CTT{self.element_sep}{len(line_items)}")

        # AMT - Monetary Total
        total_amt = payload.get("total_amount")
        if total_amt is None:
            total_amt = calculated_total

        tx_segments.append(f"AMT{self.element_sep}TT{self.element_sep}{format_currency(total_amt)}")

        # SE - Trailer
        segment_count = len(tx_segments) + 1
        tx_segments.append(f"SE{self.element_sep}{segment_count}{self.element_sep}{st_control_num}")

        # Format segment endings
        for seg in tx_segments:
            output.append(seg + self.segment_term)

        # Envelope Trailers
        output.append(self.build_ge_trailer(1, control_num))
        output.append(self.build_iea_trailer(1, control_num))

        return "".join(output)