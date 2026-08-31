from __future__ import annotations

from dataclasses import dataclass, asdict
from statistics import mean
from typing import Sequence

from memory_bakeoff.models import QueryCase, RetrievalResult


@dataclass
class CaseMetrics:
    query_id: str
    category: str
    hit_at_k: float
    recall_at_k: float
    precision_at_k: float
    reciprocal_rank: float
    all_relevant_at_k: float
    prohibited_at_k: float
    prohibited_count: int
    useful_before_harmful: float | None
    returned_count: int
    returned_chars: int
    returned_words: int
    latency_ms: float

    def to_dict(self):
        return asdict(self)


def score_case(case: QueryCase, result: RetrievalResult, k: int = 5) -> CaseMetrics:
    ids = result.ids[:k]
    relevant = set(case.relevant_ids)
    prohibited = set(case.prohibited_ids)
    hits = [rid for rid in ids if rid in relevant]
    hit = 1.0 if hits else 0.0
    recall = len(set(hits)) / len(relevant) if relevant else 1.0
    precision = len(hits) / max(1, len(ids)) if relevant else (1.0 if not ids else 0.0)
    rr = 0.0
    if relevant:
        for i, rid in enumerate(ids, 1):
            if rid in relevant:
                rr = 1.0 / i
                break
    else:
        rr = 1.0 if not ids else 0.0
    allrel = (1.0 if relevant.issubset(ids) else 0.0) if relevant else (1.0 if not ids else 0.0)
    prohibited_rate = sum(1 for rid in ids if rid in prohibited) / max(1, len(ids))

    ubh = None
    if relevant and prohibited:
        good_positions = [ids.index(r) for r in relevant if r in ids]
        bad_positions = [ids.index(r) for r in prohibited if r in ids]
        if good_positions:
            ubh = 1.0 if not bad_positions or min(good_positions) < min(bad_positions) else 0.0
        elif bad_positions:
            ubh = 0.0

    return CaseMetrics(
        query_id=case.id,
        category=case.category,
        hit_at_k=hit,
        recall_at_k=recall,
        precision_at_k=precision,
        reciprocal_rank=rr,
        all_relevant_at_k=allrel,
        prohibited_at_k=prohibited_rate,
        prohibited_count=sum(1 for rid in ids if rid in prohibited),
        useful_before_harmful=ubh,
        returned_count=len(ids),
        returned_chars=sum(len(item.text) for item in result.items[:k]),
        returned_words=sum(len(item.text.split()) for item in result.items[:k]),
        latency_ms=result.latency_ms,
    )


def aggregate(rows: Sequence[CaseMetrics], k: int = 5) -> dict[str, float]:
    if not rows:
        return {}
    def avg(field: str) -> float:
        vals = [getattr(r, field) for r in rows if getattr(r, field) is not None]
        return mean(vals) if vals else 0.0
    negatives = [r for r in rows if r.category == "negative"]
    positives = [r for r in rows if r.category != "negative"]
    return {
        "n_cases": float(len(rows)),
        f"hit@{k}": mean(r.hit_at_k for r in positives) if positives else 0.0,
        f"recall@{k}": mean(r.recall_at_k for r in positives) if positives else 0.0,
        f"precision@{k}": mean(r.precision_at_k for r in positives) if positives else 0.0,
        "mrr": mean(r.reciprocal_rank for r in positives) if positives else 0.0,
        f"all_relevant@{k}": mean(r.all_relevant_at_k for r in positives) if positives else 0.0,
        f"prohibited@{k}": mean(r.prohibited_at_k for r in positives) if positives else 0.0,
        "harmful_presence_rate": mean(1.0 if r.prohibited_count > 0 else 0.0 for r in positives) if positives else 0.0,
        "mean_prohibited_count": mean(r.prohibited_count for r in positives) if positives else 0.0,
        "useful_before_harmful": avg("useful_before_harmful"),
        "negative_empty_rate": mean(1.0 if r.returned_count == 0 else 0.0 for r in negatives) if negatives else 0.0,
        "mean_context_chars": mean(r.returned_chars for r in rows),
        "mean_context_words": mean(r.returned_words for r in rows),
        "mean_latency_ms": mean(r.latency_ms for r in rows),
    }
