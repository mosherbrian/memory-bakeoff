"""Gen40 focused tests: identity, fallback rejection, provenance, determinism.

These tests never touch a benchmark corpus and never assert an accuracy number.
Artifact-backed tests skip when the run has not been executed in this checkout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import (  # noqa: E402
    FALLBACK_ENCODER,
    FALLBACK_IDS,
    FALLBACK_RERANKER,
    INTENDED_ENCODER_REPO,
    INTENDED_RERANKER_REPO,
    MEMBUKKIT_PINNED_COMMIT,
    SYNTHETIC_FACTS,
    SYNTHETIC_QUERIES,
    FallbackDetected,
    LoadTrace,
    git_blob_sha1,
    leaf_digest,
    load_json,
    reconcile_snapshot,
)

RESULTS = ROOT / "results" / "membukkit_gen40_intended_model"
ALLOWED = ["/home/x/.membukkit/models"]


def _leaf(name: str) -> dict:
    path = RESULTS / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


# --- pins --------------------------------------------------------------------


def test_pinned_upstream_commit_is_the_gen7_one():
    assert MEMBUKKIT_PINNED_COMMIT == "f28a2e58cdc0e77758c0f6d9a1e050f80dcad807"


def test_intended_and_fallback_repos_are_distinct_and_named():
    assert INTENDED_ENCODER_REPO == "MemseekAI/membukkit-biencoder-v1"
    assert INTENDED_RERANKER_REPO == "MemseekAI/membukkit-reranker-v2"
    assert FALLBACK_IDS == {FALLBACK_ENCODER, FALLBACK_RERANKER}
    assert not FALLBACK_IDS & {INTENDED_ENCODER_REPO, INTENDED_RERANKER_REPO}


# --- fallback rejection ------------------------------------------------------


def test_resolver_returning_a_fallback_is_a_failure():
    trace = LoadTrace(
        resolver_calls=[{"role": "encoder", "intended_repo": INTENDED_ENCODER_REPO,
                         "returned": FALLBACK_ENCODER}],
        downloads=[], loads=[],
    )
    assert trace.fallback_events()
    with pytest.raises(FallbackDetected):
        trace.assert_intended_only(ALLOWED)


def test_loading_a_fallback_model_is_a_failure():
    trace = LoadTrace(
        resolver_calls=[], downloads=[],
        loads=[{"kind": "reranker", "target": FALLBACK_RERANKER}],
    )
    with pytest.raises(FallbackDetected):
        trace.assert_intended_only(ALLOWED)


def test_loading_from_outside_the_pinned_snapshot_is_a_failure():
    trace = LoadTrace(
        resolver_calls=[], downloads=[],
        loads=[{"kind": "biencoder", "target": "/somewhere/else/model"}],
    )
    with pytest.raises(FallbackDetected):
        trace.assert_intended_only(ALLOWED)


def test_intended_snapshot_load_passes():
    trace = LoadTrace(
        resolver_calls=[{"role": "encoder", "intended_repo": INTENDED_ENCODER_REPO,
                         "returned": ALLOWED[0] + "/MemseekAI__membukkit-biencoder-v1"}],
        downloads=[INTENDED_ENCODER_REPO],
        loads=[{"kind": "biencoder", "target": ALLOWED[0] + "/MemseekAI__membukkit-biencoder-v1"}],
    )
    trace.assert_intended_only(ALLOWED)


# --- content identity --------------------------------------------------------


def test_git_blob_sha1_matches_git(tmp_path):
    p = tmp_path / "empty"
    p.write_bytes(b"")
    assert git_blob_sha1(p) == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_reconcile_reports_every_kind_of_disagreement():
    local = {
        "a.bin": {"sha256": "aa", "git_oid": "1"},
        "b.txt": {"sha256": "bb", "git_oid": "2"},
        "extra": {"sha256": "cc", "git_oid": "3"},
    }
    remote = {
        "a.bin": {"lfs_sha256": "aa", "oid": None},
        "b.txt": {"lfs_sha256": None, "oid": "9"},
        "missing": {"lfs_sha256": None, "oid": "4"},
    }
    out = reconcile_snapshot(local, remote)
    assert out["matched"] == ["a.bin"]
    assert out["mismatched"] == ["b.txt"]
    assert out["local_only"] == ["extra"]
    assert out["remote_only"] == ["missing"]
    assert out["all_match"] is False


def test_load_json_raises_rather_than_defaulting(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_json(tmp_path / "nope.json")


# --- fixture hygiene ---------------------------------------------------------


def test_fixture_is_synthetic_and_self_contained():
    assert len(SYNTHETIC_FACTS) >= 50
    assert all(f["fact_id"].startswith("SYN-") for f in SYNTHETIC_FACTS)
    assert len({f["fact_id"] for f in SYNTHETIC_FACTS}) == len(SYNTHETIC_FACTS)
    assert any(q["kind"] == "unrelated" for q in SYNTHETIC_QUERIES)


def test_contract_module_names_no_corpus_and_imports_no_lane():
    """The fixture is literal: the module locates no data and imports no lane."""
    src = (ROOT / "src" / "memory_bakeoff" / "membukkit_gen40.py").read_text()
    for forbidden in ("Data/Step4_4", "external/", "results/round1", "longitudinal-v1"):
        assert forbidden not in src
    assert "from memory_bakeoff" not in src
    assert "import memory_bakeoff" not in src


# --- digest ------------------------------------------------------------------


def test_digest_ignores_wall_clock():
    a = {"x": 1, "wall_clock_seconds": 1.0, "started_at": "t"}
    b = {"x": 1, "wall_clock_seconds": 99.0, "started_at": "u"}
    assert leaf_digest(a) == leaf_digest(b)


def test_digest_tracks_content():
    assert leaf_digest({"x": 1}) != leaf_digest({"x": 2})


# --- artifact-backed ---------------------------------------------------------


def test_online_leaf_used_only_intended_models():
    leaf = _leaf("online.json")
    assert leaf["evidence_class"] == "product_identity_reproduction_no_score"
    assert leaf["load_trace"]["fallback_events"] == []
    assert leaf["membukkit_source"]["matches_gen7_pin"] is True
    assert leaf["llm_invocations"] == 0


def test_online_leaf_provenance_maps_exactly():
    leaf = _leaf("online.json")
    assert leaf["provenance"]["all_returns_mapped"] is True
    assert leaf["provenance"]["unmapped_returned_ids"] == []


def test_online_snapshots_reconcile_to_pinned_revisions():
    leaf = _leaf("online.json")
    for role in ("encoder", "reranker"):
        snap = leaf["snapshots"][role]
        assert snap["revision"]
        assert snap["reconciliation"]["all_match"] is True


def test_leaf_digests_rebuild_deterministically():
    for name in ("online.json", "offline.json"):
        leaf = _leaf(name)
        recorded = leaf.pop("digest")
        assert leaf_digest(leaf) == recorded


def test_offline_phase_downloaded_nothing_and_kept_identity():
    online, offline = _leaf("online.json"), _leaf("offline.json")
    assert offline["load_trace"]["downloads"] == []
    assert offline["load_trace"]["fallback_events"] == []
    for role in ("encoder", "reranker"):
        assert offline["snapshots"][role]["revision"] == online["snapshots"][role]["revision"]
