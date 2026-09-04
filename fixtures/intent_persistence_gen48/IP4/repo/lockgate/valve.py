"""Valve control."""

MAX_OPEN = 100


def clamp(value: int) -> int:
    if value > MAX_OPEN:
        return MAX_OPEN
    return value
