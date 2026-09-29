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
    Uses strict 106-character positional indexing as required by ANSI X12.
    """
    clean_text = raw_edi_text.lstrip('\ufeff \t\r\n')

    # Fallback to defaults if the file is severely truncated or not EDI
    if not clean_text.startswith("ISA") or len(clean_text) < 106:
        return "*", "~"

    # In a standard ISA segment, index 3 is strictly the element separator
    element_sep = clean_text[3]

    # Index 105 is strictly the segment terminator
    segment_term = clean_text[105]

    return element_sep, segment_term

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
