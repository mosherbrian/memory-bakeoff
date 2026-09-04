from tally.counter import totals


def summary(items: list) -> str:
    return ", ".join(f"{hold}={count}" for hold, count in totals(items).items())
