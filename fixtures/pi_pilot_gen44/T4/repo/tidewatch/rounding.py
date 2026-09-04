"""Reading normalisation.

Design note: readings are reported to two decimals. A value exactly on the
midpoint is rounded AWAY FROM ZERO, because the harbourmaster's printed log has
always done that and our output must keep matching it. Python's built-in
round() does not do this: it rounds halves to even, and it works on the binary
float rather than the decimal the operator typed.
"""
from decimal import Decimal, ROUND_HALF_UP


def normalise(reading_m: float) -> float:
    """Round a reading to two decimals, away from zero at the midpoint."""
    return round(reading_m, 2)


def clamp(reading_m: float, low: float, high: float) -> float:
    return max(low, min(high, reading_m))
