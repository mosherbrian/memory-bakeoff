"""Unit conversions for harbour gauge readings."""

CENTIMETRES_PER_METRE = 10


def cm_to_m(value_cm: float) -> float:
    return value_cm / CENTIMETRES_PER_METRE


def m_to_cm(value_m: float) -> float:
    return value_m * CENTIMETRES_PER_METRE
