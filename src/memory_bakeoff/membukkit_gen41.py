"""Gen41: MemBukkit intended models on the frozen Round1 raw-product ruler.

This is a within-product model-weight ablation, not a new lane. The same frozen
Round1 corpus, scorer, provider and retrieval configuration run twice: once with
the Gen8 documented-fallback model pair as a replication control, and once with
the intended MemseekAI pair pinned in Gen40. Only the model snapshots differ.

Device is the trap this module exists to close. Gen40 measured that the
historical encoder wrapper never passes ``ModelConfig.device`` to
``SentenceTransformer``, so the bi-encoder auto-selects an accelerator while the
reranker honours the request. ``force_cpu`` is a harness-owned constructor
shim, applied identically to both configurations, that supplies a device where
the caller supplied none. It changes no weight, tokenizer, pooling or ranking.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from memory_bakeoff.membukkit_gen40 import (
    MEMBUKKIT_PINNED_COMMIT,
    reconcile_snapshot,
    sha256_file,
    snapshot_identity,
)

__all__ = [
    "CONFIGURATIONS",
    "EXPECTED_RETRIEVAL",
    "GEN8_DIRS",
    "gen8_reference",
    "ROUND1_CONDITIONS",
    "DeviceProof",
    "PinMismatch",
    "contract_sha256",
    "ensure_snapshot",
    "force_cpu",
    "observe_devices",
    "metrics_of",
    "per_query_ids",
    "record_devices",
    "verify_snapshot",
]


class PinMismatch(RuntimeError):
    """A model snapshot did not match the revision it was pinned to."""


# --- what each configuration is allowed to load ------------------------------

INTENDED_ROOT = Path.home() / ".membukkit" / "models"
FALLBACK_ROOT = Path.home() / ".membukkit-gen41" / "fallback"

CONFIGURATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    # The Gen8 documented-fallback pair, at the revisions Gen8 recorded. The
    # reranker repo id in the pinned MemBukkit source now redirects: Hugging
    # Face renamed it to ms-marco-MiniLM-L6-v2. The revision is unchanged.
    "fallback_control": {
        "encoder": {
            "repo": "sentence-transformers/all-mpnet-base-v2",
            "revision": "e8c3b32edf5434bc2275fc9bab85f82640a19130",
            "local": str(FALLBACK_ROOT / "all-mpnet-base-v2"),
        },
        "reranker": {
            "repo": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "resolved_repo": "cross-encoder/ms-marco-MiniLM-L6-v2",
            "revision": "233902d25c440f23af6f7d6e94d2946bac0bee0a",
            "local": str(FALLBACK_ROOT / "ms-marco-MiniLM-L-6-v2"),
        },
    },
    # The intended pair, reproduced and pinned in Gen40.
    "intended": {
        "encoder": {
            "repo": "MemseekAI/membukkit-biencoder-v1",
            "revision": "50ab0a1fefa47c44d6d66f530dea2d3ea426f5b3",
            "local": str(INTENDED_ROOT / "MemseekAI__membukkit-biencoder-v1"),
        },
        "reranker": {
            "repo": "MemseekAI/membukkit-reranker-v2",
            "revision": "0b46ab535caa4044542889dd76a15868799aabbe",
            "local": str(INTENDED_ROOT / "MemseekAI__membukkit-reranker-v2"),
        },
    },
}

# Only what the loaders read. The full revisions also carry ONNX and OpenVINO
# exports and a duplicate .bin checkpoint, none of which this runtime touches;
# reconciliation is therefore scoped to the downloaded manifest and says so.
ALLOW_PATTERNS = ["*.json", "*.txt", "*.safetensors"]

ROUND1_CONDITIONS = {"core": 0, "stress": 450}

# The frozen Round1 raw-product retrieval scope, as committed in
# MemBukkitProvider._retrieval(). Asserted before every scored run.
EXPECTED_RETRIEVAL: Dict[str, Any] = {
    "union": True,
    "union_lanes": ("atomic",),
    "bucket_mode": "topic",
    "scan_budget": 0.3,
    "scan_budget_temporal": None,
    "num_buckets": 24,
    "k_proto": 0,
    "select": "hybrid",
    "rerank_cap": 50,
    "top_k": 10,
    "reasoning_top_k": 30,
    "k_rrf": 60,
    "lexical_lane": False,
}

# The committed Gen8 runs are the replication anchor. They are read from the
# repository rather than restated here, so the anchor cannot drift from what was
# actually published.
GEN8_DIRS = {
    "core": [f"results/membukkit_fallback_gen8_core-r{i}" for i in (1, 2, 3)],
    "stress": [f"results/membukkit_fallback_gen8_stress-r{i}" for i in (1, 2, 3)],
}


def gen8_reference(root: Path, condition: str) -> List[Dict[str, Any]]:
    """Committed Gen8 metrics for one condition, one entry per repetition."""
    return [metrics_of(root / d / "run.json") for d in GEN8_DIRS[condition]]


METRIC_KEYS = (
    "hit@5",
    "mrr",
    "all_relevant@5",
    "prohibited@5",
    "useful_before_harmful",
    "mean_context_chars",
)


# --- model acquisition and pinning -------------------------------------------


def ensure_snapshot(repo: str, revision: str, local: Path) -> Path:
    """Download exactly this revision's loader files, or reuse what is there."""
    from huggingface_hub import snapshot_download

    local.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=repo,
        revision=revision,
        local_dir=str(local),
        allow_patterns=ALLOW_PATTERNS,
    )
    return local


def verify_snapshot(repo: str, revision: str, local: Path) -> Dict[str, Any]:
    """Reconcile every local file against the published revision, or raise."""
    from huggingface_hub import HfApi

    info = HfApi().model_info(repo, revision=revision, files_metadata=True)
    if info.sha != revision:
        raise PinMismatch(f"{repo} resolved to {info.sha}, not {revision}")
    remote = {}
    for s in info.siblings:
        lfs = getattr(s, "lfs", None)
        remote[s.rfilename] = {
            "oid": getattr(s, "blob_id", None),
            "lfs_sha256": (
                lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)
            )
            if lfs
            else None,
        }
    local_files = snapshot_identity(local)
    rec = reconcile_snapshot(local_files, remote)
    if rec["mismatched"] or rec["local_only"]:
        raise PinMismatch(f"{repo}@{revision}: {rec['mismatched'] + rec['local_only']}")
    return {
        "repo": repo,
        "resolved_repo": info.id,
        "revision": info.sha,
        "local": str(local),
        "n_files_local": len(local_files),
        "n_files_in_revision": len(remote),
        "files": local_files,
        "reconciliation": rec,
        "scope": "loader files only; ONNX/OpenVINO/.bin exports in the revision are not downloaded",
    }


# --- device control ----------------------------------------------------------


class DeviceProof(Dict[str, Any]):
    """Per-model record of the device actually in use after construction."""


@contextmanager
def force_cpu(proof: List[Dict[str, Any]]) -> Iterator[None]:
    """Supply ``device="cpu"`` where the caller supplied none, and prove it.

    Applied identically to both configurations. It touches only the device
    argument of the model constructors; weights, tokenizer, pooling, precision
    and every retrieval parameter are untouched.
    """
    import sentence_transformers

    orig_st = sentence_transformers.SentenceTransformer.__init__
    orig_ce = sentence_transformers.CrossEncoder.__init__

    def wrap_st(self, model_name_or_path=None, *a, **kw):
        kw.setdefault("device", "cpu")
        out = orig_st(self, model_name_or_path, *a, **kw)
        proof.append(record_devices("biencoder", str(model_name_or_path), self))
        return out

    def wrap_ce(self, model_name=None, *a, **kw):
        kw.setdefault("device", "cpu")
        out = orig_ce(self, model_name, *a, **kw)
        proof.append(record_devices("reranker", str(model_name), self))
        return out

    sentence_transformers.SentenceTransformer.__init__ = wrap_st
    sentence_transformers.CrossEncoder.__init__ = wrap_ce
    try:
        yield
    finally:
        sentence_transformers.SentenceTransformer.__init__ = orig_st
        sentence_transformers.CrossEncoder.__init__ = orig_ce


@contextmanager
def observe_devices(proof: List[Dict[str, Any]]) -> Iterator[None]:
    """Record the device each model chooses, changing nothing.

    The diagnostic counterpart to ``force_cpu``: same observation, no injected
    device argument, so the product's own selection is what gets measured.
    """
    import sentence_transformers

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
        yield
    finally:
        sentence_transformers.SentenceTransformer.__init__ = orig_st
        sentence_transformers.CrossEncoder.__init__ = orig_ce


def record_devices(kind: str, target: str, obj: Any) -> Dict[str, Any]:
    """Read the device off the constructed model itself, not off the request."""
    devices = []
    for attr in ("device", "_target_device"):
        v = getattr(obj, attr, None)
        if v is not None:
            devices.append(str(v))
    inner = getattr(obj, "model", None)
    if inner is not None:
        v = getattr(inner, "device", None)
        if v is not None:
            devices.append(str(v))
        try:
            devices.extend(str(p.device) for p in list(inner.parameters())[:1])
        except (AttributeError, TypeError):
            pass
    return {
        "kind": kind,
        "target": target,
        "devices": sorted(set(devices)),
        "all_cpu": bool(devices) and all(d.startswith("cpu") for d in devices),
    }


# --- reading Round1 leaves ---------------------------------------------------


def metrics_of(run_json: Path) -> Dict[str, Any]:
    payload = json.loads(run_json.read_text())
    row = payload[0]
    s = row["summary"]
    return {
        "provider": row["provider"],
        "experiment_class": row["experiment_class"],
        "distractors": row["distractors"],
        "status": row["status"],
        "publishable": row["publishability"]["publishable"],
        "provenance_status": row["provenance"]["status"],
        "provenance_methods": row["provenance"]["methods"],
        "n_cases": s["n_cases"],
        **{k: s[k] for k in METRIC_KEYS if k in s},
        "mean_latency_ms": s.get("mean_latency_ms"),
    }


def per_query_ids(run_json: Path) -> Dict[str, List[str]]:
    payload = json.loads(run_json.read_text())
    return {d["query_id"]: list(d["retrieved_ids"]) for d in payload[0]["details"]}


def contract_sha256() -> str:
    return sha256_file(Path(__file__))


def membukkit_pin() -> str:
    return MEMBUKKIT_PINNED_COMMIT
