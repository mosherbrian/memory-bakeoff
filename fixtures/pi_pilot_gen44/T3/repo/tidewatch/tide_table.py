"""Tide table lookups."""

SLOTS = 48


def slot_for(minutes_after_midnight: int) -> int:
    """Which half-hour slot a timestamp falls in."""
    return minutes_after_midnight // 30


def label(slot: int) -> str:
    hour, half = divmod(slot, 2)
    return f"{hour:02d}:{'00' if half else '30'}"
