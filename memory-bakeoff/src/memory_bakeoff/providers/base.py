from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Sequence

from memory_bakeoff.models import (
    FeedbackEvent,
    MemoryRecord,
    ProviderCapabilities,
    ProviderProbe,
    QueryCase,
    RetrievalItem,
    RetrievalResult,
)


class ProviderUnavailable(RuntimeError):
    pass


class MemoryProvider(ABC):
    name: str
    capabilities: ProviderCapabilities

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    @abstractmethod
    def reset(self) -> None:
        ...

    @abstractmethod
    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        ...

    @abstractmethod
    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        ...

    def feedback(self, event: FeedbackEvent) -> None:
        return None

    def probe(self) -> ProviderProbe:
        return ProviderProbe(self.name, True, "available", self.capabilities)

    def remember_records(self, records: Sequence[MemoryRecord]) -> None:
        self._records.update({r.id: r for r in records})

    def resolve_record_id(self, text: str, explicit_id: str | None = None) -> str | None:
        if explicit_id and explicit_id in self._records:
            return explicit_id
        # Some adapters intentionally include an invisible-ish stable marker in metadata,
        # but never rely on it being surfaced by the engine.
        m = re.search(r"\b(M\d{3})\b", text)
        if m and m.group(1) in self._records:
            return m.group(1)
        norm = " ".join(text.lower().split())
        best: tuple[int, str] | None = None
        for rid, record in self._records.items():
            rnorm = " ".join(record.text.lower().split())
            if rnorm and (rnorm in norm or norm in rnorm):
                score = min(len(rnorm), len(norm))
                if best is None or score > best[0]:
                    best = (score, rid)
        return best[1] if best else None

    def normalize_items(self, texts: Sequence[str], scores: Sequence[float | None] | None = None) -> list[RetrievalItem]:
        out: list[RetrievalItem] = []
        scores = scores or [None] * len(texts)
        for text, score in zip(texts, scores):
            out.append(RetrievalItem(record_id=self.resolve_record_id(text), text=text, score=score))
        return out
