from datetime import datetime
from generators.base import BaseGenerator

class Generator997(BaseGenerator):

    def generate(self, payload: dict) -> str:
        dt = datetime.now()
        sender = payload.get("sender_id", "MYCOMPANY")
        receiver = payload.get("receiver_id", "TRADINGPARTNER")
        control_num = str(payload.get("control_number", "1"))

        ack_group = payload.get("acknowledged_functional_group", "PO")
        ack_group_control = str(payload.get("acknowledged_group_control_number", "1"))
        ack_status = payload.get("acknowledgment_status", "A")

        segments = []

        # Outer Envelopes
        segments.append(self.build_isa_header(sender, receiver, control_num, dt))
        segments.append(self.build_gs_header("FA", sender, receiver, control_num, dt))

        # ST Header
        tx_control = "0001"
        segments.append(f"ST{self.element_sep}997{self.element_sep}{tx_control}{self.segment_term}")

        # AK1 - Group Header
        segments.append(f"AK1{self.element_sep}{ack_group}{self.element_sep}{ack_group_control}{self.segment_term}")

        # Transaction Set Detail Loops (AK2 -> AK5)
        tx_acks = payload.get("transaction_set_acknowledgments", [])
        for tx in tx_acks:
            tx_type = tx.get("transaction_type", "850")
            tx_ctrl = str(tx.get("control_number", "0001"))
            tx_stat = tx.get("status", "A")

            segments.append(f"AK2{self.element_sep}{tx_type}{self.element_sep}{tx_ctrl}{self.segment_term}")

            for err in tx.get("errors", []):
                seg_id = err.get("segment_id", "")
                seg_pos = str(err.get("segment_position", "0"))
                err_code = str(err.get("error_code", "1"))

                segments.append(
                    f"AK3{self.element_sep}{seg_id}{self.element_sep}{seg_pos}{self.element_sep}{self.element_sep}{err_code}{self.segment_term}"
                )

                for elem_err in err.get("element_errors", []):
                    elem_pos = str(elem_err.get("element_position", "1"))
                    elem_code = str(elem_err.get("error_code", "1"))
                    bad_val = elem_err.get("bad_value", "")

                    segments.append(
                        f"AK4{self.element_sep}{elem_pos}{self.element_sep}{self.element_sep}{elem_code}{self.element_sep}{bad_val}{self.segment_term}"
                    )

            segments.append(f"AK5{self.element_sep}{tx_stat}{self.segment_term}")

        # AK9 - Group Summary
        totals = payload.get("group_totals", {})
        inc = str(totals.get("included", 1))
        rec = str(totals.get("received", 1))
        acc = str(totals.get("accepted", 1 if ack_status == "A" else 0))

        if ack_status in ["M", "W"]:
            segments.append(f"AK9{self.element_sep}{ack_status}{self.segment_term}")
        else:
            segments.append(f"AK9{self.element_sep}{ack_status}{self.element_sep}{inc}{self.element_sep}{rec}{self.element_sep}{acc}{self.segment_term}")

        # SE Trailer Segment Count
        st_index = next(i for i, s in enumerate(segments) if s.startswith("ST"))
        segment_count = len(segments) - st_index + 1

        segments.append(f"SE{self.element_sep}{segment_count}{self.element_sep}{tx_control}{self.segment_term}")

        # Envelope Trailers
        segments.append(self.build_ge_trailer(1, control_num))
        segments.append(self.build_iea_trailer(1, control_num))

        return "".join(segments)