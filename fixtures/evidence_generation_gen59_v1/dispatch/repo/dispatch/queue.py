class Queue:
    def __init__(self) -> None:
        self._jobs = []

    def push(self, name: str, urgent: bool = False) -> None:
        self._jobs.append(name)

    def pop(self) -> str:
        return self._jobs.pop(0)
