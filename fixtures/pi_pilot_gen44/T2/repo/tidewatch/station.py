"""Station records."""


class Station:
    def __init__(self, name: str, datum_m: float):
        self.name = name
        self.datum_m = datum_m

    def level(self, reading_m: float) -> float:
        return reading_m - self.datum_m
