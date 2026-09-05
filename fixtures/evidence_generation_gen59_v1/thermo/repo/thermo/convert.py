def to_fahrenheit(celsius: float, places: int = 2) -> float:
    return round(celsius * 9 / 5 + 32, places)
