from culvert.units import to_steps


def frame(millimetres: int) -> dict:
    return {"mm": millimetres, "steps": to_steps(millimetres)}
