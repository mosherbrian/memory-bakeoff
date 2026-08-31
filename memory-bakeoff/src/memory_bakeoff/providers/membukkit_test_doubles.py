"""Deterministic model doubles copied from MemBukkit upstream test_union_parity.py.

These deliberately test MemBukkit's production structural retrieval path without
claiming to represent the quality of its pretrained encoder/reranker weights.
"""
from __future__ import annotations

import hashlib
import numpy as np


def _shash(s, mod: int) -> int:
    """Process-stable hash (Python's builtin hash() is salted per run)."""
    return int(hashlib.sha1(str(s).encode()).hexdigest(), 16) % mod


class FakeEncoder:
    """Deterministic encoder accepting BOTH call conventions (backend + CLI)."""

    def __init__(self, dim: int = 32):
        self.dim = dim

    def encode(
        self,
        texts,
        normalize=True,
        normalize_embeddings=None,
        show_progress=False,
        show_progress_bar=False,
        **_,
    ):
        single = isinstance(texts, str)
        items = [texts] if single else list(texts)
        vecs = []
        for t in items:
            rng = np.random.default_rng(_shash(t, 2**32))
            v = rng.standard_normal(self.dim).astype(np.float32)
            v /= np.linalg.norm(v) + 1e-8
            vecs.append(v)
        out = np.vstack(vecs).astype(np.float32)
        return out[0] if single else out


class FakeReranker:
    """Deterministic cross-encoder: token overlap + a stable hash tiebreak."""

    def score(self, query, texts, batch_size: int = 64):
        qs = set(query.lower().split())
        out = []
        for t in texts:
            overlap = len(qs & set(t.lower().split()))
            jitter = _shash(t, 1000) / 1e6
            out.append(overlap + jitter)
        return np.asarray(out, dtype=np.float32)

class SharedLSAEncoder:
    """Corpus-fit LSA encoder matching the benchmark DenseLSA baseline representation."""

    def __init__(self, texts, dimensions: int = 32):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.preprocessing import normalize
        self._normalize = normalize
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        X = self.vectorizer.fit_transform(list(texts))
        max_dim = max(1, min(dimensions, X.shape[0] - 1, X.shape[1] - 1))
        self.svd = TruncatedSVD(n_components=max_dim, random_state=0)
        self.svd.fit(X)
        self.dim = max_dim

    def encode(self, texts, normalize=True, normalize_embeddings=None, **_):
        single = isinstance(texts, str)
        items = [texts] if single else list(texts)
        X = self.vectorizer.transform(items)
        out = self.svd.transform(X)
        if normalize or normalize_embeddings:
            out = self._normalize(out)
        out = np.asarray(out, dtype=np.float32)
        return out[0] if single else out
