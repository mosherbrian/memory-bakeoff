MAX_PERCENT = 100


def opening_percent(raw: int) -> int:
    if raw > MAX_PERCENT:
        return MAX_PERCENT
    return raw
