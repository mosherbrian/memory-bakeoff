from __future__ import annotations

import time
from typing import Sequence
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider


class DenseLSAProvider(MemoryProvider):
    name = "dense_lsa"
    raw_experiment_class = "baseline"
    product_experiment_class = "baseline"
    capabilities = ProviderCapabilities(raw_ingest=True, product_ingest=True, supports_as_of=True, notes="Offline deterministic dense LSA baseline; not a pretrained sentence embedding model. Uses structured as-of cutoff when supplied; scope must be resolved from query text.")

    def __init__(self, dimensions: int = 32):
        super().__init__(); self.dimensions=dimensions; self.docs=[]; self.vectorizer=None; self.svd=None; self.matrix=None

    def reset(self):
        self._records.clear(); self.docs=[]; self.vectorizer=None; self.svd=None; self.matrix=None

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        self.reset(); self.remember_records(records); self.docs=list(records)
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, stop_words="english")
        X=self.vectorizer.fit_transform([r.text for r in self.docs])
        max_dim=max(1,min(self.dimensions, X.shape[0]-1, X.shape[1]-1))
        self.svd=TruncatedSVD(n_components=max_dim, random_state=0)
        self.matrix=normalize(self.svd.fit_transform(X))

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        t0=time.perf_counter()
        q=self.vectorizer.transform([case.query]); qv=normalize(self.svd.transform(q))[0]
        sims=self.matrix @ qv
        scored=[]
        for i,(r,s) in enumerate(zip(self.docs,sims)):
            if case.as_of and r.timestamp > case.as_of: continue
            if float(s)>0: scored.append((float(s),r))
        scored.sort(key=lambda x:(x[0],x[1].timestamp), reverse=True)
        items=[RetrievalItem(r.id,r.text,s,{"timestamp":r.timestamp.isoformat()}) for s,r in scored[:top_k]]
        return RetrievalResult(items,(time.perf_counter()-t0)*1000)
