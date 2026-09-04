"""Unit helpers."""

STEPS_PER_MM = 4


def to_millimetres(steps: int) -> int:
    return steps // STEPS_PER_MM


def to_steps(millimetres: int) -> int:
    return millimetres * STEPS_PER_MM
