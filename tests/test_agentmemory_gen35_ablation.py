"""Gen35: the ablation is only a causal claim if the patch, the build and the
reporting all hold everything except the retirement flag constant."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from memory_bakeoff import round2_reporting as R
from memory_bakeoff.longitudinal import canonical_json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/agentmemory_gen35_retirement_ablation"
PATCH = ROOT / "research/patches/agentmemory-gen35-retirement-flag.patch"
PREFLIGHT = ROOT / "results/agentmemory_gen35_preflight.json"
FLAG = "AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION"

pytestmark = pytest.mark.skipif(not RESULTS.is_dir(), reason="Gen35 evidence not present")


@pytest.fixture(scope="module")
def report() -> dict:
    return json.loads((RESULTS / "paired-derived.json").read_text())


@pytest.fixture(scope="module")
def leaves() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(RESULTS.glob("repetition-*.json"))]


def test_pinned_product_identity(report):
    identity = report["product_identity"]
    assert identity["upstream_commit"] == "e04ba88819c365c9acf9d6661ea802143e728bd6"
    assert identity["package_version"] == "0.9.29"
    assert identity["fixture_sha256"] == "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
    assert identity["scorer_contract_sha256"] == "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"


def test_patch_touches_only_the_retirement_seam():
    diff = PATCH.read_text()
    files = [line.split(" b/")[-1].strip() for line in diff.splitlines() if line.startswith("diff --git")]
    assert files == ["src/functions/remember.ts"]
    added = [l[1:].strip() for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:].strip() for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    # the only removed lines are the three supersession-state assignments
    assert removed == ["supersededId = existing.id;",
                       "supersededVersion = existing.version ?? 1;",
                       "supersededMemory = existing;"]
    assert any(FLAG in line for line in added)
    # the threshold, the tokenizer and the loop break are untouched in code
    code = [l for l in added + removed if not l.startswith("//")]
    assert not any("0.7" in line or "jaccard" in line.lower() or "break" in line for line in code)


def test_patch_hash_is_frozen_in_provenance(report):
    recorded = report["product_identity"]["patch_sha256"]
    assert recorded == hashlib.sha256(PATCH.read_bytes()).hexdigest()


def test_both_arms_ran_the_same_patched_build(leaves):
    trees = {leaf["build_tree"] for leaf in leaves}
    assert len(trees) == 1
    assert trees.pop().endswith("external/agentmemory-gen35")


def test_environment_differs_only_by_flag_and_run_identity(report, leaves):
    parity = report["product_identity"]["environment_parity"]
    assert parity["illegal_differences"] == []
    assert parity["flag_varied"] is True
    assert set(parity["allowed_differences"]) <= {"AGENT_ID", FLAG}
    for leaf in leaves:
        assert (leaf["captured_env"].get(FLAG) == "1") == (leaf["arm"] == "off")


def test_adapter_and_ruler_unchanged(report):
    from memory_bakeoff.providers import agentmemory_longitudinal as A

    assert report["product_identity"]["adapter_contract_sha256"] == A.adapter_contract_sha256()
    # the frozen Gen33 adapter contract; a change here breaks the causal contrast
    assert A.adapter_contract_sha256() == "a06482525d718dd1540c9491c80efe468c5414dcaf0ab6393781ac5254ff9b26"


def test_preflight_on_retires_and_off_does_not():
    preflight = json.loads(PREFLIGHT.read_text())
    assert preflight["passed"] is True
    assert preflight["checks"]["above_on_retires_exactly_one"] is True
    assert preflight["checks"]["above_off_retires_nothing"] is True
    assert preflight["checks"]["above_on_matches_unpatched_upstream"] is True
    assert preflight["checks"]["below_arms_identical_ranking"] is True


def test_control_arm_replicates_gen33(report):
    gate = report["control_replication_gate"]
    assert gate["mismatches"] == []
    assert gate["passed"] is True
    assert gate["gen33_repetitions"] == 3


def test_manipulation_activated_in_on_and_absent_in_off(report, leaves):
    assert report["manipulation_passed"] is True
    for leaf in leaves:
        events = leaf["supersession_events"]
        if leaf["arm"] == "on":
            assert len(events) == 2
            assert leaf["checkpoint_state"]["CP16"]["rows_retired"] == 2
        else:
            assert events == []
            assert leaf["checkpoint_state"]["CP16"]["rows_retired"] == 0
            assert leaf["checkpoint_state"]["CP16"]["rows_live"] == 16


def test_false_supersession_never_comes_from_the_case_stream(report):
    assert "false_supersession" not in report["case_stream"]
    assert "false_supersession" in report["lifecycle_stream"]
    with pytest.raises(R.ReportingError):
        R.legal_stream("false_supersession", R.Stream.CASE)


def test_six_repetitions_with_counterbalanced_pairs(report, leaves):
    assert len(leaves) == 6
    assert sorted(leaf["arm"] for leaf in leaves) == ["off"] * 3 + ["on"] * 3
    order = {(leaf["repetition"], leaf["position_in_pair"]): leaf["arm"] for leaf in leaves}
    assert order[(1, 1)] == "on" and order[(2, 1)] == "off" and order[(3, 1)] == "on"


def test_totals_are_leaf_derived_and_reconcile(leaves):
    for leaf in leaves:
        rebuilt = {k: v.value_or_raise() for k, v in R.rebuild_case_totals(leaf).items()}
        stored = leaf["failure_totals"]
        assert R.reconcile(stored, R.rebuild_case_totals(leaf), leaf["arm"], R.Stream.CASE) == []
        assert rebuilt[list(rebuilt)[0]] is not None
        assert all(stored.get(k, 0) == v for k, v in rebuilt.items() if v)


def test_missing_evidence_raises_rather_than_counting_zero(tmp_path):
    with pytest.raises(R.ReportingError):
        R.load_json(tmp_path / "absent.json")
    broken = {"cases": [], "lifecycle": {}}
    with pytest.raises(R.ReportingError):
        R.validate_repetition(broken, "synthetic")


def test_report_digest_is_deterministic(report):
    content = {k: v for k, v in report.items() if k not in ("product_identity", "content_digest")}
    assert hashlib.sha256(canonical_json(content).encode()).hexdigest() == report["content_digest"]
    assert (RESULTS / "content-digest.txt").read_text().strip() == report["content_digest"]


def test_no_llm_or_gpu_path(leaves):
    for leaf in leaves:
        env = leaf["captured_env"]
        assert env["EMBEDDING_PROVIDER"] == "local"
        assert env["CONSOLIDATION_ENABLED"] == "false"
        assert env["GRAPH_EXTRACTION_ENABLED"] == "false"
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
                    "GOOGLE_API_KEY", "OPENROUTER_API_KEY"):
            assert env[key] == ""


def test_every_arm_difference_traces_to_retirement(report):
    trace = report["case_difference_trace"]
    assert trace, "the arms must differ somewhere or the treatment did nothing"
    assert [t["case_id"] for t in trace if t["possible_confound"]] == []
