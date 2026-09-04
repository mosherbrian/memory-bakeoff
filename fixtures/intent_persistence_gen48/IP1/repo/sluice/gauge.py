"""Reads a gate position from the controller."""
from sluice.units import to_millimetres


def position_mm(raw: int) -> int:
    return to_millimetres(raw)
