from datetime import datetime
from typing import Dict, Any, List
from generators.base import BaseGenerator
from utils.formatters import pad_left_zero


class ASN856Generator(BaseGenerator):
    """Generates ANSI X12 856 Advance Ship Notice (ASN) transaction sets."""

    def __init__(self, element_sep: str = "*", segment_term: str = "~\n"):
        super().__init__(element_sep, segment_term)

    def generate(self, payload: Dict[str, Any]) -> str:
        """Generates a complete 856 interchange string from payload data."""
        dt = datetime.now()
        sender_id = payload.get("sender_id", "SENDER")
        receiver_id = payload.get("receiver_id", "RECEIVER")
        control_num = str(payload.get("control_number", "1"))

        # Envelope Headers
        output = []
        output.append(self.build_isa_header(sender_id, receiver_id, control_num, dt))
        output.append(self.build_gs_header("SH", sender_id, receiver_id, control_num, dt))

        st_control_num = pad_left_zero(control_num, 4)
        tx_segments = []

        # ST - Header
        tx_segments.append(f"ST{self.element_sep}856{self.element_sep}{st_control_num}")

        # BSN - Beginning Segment for Ship Notice
        ship_id = payload.get("shipment_id", "SHIP001")
        ship_date = payload.get("ship_date", dt.strftime("%Y%m%d"))
        ship_time = payload.get("ship_time", dt.strftime("%H%M"))

        # BSN01: Transaction Set Purpose (00 = Original)
        tx_segments.append(f"BSN{self.element_sep}00{self.element_sep}{ship_id}{self.element_sep}{ship_date}{self.element_sep}{ship_time}")

        hl_counter = 0

        # --- LEVEL 1: SHIPMENT (S) ---
        hl_counter += 1
        shipment_hl_id = hl_counter
        # HL: ID, Parent ID (empty for root), Level Code (S)
        tx_segments.append(f"HL{self.element_sep}{shipment_hl_id}{self.element_sep}{self.element_sep}S")

        # TD5 - Carrier Details & REF - Tracking
        carrier = payload.get("carrier_code", "FDEG")
        tracking = payload.get("tracking_number", "")
        tx_segments.append(f"TD5{self.element_sep}B{self.element_sep}2{self.element_sep}{carrier}")
        if tracking:
            tx_segments.append(f"REF{self.element_sep}CN{self.element_sep}{tracking}")

        # DTM - Ship Date
        tx_segments.append(f"DTM{self.element_sep}011{self.element_sep}{ship_date}")

        # N1 Loops - Ship From / Ship To
        if ship_from := payload.get("ship_from"):
            tx_segments.append(f"N1{self.element_sep}SF{self.element_sep}{ship_from.get('name', '')}")
        if ship_to := payload.get("ship_to"):
            tx_segments.append(f"N1{self.element_sep}ST{self.element_sep}{ship_to.get('name', '')}")

        # --- LEVEL 2: ORDER (O) & DYNAMIC CHILD LEVELS ---
        orders: List[Dict[str, Any]] = payload.get("orders", [])
        for order in orders:
            hl_counter += 1
            order_hl_id = hl_counter
            # HL: ID, Parent ID (shipment_hl_id), Level Code (O)
            tx_segments.append(f"HL{self.element_sep}{order_hl_id}{self.element_sep}{shipment_hl_id}{self.element_sep}O")

            if po_num := order.get("po_number"):
                tx_segments.append(f"PRF{self.element_sep}{po_num}")

            # Helper to write Item loops
            def write_items(items_list, parent_hl_id):
                nonlocal hl_counter
                for item in items_list:
                    hl_counter += 1
                    tx_segments.append(f"HL{self.element_sep}{hl_counter}{self.element_sep}{parent_hl_id}{self.element_sep}I")

                    line_num = item.get("line_number", "")
                    sku = item.get("sku", "")
                    qty = str(item.get("quantity", 1))
                    uom = item.get("unit_of_measure", "EA")

                    tx_segments.append(f"LIN{self.element_sep}{line_num}{self.element_sep}VN{self.element_sep}{sku}")
                    tx_segments.append(f"SN1{self.element_sep}{self.element_sep}{qty}{self.element_sep}{uom}")

            # Helper to write Pack (Carton) loops
            def write_packs(packs_list, parent_hl_id):
                nonlocal hl_counter
                for pack in packs_list:
                    hl_counter += 1
                    pack_hl_id = hl_counter
                    tx_segments.append(f"HL{self.element_sep}{pack_hl_id}{self.element_sep}{parent_hl_id}{self.element_sep}P")

                    # Add MAN segment for carton barcodes if they exist
                    if cartons := pack.get("cartons"):
                        for carton in cartons:
                            if sscc := carton.get("sscc") or carton.get("tracking"):
                                tx_segments.append(f"MAN{self.element_sep}GM{self.element_sep}{sscc}")

                    if pack_items := pack.get("items"):
                        write_items(pack_items, pack_hl_id)

            # Route the hierarchy based on the provided payload structure
            if tares := order.get("tares"):
                # Path 1: S-O-T-P-I (Palletized)
                for tare in tares:
                    hl_counter += 1
                    tare_hl_id = hl_counter
                    tx_segments.append(f"HL{self.element_sep}{tare_hl_id}{self.element_sep}{order_hl_id}{self.element_sep}T")

                    if pallets := tare.get("pallets"):
                        for pallet in pallets:
                            if sscc := pallet.get("sscc"):
                                tx_segments.append(f"MAN{self.element_sep}GM{self.element_sep}{sscc}")

                    if packs := tare.get("packs"):
                        write_packs(packs, tare_hl_id)

            elif packs := order.get("packs"):
                # Path 2: S-O-P-I (Cartonized, no Pallets)
                write_packs(packs, order_hl_id)

            elif items := order.get("items"):
                # Path 3: S-O-I (Loose Items)
                write_items(items, order_hl_id)

        # CTT - Transaction Totals (Count of HL segments)
        tx_segments.append(f"CTT{self.element_sep}{hl_counter}")

        # SE - Trailer
        segment_count = len(tx_segments) + 1
        tx_segments.append(f"SE{self.element_sep}{segment_count}{self.element_sep}{st_control_num}")

        # Append formatted segments
        for seg in tx_segments:
            output.append(seg + self.segment_term)

        # Envelope Trailers
        output.append(self.build_ge_trailer(1, control_num))
        output.append(self.build_iea_trailer(1, control_num))

        return "".join(output)