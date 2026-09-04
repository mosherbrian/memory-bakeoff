"""Telemetry frames sent to the control room."""
from sluice.units import to_steps


def frame(position_mm: int) -> dict:
    return {"steps": to_steps(position_mm), "unit": "steps"}
