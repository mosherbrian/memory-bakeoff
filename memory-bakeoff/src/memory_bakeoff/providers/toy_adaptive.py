from __future__ import annotations

from typing import Sequence
from memory_bakeoff.models import FeedbackEvent, MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.hybrid import HybridRRFProvider


class ToyAdaptiveProvider(HybridRRFProvider):
    """Harness diagnostic, NOT an implementation of Habitus.

    Adds deterministic verified feedback bonuses/penalties to a hybrid baseline so we
    can prove the benchmark detects learning over repeated outcomes.
    """
    name = "toy_adaptive_diagnostic"
    capabilities = ProviderCapabilities(raw_ingest=True, product_ingest=False, supports_as_of=True, supports_feedback=True, notes="Harness diagnostic only; proves feedback/learning measurements work. Not Habitus.")

    def __init__(self):
        super().__init__(); self.weights: dict[str,float]={}

    def reset(self):
        super().reset(); self.weights={}

    def retrieve(self, case: QueryCase, top_k: int=5) -> RetrievalResult:
        base=super().retrieve(case, max(top_k*4,20))
        reranked=[]
        for rank,item in enumerate(base.items,1):
            bonus=self.weights.get(item.record_id or "",0.0)
            score=(item.score or 0.0)+0.02*bonus
            reranked.append((score,rank,item))
        reranked.sort(key=lambda x:(x[0],-x[1]),reverse=True)
        base.items=[RetrievalItem(x[2].record_id,x[2].text,x[0],x[2].metadata) for x in reranked[:top_k]]
        return base

    def feedback(self,event:FeedbackEvent)->None:
        if not event.verified: return
        for rid in event.useful_ids: self.weights[rid]=self.weights.get(rid,0.0)+event.reward
        for rid in event.harmful_ids: self.weights[rid]=self.weights.get(rid,0.0)-event.reward
