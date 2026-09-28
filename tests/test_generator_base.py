import pytest
from datetime import datetime
from generators.base import pad_right, pad_left_zero, BaseGenerator


# --- Padding Utility Tests ---
def test_pad_right_standard():
    # Pads string with trailing spaces to exact length
    assert pad_right("SENDER", 10) == "SENDER    "


def test_pad_right_truncation():
    # Truncates if the provided string exceeds the target length
    assert pad_right("SENDER123456", 10) == "SENDER1234"


def test_pad_right_empty():
    assert pad_right(None, 5) == "     "
    assert pad_right("", 5) == "     "


def test_pad_left_zero_standard():
    # Pads control numbers with leading zeros
    assert pad_left_zero("123", 9) == "000000123"


def test_pad_left_zero_truncation():
    # Truncates if the provided string exceeds the target length
    assert pad_left_zero("1234567890", 9) == "123456789"


def test_pad_left_zero_empty_default():
    # Defaults to "1" if None or empty string is provided
    assert pad_left_zero(None, 4) == "0001"
    assert pad_left_zero("", 4) == "0001"


# --- BaseGenerator Tests ---
@pytest.fixture
def test_dt():
    return datetime(2026, 9, 28, 13, 46)


def test_build_isa_header(test_dt):
    # Initializes with default element_sep "*" and segment_term "~\n"
    gen = BaseGenerator()
    isa = gen.build_isa_header("COMPANY_A", "PARTNER_B", "45", test_dt)

    # Verifies standard ISA envelope formatting, 15-char ID padding, and 9-digit control numbers
    assert isa.startswith("ISA*00*          *00*          *ZZ*COMPANY_A      *ZZ*PARTNER_B      *")
    # Verifies 2-digit year format (%y%m%d) and time (%H%M)
    assert "*260928*1346*U*00401*000000045*0*P*>~\n" in isa

    elements = isa.split("*")
    assert len(elements[6]) == 15  # Sender ID field exact length
    assert len(elements[8]) == 15  # Receiver ID field exact length


def test_build_gs_header(test_dt):
    gen = BaseGenerator()
    gs = gen.build_gs_header("PO", "COMPANY_A", "PARTNER_B", "45", test_dt)

    # Verifies 4-digit year format (%Y%m%d) for GS headers
    expected = "GS*PO*COMPANY_A*PARTNER_B*20260928*1346*45*X*004010~\n"
    assert gs == expected


def test_build_ge_trailer():
    gen = BaseGenerator()
    ge = gen.build_ge_trailer(3, "45")

    expected = "GE*3*45~\n"
    assert ge == expected


def test_build_iea_trailer():
    gen = BaseGenerator()
    iea = gen.build_iea_trailer(1, "45")

    # Verifies IEA control number uses 9-digit zero padding
    expected = "IEA*1*000000045~\n"
    assert iea == expected


def test_custom_delimiters(test_dt):
    # Verifies the generator handles custom delimiters injected during initialization
    gen = BaseGenerator(element_sep="|", segment_term="^")

    ge = gen.build_ge_trailer(3, "45")
    assert ge == "GE|3|45^"

    iea = gen.build_iea_trailer(1, "45")
    assert iea == "IEA|1|000000045^"

    gs = gen.build_gs_header("PO", "SENDER", "RECEIVER", "1", test_dt)
    assert gs.startswith("GS|PO|SENDER|RECEIVER|20260928|1346|1|X|004010^")