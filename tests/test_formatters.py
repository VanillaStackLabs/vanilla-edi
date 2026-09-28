from utils.formatters import safe_float, safe_int, pad_left_zero, pad_right


def test_safe_float():
    assert safe_float(" 12.50 ") == 12.5
    assert safe_float("-5.99") == -5.99
    assert safe_float("0") == 0.0

    # Edge Cases
    assert safe_float("", default=1.0) == 1.0
    assert safe_float("ABC", default=0.0) == 0.0
    assert safe_float(None, default=5.0) == 5.0


def test_safe_int():
    assert safe_int(" 12 ") == 12
    assert safe_int("-5") == -5

    # Casting floats in string format to int
    assert safe_int("12.50") == 12

    # Edge Cases
    assert safe_int("", default=1) == 1
    assert safe_int("ABC", default=0) == 0
    assert safe_int(None, default=5) == 5

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

