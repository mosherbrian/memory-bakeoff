from __future__ import annotations

import time
from typing import Sequence

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider
from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.providers.dense import DenseLSAProvider


class HybridRRFProvider(MemoryProvider):
    name = "hybrid_rrf"
    raw_experiment_class = "baseline"
    product_experiment_class = "baseline"
    capabilities = ProviderCapabilities(raw_ingest=True, product_ingest=True, supports_as_of=True, notes="BM25 + dense LSA fused with reciprocal-rank fusion.")

    def __init__(self, rrf_k: int = 60):
        super().__init__(); self.rrf_k=rrf_k; self.bm=BM25Provider(); self.dense=DenseLSAProvider()

    def reset(self): self._records.clear(); self.bm.reset(); self.dense.reset()
    def ingest(self, records: Sequence[MemoryRecord], mode: str="raw"):
        self.reset(); self.remember_records(records); self.bm.ingest(records,mode); self.dense.ingest(records,mode)

    def retrieve(self, case: QueryCase, top_k: int=5) -> RetrievalResult:
        t0=time.perf_counter(); a=self.bm.retrieve(case, max(top_k*4,20)); b=self.dense.retrieve(case,max(top_k*4,20)); scores={}; texts={}
        for result in (a,b):
            for rank,item in enumerate(result.items,1):
                if not item.record_id: continue
                scores[item.record_id]=scores.get(item.record_id,0.0)+1/(self.rrf_k+rank); texts[item.record_id]=item.text
        ranked=sorted(scores.items(), key=lambda x:x[1], reverse=True)[:top_k]
        return RetrievalResult([RetrievalItem(rid,texts[rid],score) for rid,score in ranked],(time.perf_counter()-t0)*1000)
