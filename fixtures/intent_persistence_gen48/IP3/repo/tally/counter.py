"""Counts cargo items per hold."""


def totals(items: list) -> dict:
    counts = {}
    for item in items:
        counts[item["hold"]] = counts.get(item["hold"], 0) + 1
    return counts
