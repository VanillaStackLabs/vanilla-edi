import pytest
from edi_parser import extract_transaction_type, parse_x12_to_dict


def test_extract_transaction_type_standard_st():
    segments = ["ST*850*0001", "BEG*00*SA*123"]
    assert extract_transaction_type(segments, "*") == "850"


def test_extract_transaction_type_inferred_tags():
    # Tests the fallback inference from unique starting tags
    assert extract_transaction_type(["BEG*00*SA*123"], "*") == "850"
    assert extract_transaction_type(["BIG*20260928*INV123"], "*") == "810"
    assert extract_transaction_type(["BSN*00*SHIP123"], "*") == "856"
    assert extract_transaction_type(["AK1*PO*001"], "*") == "997"


def test_extract_transaction_type_unknown():
    # Tests the fallback for entirely unrecognized segments
    segments = ["ISA*00*", "GS*PO*", "UNK*123*456"]
    assert extract_transaction_type(segments, "*") == "Unknown"


def test_parse_x12_to_dict_unsupported():
    # Verifies the fallback dictionary structure for unsupported types
    raw_edi = "ST*999*0001~\nSE*2*0001~"
    data = parse_x12_to_dict(raw_edi)

    assert data["transaction_type"] == "999"
    assert data["status"] == "unsupported_transaction_set"
    assert "is not yet supported" in data["message"]
    assert data["segment_count"] == 2