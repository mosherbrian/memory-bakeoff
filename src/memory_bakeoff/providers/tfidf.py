from __future__ import annotations

import time
from typing import Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider


class TfidfCosineProvider(MemoryProvider):
    """Deterministic sparse TF-IDF cosine baseline.

    Deliberately boring. It preserves rare exact identifiers better than a low-rank LSA
    projection and is included because simple lexical baselines are often surprisingly
    competitive on memory benchmarks.
    """

    name = "tfidf_cosine"
    raw_experiment_class = "baseline"
    product_experiment_class = "baseline"
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=True,
        supports_as_of=True,
        notes="Sparse word/bigram TF-IDF cosine baseline; deterministic and no pretrained model.",
    )

    def __init__(self):
        super().__init__()
        self.docs: list[MemoryRecord] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None

    def reset(self) -> None:
        self._records.clear()
        self.docs = []
        self.vectorizer = None
        self.matrix = None

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        self.reset()
        self.remember_records(records)
        self.docs = list(records)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
            norm="l2",
        )
        self.matrix = self.vectorizer.fit_transform([r.text for r in self.docs])

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        assert self.vectorizer is not None and self.matrix is not None
        t0 = time.perf_counter()
        q = self.vectorizer.transform([case.query])
        # TfidfVectorizer output is already L2-normalized by default, so dot product is cosine.
        sims = (self.matrix @ q.T).toarray().ravel()
        scored = []
        for record, score in zip(self.docs, sims, strict=True):
            if case.as_of and record.timestamp > case.as_of:
                continue
            if float(score) > 0:
                scored.append((float(score), record))
        scored.sort(key=lambda x: (x[0], x[1].timestamp), reverse=True)
        items = [
            RetrievalItem(r.id, r.text, score, {"timestamp": r.timestamp.isoformat()})
            for score, r in scored[:top_k]
        ]
        return RetrievalResult(items, (time.perf_counter() - t0) * 1000)
