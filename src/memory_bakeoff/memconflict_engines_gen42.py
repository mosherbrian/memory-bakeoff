"""MemBukkit behind the frozen MemConflict engine interface (Gen42).

Kept in its own module so no Gen37 or Gen38 file is touched. The Gen42 runner
registers this engine into the frozen Gen37 procedure, which is then executed
unchanged.

Product identity is the Gen40/41 one: upstream commit f28a2e58, the intended
MemseekAI model pair, and the Gen41 raw-product retrieval configuration with
``union_lanes=("atomic",)``. Device is the product default, which Gen41
established as the historical replication anchor; the engine reads the device
off each constructed model and refuses to run on anything else.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from memory_bakeoff.membukkit_gen41 import CONFIGURATIONS, EXPECTED_RETRIEVAL, record_devices
from memory_bakeoff.providers import membukkit_memconflict as ADAPTER

REQUIRED_DEVICES = {"biencoder": ["mps:0"], "reranker": ["mps:0"]}
NATIVE_TOP_K = 5


class DeviceDrift(RuntimeError):
    """The product did not construct its models on the frozen device."""


class NativeRankMismatch(RuntimeError):
    """The observed relevance order does not hold what the product returned."""


class MemBukkitEngine:
    """One isolated MemBukkit universe per persona, models shared per process.

    The models are stateless, so loading them once and giving every persona a
    fresh ``MemorySystem`` keeps store isolation exact while avoiding two model
    loads per persona.
    """

    _shared: dict[str, Any] = {}

    def __init__(self, persona_id: str, root: Path):
        from membukkit.config import PromptConfig, RetrievalConfig
        from membukkit.pipeline import MemorySystem

        self.persona_id = str(persona_id)
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._ordinal = 0
        self._selected: list = []
        self._pool: list = []
        self._trace: dict = {}
        self.scan_fractions: list[float] = []
        # Per query text: the native ids the router opened, and the native trace.
        # A same-state repeat re-opens the same region, so last-write-wins is exact.
        self.regions: dict[str, list[str]] = {}
        self.traces: dict[str, dict] = {}

        encoder, reranker, self.device_proof = self._models()
        self.system = MemorySystem(
            encoder=encoder,
            reranker=reranker,
            llm_fn=self._refuse_llm,
            retrieval=RetrievalConfig(**EXPECTED_RETRIEVAL),
            prompts=PromptConfig.default(),
            distiller=None,
        )
        self._install_observers()

    # --- construction -------------------------------------------------------

    @staticmethod
    def _refuse_llm(_prompt: str) -> str:
        raise AssertionError("Gen42 must not call an LLM")

    @classmethod
    def _models(cls):
        if cls._shared:
            return cls._shared["encoder"], cls._shared["reranker"], cls._shared["proof"]

        import sentence_transformers
        from membukkit.models.encoder import Encoder
        from membukkit.models.reranker import UtilityReranker

        proof: list[dict] = []
        orig_st = sentence_transformers.SentenceTransformer.__init__
        orig_ce = sentence_transformers.CrossEncoder.__init__

        def wrap_st(self, model_name_or_path=None, *a, **kw):
            out = orig_st(self, model_name_or_path, *a, **kw)
            proof.append(record_devices("biencoder", str(model_name_or_path), self))
            return out

        def wrap_ce(self, model_name=None, *a, **kw):
            out = orig_ce(self, model_name, *a, **kw)
            proof.append(record_devices("reranker", str(model_name), self))
            return out

        sentence_transformers.SentenceTransformer.__init__ = wrap_st
        sentence_transformers.CrossEncoder.__init__ = wrap_ce
        try:
            paths = {
                role: str(Path(CONFIGURATIONS["intended"][role]["local"]).resolve())
                for role in ("encoder", "reranker")
            }
            encoder = Encoder(paths["encoder"])
            encoder.model  # force construction now so the device is proven up front
            reranker = UtilityReranker.load(paths["reranker"])
        finally:
            sentence_transformers.SentenceTransformer.__init__ = orig_st
            sentence_transformers.CrossEncoder.__init__ = orig_ce

        seen = {p["kind"]: p for p in proof}
        for kind, want in REQUIRED_DEVICES.items():
            got = seen.get(kind)
            if got is None:
                raise DeviceDrift(f"{kind} was never constructed")
            if got["devices"] != want:
                raise DeviceDrift(f"{kind} on {got['devices']}, frozen identity requires {want}")
            if got["target"] != paths["encoder" if kind == "biencoder" else "reranker"]:
                raise DeviceDrift(f"{kind} loaded {got['target']!r}, not the pinned snapshot")

        cls._shared = {"encoder": encoder, "reranker": reranker, "proof": proof}
        return encoder, reranker, proof

    def _install_observers(self) -> None:
        """Observe native relevance order and the opened candidate region.

        Both wrappers forward to the original and record what passed through,
        so retrieval is unchanged.
        """
        system = self.system
        orig_retrieve = system._retrieve
        orig_candidates = system._backend.candidates

        def traced_retrieve(*a, **kw):
            cands, trace = orig_retrieve(*a, **kw)
            self._selected = list(cands)
            self._trace = dict(trace or {})
            return cands, trace

        def traced_candidates(*a, **kw):
            pool = orig_candidates(*a, **kw)
            self._pool = list(pool.candidates)
            return pool

        system._retrieve = traced_retrieve
        system._backend.candidates = traced_candidates

    # --- engine interface ---------------------------------------------------

    def write(self, text: str) -> tuple[str, float, str]:
        from membukkit.storage.base import content_id

        self._ordinal += 1
        payload = ADAPTER.write_payload(text, self._ordinal)
        ADAPTER.assert_write_payload(payload)
        started = time.perf_counter()
        n_new = self.system.ingest_facts([payload], subject=self.persona_id)
        latency = (time.perf_counter() - started) * 1000
        native_id = content_id(payload["fact_id"], self.persona_id)
        return native_id, latency, "created" if n_new == 1 else "deduped"

    def open_read_snapshot(self) -> None:
        """The in-memory backend has no snapshot handle; reads are direct."""

    def close_read_snapshot(self) -> None:
        return None

    def search(self, question_text: str) -> tuple[list[dict], float]:
        self._selected, self._pool, self._trace = [], [], {}
        started = time.perf_counter()
        result = self.system.search(question_text, top_k=NATIVE_TOP_K)
        latency = (time.perf_counter() - started) * 1000

        surfaced = {h.source_id for h in result.hits}
        native = [getattr(c, "id", "") for c in self._selected]
        if surfaced != set(native):
            raise NativeRankMismatch(
                f"public surface returned {sorted(surfaced)}, native order holds {sorted(native)}"
            )
        if self._trace.get("scan_fraction") is not None:
            self.scan_fractions.append(float(self._trace["scan_fraction"]))
        self.regions[question_text] = [getattr(c, "id", "") for c in self._pool]
        self.traces[question_text] = {
            k: self._trace.get(k)
            for k in ("mode", "scan_fraction", "n_scanned", "n_facts", "n_buckets_opened")
            if k in self._trace
        }

        items = [
            {
                "native_id": getattr(cand, "id", ""),
                "rank": index,
                "score": round(float(getattr(cand, "cosine", 0.0)), 8),
            }
            for index, cand in enumerate(self._selected, start=1)
        ]
        return items, latency

    def candidate_region(self) -> list[str]:
        """Native ids the router opened for the query just executed."""
        return [getattr(c, "id", "") for c in self._pool]

    def last_trace(self) -> dict:
        return dict(self._trace)

    # --- state and integrity ------------------------------------------------

    def _state(self) -> dict:
        return self.system._backend.to_state()

    def state_digest(self) -> str:
        state = self._state()
        rows = state.get("facts", [])
        digest = hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode())
        vectors = state.get("vectors")
        if vectors is not None:
            digest.update(getattr(vectors, "tobytes", lambda: b"")())
        return digest.hexdigest()

    def store_digest(self) -> str:
        return self.state_digest()

    def inventory(self) -> dict[str, Any]:
        rows = self._state().get("facts", [])
        return {
            "backend_count": int(self.system._backend.count()),
            "rows": len(rows),
            "distinct_ids": len({r.get("id") for r in rows}),
            "distinct_texts": len({r.get("text") for r in rows}),
            "superseded_rows": sum(1 for r in rows if r.get("superseded_by")),
            "reconciliation": "count == rows == distinct ids when no write collapsed",
        }

    def store_bytes(self) -> int:
        """In-memory store: text bytes plus the embedding matrix."""
        state = self._state()
        rows = state.get("facts", [])
        vectors = state.get("vectors")
        nbytes = int(getattr(vectors, "nbytes", 0) or 0)
        return nbytes + sum(len((r.get("text") or "").encode()) for r in rows)

    def close(self) -> None:
        self.system = None


ENGINES = {"membukkit": MemBukkitEngine}
