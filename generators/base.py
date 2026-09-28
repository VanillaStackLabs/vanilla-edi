from datetime import datetime

def pad_right(val: str, length: int) -> str:
    """Pads string with trailing spaces to exact length (ISA requirement)."""
    return (val or "")[:length].ljust(length)


def pad_left_zero(val: str, length: int) -> str:
    """Pads control numbers with leading zeros to exact length."""
    return (val or "1")[:length].zfill(length)


class BaseGenerator:
    """Handles ISA/GS envelope formatting and segment counting."""

    def __init__(self, element_sep: str = "*", segment_term: str = "~\n"):
        self.element_sep = element_sep
        self.segment_term = segment_term

    def build_isa_header(self, sender_id: str, receiver_id: str, control_num: str, dt: datetime) -> str:
        date_str = dt.strftime("%y%m%d")
        time_str = dt.strftime("%H%M")
        ctrl_str = pad_left_zero(control_num, 9)

        isa_elements = [
            "ISA",
            "00",
            pad_right("", 10),
            "00",
            pad_right("", 10),
            "ZZ",
            pad_right(sender_id, 15),
            "ZZ",
            pad_right(receiver_id, 15),
            date_str,
            time_str,
            "U",
            "00401",
            ctrl_str,
            "0",
            "P",
            ">",
        ]
        return self.element_sep.join(isa_elements) + self.segment_term

    def build_gs_header(self, group_code: str, sender_id: str, receiver_id: str, control_num: str, dt: datetime) -> str:
        date_str = dt.strftime("%Y%m%d")
        time_str = dt.strftime("%H%M")

        gs_elements = [
            "GS",
            group_code,
            sender_id,
            receiver_id,
            date_str,
            time_str,
            control_num,
            "X",
            "004010",
        ]
        return self.element_sep.join(gs_elements) + self.segment_term

    def build_ge_trailer(self, tx_count: int, control_num: str) -> str:
        return f"GE{self.element_sep}{tx_count}{self.element_sep}{control_num}{self.segment_term}"

    def build_iea_trailer(self, group_count: int, control_num: str) -> str:
        ctrl_str = pad_left_zero(control_num, 9)
        return f"IEA{self.element_sep}{group_count}{self.element_sep}{ctrl_str}{self.segment_term}"