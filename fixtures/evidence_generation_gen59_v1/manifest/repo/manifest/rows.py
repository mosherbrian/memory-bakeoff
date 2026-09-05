FIELDS = ("code", "label", "depot")


def parse_row(line: str) -> dict:
    parts = line.split(",")
    return {name: parts[index] for index, name in enumerate(FIELDS)}
