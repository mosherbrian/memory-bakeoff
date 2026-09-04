from tidewatch.fleet import Fleet


def summarise(fleet: Fleet, readings: dict) -> dict:
    return {name: fleet.level(name, value) for name, value in readings.items()}
