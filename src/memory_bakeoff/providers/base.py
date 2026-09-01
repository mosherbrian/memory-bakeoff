from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import Counter
from typing import Sequence

from memory_bakeoff.models import (
    FeedbackEvent,
    EXPERIMENT_CLASSES,
    ExperimentClass,
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
    raw_experiment_class: ExperimentClass = "raw_product"
    product_experiment_class: ExperimentClass = "product"

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._provenance_methods: Counter[str] = Counter()

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

    def close(self) -> None:
        """Release provider resources after one benchmark run.

        Most in-process providers have nothing to close. Service-backed providers
        may override this to close client sessions before the harness records its
        completed result.
        """
        return None

    def configuration(self) -> dict:
        """Return non-secret, reproducibility-relevant provider settings."""
        return {}

    def diagnostics(self) -> dict:
        """Return non-scoring, provider-native diagnostic evidence for this run."""
        return {}

    def probe(self) -> ProviderProbe:
        return ProviderProbe(self.name, True, "available", self.capabilities)

    def remember_records(self, records: Sequence[MemoryRecord]) -> None:
        self._records.update({r.id: r for r in records})
        self._provenance_methods.clear()

    def experiment_class(self, mode: str) -> ExperimentClass:
        if mode not in ("raw", "product"):
            raise ValueError(f"invalid ingestion mode for {self.name}: {mode}")
        value = self.raw_experiment_class if mode == "raw" else self.product_experiment_class
        if value not in EXPERIMENT_CLASSES:
            raise ValueError(f"invalid experiment class for {self.name}: {value}")
        return value

    def _record_provenance(self, method: str) -> None:
        self._provenance_methods[method] += 1

    def provenance_report(self) -> dict:
        methods = dict(sorted(self._provenance_methods.items()))
        if not methods:
            return {
                "status": "native_by_construction",
                "publishable": True,
                "methods": {},
                "reason": "adapter returns canonical benchmark record IDs without text reconciliation",
            }
        unsafe = [name for name in ("fuzzy_subtext", "unmapped") if methods.get(name)]
        if unsafe:
            return {
                "status": "exploratory_only",
                "publishable": False,
                "methods": methods,
                "reason": "fuzzy/subtext or unmapped provenance cannot establish canonical source identity",
            }
        return {
            "status": "verified",
            "publishable": True,
            "methods": methods,
            "reason": "all returned evidence used native IDs or exact canonical markers",
        }

    def resolve_record_id(self, text: str, explicit_id: str | None = None) -> str | None:
        if explicit_id and explicit_id in self._records:
            self._record_provenance("native")
            return explicit_id
        # Some adapters intentionally include an invisible-ish stable marker in metadata,
        # but never rely on it being surfaced by the engine.
        m = re.search(r"\b(M\d{3})\b", text)
        if m and m.group(1) in self._records:
            self._record_provenance("canonical_marker")
            return m.group(1)
        norm = " ".join(text.lower().split())
        best: tuple[int, str] | None = None
        for rid, record in self._records.items():
            rnorm = " ".join(record.text.lower().split())
            if rnorm and (rnorm in norm or norm in rnorm):
                score = min(len(rnorm), len(norm))
                if best is None or score > best[0]:
                    best = (score, rid)
        if best:
            self._record_provenance("fuzzy_subtext")
            return best[1]
        self._record_provenance("unmapped")
        return None

    def normalize_items(self, texts: Sequence[str], scores: Sequence[float | None] | None = None) -> list[RetrievalItem]:
        out: list[RetrievalItem] = []
        scores = scores or [None] * len(texts)
        for text, score in zip(texts, scores):
            out.append(RetrievalItem(record_id=self.resolve_record_id(text), text=text, score=score))
        return out
