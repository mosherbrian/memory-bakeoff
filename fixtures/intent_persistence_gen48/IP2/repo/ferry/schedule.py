"""Sailing schedule."""

SAILINGS = ["06:00", "07:30", "09:00", "10:30"]


def next_sailing(after: str) -> str:
    for sailing in SAILINGS:
        if sailing > after:
            return sailing
    return SAILINGS[0]


def as_list() -> list:
    """Public: the crew rota tool reads this and expects a list of strings."""
    return list(SAILINGS)
