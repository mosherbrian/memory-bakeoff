from __future__ import annotations

import math
import re
import time
from collections import Counter
from typing import Sequence

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider

TOKEN_RE = re.compile(r"[A-Za-z0-9_./:-]+")


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


class BM25Provider(MemoryProvider):
    name = "bm25"
    capabilities = ProviderCapabilities(raw_ingest=True, product_ingest=True, supports_as_of=True, notes="Pure-Python BM25 baseline. Uses structured as-of cutoff when supplied; scope must be resolved from query text.")

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        super().__init__()
        self.k1, self.b = k1, b
        self.docs: list[MemoryRecord] = []
        self.tf: list[Counter[str]] = []
        self.df: Counter[str] = Counter()
        self.avgdl = 0.0

    def reset(self) -> None:
        self._records.clear(); self.docs=[]; self.tf=[]; self.df=Counter(); self.avgdl=0.0

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        self.reset(); self.remember_records(records); self.docs=list(records)
        lengths=[]
        for r in self.docs:
            toks=tokenize(r.text); c=Counter(toks); self.tf.append(c); lengths.append(len(toks)); self.df.update(c.keys())
        self.avgdl=sum(lengths)/len(lengths) if lengths else 0.0

    def _score(self, query: str, idx: int) -> float:
        q=tokenize(query); tf=self.tf[idx]; dl=sum(tf.values()); n=len(self.docs); s=0.0
        for term in q:
            if term not in tf: continue
            df=self.df[term]; idf=math.log(1+(n-df+0.5)/(df+0.5)); f=tf[term]
            denom=f+self.k1*(1-self.b+self.b*(dl/self.avgdl if self.avgdl else 0))
            s += idf*(f*(self.k1+1)/denom)
        return s

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        t0=time.perf_counter()
        scored=[]
        for i,r in enumerate(self.docs):
            if case.as_of and r.timestamp > case.as_of: continue
            s=self._score(case.query, i)
            if s>0: scored.append((s,r))
        scored.sort(key=lambda x:(x[0], x[1].timestamp), reverse=True)
        items=[RetrievalItem(r.id,r.text,float(s),{"timestamp":r.timestamp.isoformat()}) for s,r in scored[:top_k]]
        return RetrievalResult(items,(time.perf_counter()-t0)*1000)
