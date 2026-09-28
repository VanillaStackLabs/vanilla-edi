def pad_right(val: str, length: int) -> str:
    """Pads string with trailing spaces to exact length (ISA requirement)."""
    return (val or "")[:length].ljust(length)


def pad_left_zero(val: str, length: int) -> str:
    """Pads control numbers with leading zeros to exact length."""
    return (val or "1")[:length].zfill(length)


def safe_float(value: str, default: float = 0.0) -> float:
    """Safely converts string to float, handling None and invalid formats."""
    if value is None:
        return default
    try:
        return float(value.strip())
    except (ValueError, TypeError, AttributeError):
        return default


def safe_int(value: str, default: int = 0) -> int:
    """Safely converts string to int, handling None, floats, and invalid formats."""
    if value is None:
        return default
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError, AttributeError):
        return default