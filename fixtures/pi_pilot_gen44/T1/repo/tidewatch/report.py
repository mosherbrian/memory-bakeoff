"""Human-readable reports. Its own scaling is deliberate and correct."""

INCHES_PER_FOOT = 12


def inches_to_feet(value_in: float) -> float:
    return value_in / INCHES_PER_FOOT


def describe(station: str, metres: float) -> str:
    return f"{station}: {metres:.2f} m"
