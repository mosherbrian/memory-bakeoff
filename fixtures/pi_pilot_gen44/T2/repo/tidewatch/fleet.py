from tidewatch.station import Station


class Fleet:
    def __init__(self):
        self.stations = {}

    def add(self, name: str, datum_m: float) -> None:
        self.stations[name] = Station(name, datum_m)

    def level(self, name: str, reading_m: float) -> float:
        return self.stations[name].level(reading_m)
