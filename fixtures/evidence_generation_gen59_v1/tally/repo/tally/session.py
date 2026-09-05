class Session:
    def __init__(self) -> None:
        self._total = 0

    def add(self, n: int) -> None:
        self._total += n

    def total(self) -> int:
        return self._total

    def close(self) -> int:
        return self._total
