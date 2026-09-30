import pytest
from parsers.base import (
    BaseParser,
    extract_delimiters,
    parse_envelope_headers,
)


# --- Helper Class for Testing BaseParser ---
class MockParser(BaseParser):
    transaction_code = "MOCK"

    def parse(self):
        return {"status": "success"}


# --- extract_delimiters Tests ---
def test_extract_delimiters_standard():
    edi_text = "ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260928*1000*U*00401*000000001*0*P*>~\n"
    element_sep, segment_term = extract_delimiters(edi_text)
    assert element_sep == "*"
    assert segment_term == "~"


def test_extract_delimiters_custom():
    edi_text = "ISA|00|          |00|          |ZZ|SENDER         |ZZ|RECEIVER       |260928|1000|U|00401|000000001|0|P|>\n"
    element_sep, segment_term = extract_delimiters(edi_text)
    assert element_sep == "|"
    assert segment_term == "\n"


def test_extract_delimiters_fallback():
    edi_text = "ST*850*0001~"
    element_sep, segment_term = extract_delimiters(edi_text)
    assert element_sep == "*"
    assert segment_term == "~"


# --- parse_envelope_headers Tests ---
def test_parse_envelope_headers():
    segments = [
        "ISA*00*          *00*          *ZZ*SENDER ID      *ZZ*RECEIVER ID    *260928*1000*U*00401*123456789*0*P*>",
        "GS*PO*SENDER*RECEIVER*20260928*1000*1*X*004010",
        "ST*850*0001"
    ]
    envelope = parse_envelope_headers(segments, "*")
    assert envelope["sender_id"] == "SENDER ID"
    assert envelope["receiver_id"] == "RECEIVER ID"
    assert envelope["control_number"] == "123456789"
    assert envelope["transaction_type"] == "850"


def test_parse_envelope_headers_missing_isa():
    segments = ["ST*810*0001"]
    envelope = parse_envelope_headers(segments, "*")
    assert envelope["sender_id"] == ""
    assert envelope["transaction_type"] == "810"


# --- BaseParser Subclass Discovery Tests ---
def test_get_parser_for_existing():
    parser_class = BaseParser.get_parser_for("MOCK")
    assert parser_class is MockParser

    # Instantiate and call parse() to execute line 13 inside MockParser!
    instance = parser_class(segments=[], element_sep="*")
    assert instance.parse() == {"status": "success"}


def test_get_parser_for_missing():
    parser_class = BaseParser.get_parser_for("000")
    assert parser_class is None


def test_base_parser_enforces_implementation():
    parser = BaseParser(segments=["ST*888*0001"], element_sep="*")
    with pytest.raises(NotImplementedError):
        parser.parse()


def test_get_parser_for_nested_subclass():
    class SubMockParser(MockParser):
        transaction_code = "SUBMOCK"

    parser_class = BaseParser.get_parser_for("SUBMOCK")
    assert parser_class is SubMockParser

    instance = parser_class(segments=[], element_sep="*")
    assert instance.parse() == {"status": "success"}