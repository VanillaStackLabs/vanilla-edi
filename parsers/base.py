from typing import List, Tuple, Optional


class BaseParser:
    """Base class for all X12 document parsers."""
    transaction_code: str = ""  # Overridden by subclasses (e.g. "850", "810")

    def __init__(self, segments: List[str], element_sep: str):
        self.segments = segments
        self.element_sep = element_sep

    @property
    def envelope(self) -> dict:
        """Dynamically parses and returns header envelope metadata."""
        return parse_envelope_headers(self.segments, self.element_sep)

    def parse(self) -> dict:
        raise NotImplementedError("Subclasses must implement parse()")

    @classmethod
    def get_parser_for(cls, transaction_type: str) -> Optional['BaseParser']:
        """Recursively finds the subclass registered for a transaction code."""
        for subclass in cls.__subclasses__():
            if subclass.transaction_code == transaction_type:
                return subclass
        return None


def extract_delimiters(raw_edi_text: str) -> tuple[str, str]:
    """
    Extracts element separator and segment terminator dynamically from ISA header.
    Dynamically finds the segment terminator after ISA16 (Component Element Separator).
    """
    clean_text = raw_edi_text.lstrip()
    if clean_text.startswith("ISA") and len(clean_text) >= 4:
        element_sep = clean_text[3]
        elements = clean_text.split(element_sep)

        if len(elements) > 16 and len(elements[16]) >= 2:
            segment_term = elements[16][1]
            return element_sep, segment_term

        return element_sep, "~"

    return "*", "~"


def parse_envelope_headers(segments: list, element_sep: str) -> dict:
    """Extracts common ISA and ST header envelope metadata."""
    envelope = {
        "sender_id": "",
        "receiver_id": "",
        "control_number": "",
        "transaction_type": "Unknown"
    }

    for segment in segments:
        elements = segment.split(element_sep)
        tag = elements[0]

        if tag == "ISA" and len(elements) >= 14:
            envelope["sender_id"] = elements[6].strip()
            envelope["receiver_id"] = elements[8].strip()
            envelope["control_number"] = elements[13].strip()

        elif tag == "ST" and len(elements) >= 2:
            envelope["transaction_type"] = elements[1].strip()

    return envelope


def safe_float(value: str, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value.strip())
    except (ValueError, TypeError, AttributeError):
        return default

def safe_int(value: str, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError, AttributeError):
        return default