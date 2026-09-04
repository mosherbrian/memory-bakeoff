"""Gauge readings for the tidewatch stations."""
from tidewatch.units import cm_to_m


class Gauge:
    def __init__(self, station: str):
        self.station = station

    def read(self, raw_cm: float) -> float:
        """Return the reading in metres."""
        return cm_to_m(raw_cm)
