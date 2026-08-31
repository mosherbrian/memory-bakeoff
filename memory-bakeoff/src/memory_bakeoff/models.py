from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Iterable


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    text: str
    timestamp: datetime
    session_id: str
    scope: str = "repo:demo"
    metadata: dict[str, Any] = field(default_factory=dict)
    supersedes_id: str | None = None
    outcome: str | None = None  # success | failure | neutral

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


@dataclass(frozen=True)
class QueryCase:
    id: str
    category: str
    query: str
    relevant_ids: tuple[str, ...]
    prohibited_ids: tuple[str, ...] = ()
    scope: str = "repo:demo"
    as_of: datetime | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["as_of"] = self.as_of.isoformat() if self.as_of else None
        return d


@dataclass
class RetrievalItem:
    record_id: str | None
    text: str
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    items: list[RetrievalItem]
    latency_ms: float
    raw: Any = None

    @property
    def ids(self) -> list[str]:
        return [x.record_id for x in self.items if x.record_id]


@dataclass(frozen=True)
class FeedbackEvent:
    query_id: str
    retrieved_ids: tuple[str, ...]
    useful_ids: tuple[str, ...]
    harmful_ids: tuple[str, ...] = ()
    verified: bool = True
    reward: float = 1.0


@dataclass(frozen=True)
class ProviderCapabilities:
    raw_ingest: bool
    product_ingest: bool
    requires_llm_for_product_ingest: bool = False
    supports_as_of: bool = False
    supports_feedback: bool = False
    service_required: bool = False
    notes: str = ""


@dataclass
class ProviderProbe:
    name: str
    available: bool
    reason: str
    capabilities: ProviderCapabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self.available,
            "reason": self.reason,
            "capabilities": asdict(self.capabilities),
        }


def unique_in_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out
