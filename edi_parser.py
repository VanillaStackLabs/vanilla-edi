import parsers
from parsers.base import BaseParser, extract_delimiters, parse_envelope_headers

def extract_transaction_type(segments: list, element_sep: str) -> str:
    """Finds transaction type from ST segment or infers it from unique starting tags."""
    for segment in segments:
        clean_segment = segment.replace("\n", "").replace("\r", "").strip()
        elements = [e.strip() for e in clean_segment.split(element_sep)]
        tag = elements[0]

        if tag == "ST" and len(elements) >= 2:
            return elements[1]
        elif tag == "BEG":
            return "850"
        elif tag == "BIG":
            return "810"
        elif tag == "BSN":
            return "856"
        elif tag == "AK1":
            return "997"

    return "Unknown"

def parse_x12_to_dict(raw_edi_text: str) -> dict:
    element_sep, segment_term = extract_delimiters(raw_edi_text)
    segments = [
        s.strip() for s in raw_edi_text.split(segment_term) if s.strip()
    ]

    transaction_type = extract_transaction_type(segments, element_sep)
    envelope = parse_envelope_headers(segments, element_sep)

    parser_cls = BaseParser.get_parser_for(transaction_type)

    if parser_cls:
        parser_instance = parser_cls(segments, element_sep)
        return parser_instance.parse()

    return {
        **envelope,
        "transaction_type": transaction_type,
        "status": "unsupported_transaction_set",
        "message": f"Transaction type '{transaction_type}' is not yet supported by VanillaEDI.",
        "segment_count": len(segments),
    }