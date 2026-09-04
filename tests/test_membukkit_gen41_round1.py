"""Gen41 focused tests: frozen ruler, pins, CPU proof, provenance, gate logic.

Artifact-backed tests skip when the Gen41 runs are absent from this checkout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen41 import (  # noqa: E402
    CONFIGURATIONS,
    EXPECTED_RETRIEVAL,
    ROUND1_CONDITIONS,
    gen8_reference,
    membukkit_pin,
    metrics_of,
    per_query_ids,
    record_devices,
)

MANIFEST = ROOT / "results" / "membukkit_gen41_manifest"


POLICIES = ("product_default", "cpu")


def _dir(config: str, condition: str, rep: int, policy: str) -> Path:
    stem = (
        f"membukkit_intended_gen41_{policy}_{condition}-r{rep}"
        if config == "intended"
        else f"membukkit_gen41_replication_control_{policy}_{condition}-r{rep}"
    )
    p = ROOT / "results" / stem
    if not (p / "run.json").exists():
        pytest.skip(f"{stem} not present in this checkout")
    return p


def _json(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"{path.name} not present in this checkout")
    return json.loads(path.read_text())


# --- contract ----------------------------------------------------------------


@pytest.fixture
def unimport_membukkit():
    """Importing the product here would make a later fails-closed test see it.

    The provider probe consults ``sys.modules`` before ``find_spec``, so leaving
    ``membukkit`` loaded turns another test's "package is absent" case into a
    false pass.
    """
    before = {k for k in sys.modules if k == "membukkit" or k.startswith("membukkit.")}
    yield
    for name in [k for k in sys.modules if k == "membukkit" or k.startswith("membukkit.")]:
        if name not in before:
            del sys.modules[name]


def test_frozen_round1_config_matches_the_committed_provider(unimport_membukkit):
    from memory_bakeoff.providers.external import MemBukkitProvider

    got = vars(MemBukkitProvider._retrieval())
    for key, want in EXPECTED_RETRIEVAL.items():
        assert got[key] == want, key
    assert got["union_lanes"] == ("atomic",)


def test_the_two_configurations_share_nothing_but_the_ruler():
    intended = CONFIGURATIONS["intended"]
    fallback = CONFIGURATIONS["fallback_control"]
    paths = {r["local"] for r in intended.values()} | {r["local"] for r in fallback.values()}
    assert len(paths) == 4
    assert {r["revision"] for r in intended.values()} & {
        r["revision"] for r in fallback.values()
    } == set()


def test_membukkit_source_pin_is_the_historical_one():
    assert membukkit_pin() == "f28a2e58cdc0e77758c0f6d9a1e050f80dcad807"


def _stable(metrics: dict) -> dict:
    return {k: v for k, v in metrics.items() if k != "mean_latency_ms"}


def test_gen8_anchor_is_read_from_the_repository():
    for condition in ROUND1_CONDITIONS:
        reps = gen8_reference(ROOT, condition)
        assert len(reps) == 3
        assert all(_stable(r) == _stable(reps[0]) for r in reps)
        assert reps[0]["experiment_class"] == "raw_product"


# --- device proof ------------------------------------------------------------


class _FakeInner:
    device = "cpu"

    def parameters(self):
        return iter(())


class _FakeModel:
    def __init__(self, dev):
        self.device = dev
        self.model = _FakeInner()


def test_device_proof_accepts_cpu_and_rejects_an_accelerator():
    assert record_devices("biencoder", "x", _FakeModel("cpu"))["all_cpu"] is True
    assert record_devices("biencoder", "x", _FakeModel("mps:0"))["all_cpu"] is False


def test_device_proof_is_false_when_nothing_could_be_read():
    class Bare:
        pass

    assert record_devices("reranker", "x", Bare())["all_cpu"] is False


# --- artifact-backed ---------------------------------------------------------


@pytest.mark.parametrize("policy", POLICIES)
@pytest.mark.parametrize("config", ["fallback_control", "intended"])
@pytest.mark.parametrize("condition", ["core", "stress"])
def test_every_scored_run_proves_device_pins_and_provenance(config, condition, policy):
    for rep in (1, 2, 3):
        d = _dir(config, condition, rep, policy)
        control = json.loads((d / "gen41_control.json").read_text())
        assert control["configuration"] == config
        assert control["cpu_shim"] is (policy == "cpu")
        assert control["device_proof"], "no device was proven"
        if policy == "cpu":
            assert all(p["all_cpu"] for p in control["device_proof"])
        assert control["load_trace"]["downloads"] == []
        assert control["load_trace"]["fallback_events"] == []
        assert control["retrieval_config"]["union_lanes"] == ["atomic"]
        for role in ("encoder", "reranker"):
            assert control["model_paths"][role] == str(
                Path(CONFIGURATIONS[config][role]["local"]).resolve()
            )
        m = metrics_of(d / "run.json")
        assert m["experiment_class"] == "raw_product"
        assert m["provenance_status"] == "verified"
        assert m["publishable"] is True
        assert set(m["provenance_methods"]) == {"native"}


def test_replication_gate_passed_before_intended_exposure():
    gate = _json(MANIFEST / "replication_gate.json")
    assert gate["passed"] is True
    assert gate["tolerance"]["product_default_must_match_gen8_exactly"] is True
    for condition in ROUND1_CONDITIONS:
        block = gate["conditions"][condition]
        # The gate requires metric equality with Gen8, not byte-equal ordering:
        # two stress queries return the same items in a different tail order and
        # move no metric. That is recorded, not gated away.
        assert block["product_default"]["metric_differences_vs_gen8"] == {}
        for policy in POLICIES:
            assert block[policy]["provenance_clean"] is True
            assert block[policy]["repeats_retrieved_ids_identical"] is True


def test_the_cpu_deviation_from_gen8_is_published_not_absorbed():
    """A gate that hid the CPU drift would be worse than one that failed."""
    gate = _json(MANIFEST / "replication_gate.json")
    stress = gate["conditions"]["stress"]["cpu"]
    assert "metric_differences_vs_gen8" in stress
    assert stress["deviation_explained_by_device"] is True


@pytest.mark.parametrize("policy", POLICIES)
def test_only_the_model_snapshots_differ_within_a_policy(policy):
    for condition in ROUND1_CONDITIONS:
        a = json.loads(
            (_dir("fallback_control", condition, 1, policy) / "gen41_control.json").read_text()
        )
        b = json.loads((_dir("intended", condition, 1, policy) / "gen41_control.json").read_text())
        assert a["retrieval_config"] == b["retrieval_config"]
        assert a["cpu_shim"] == b["cpu_shim"]
        assert [p["devices"] for p in a["device_proof"]] == [
            p["devices"] for p in b["device_proof"]
        ]
        assert a["model_paths"] != b["model_paths"]


def test_historical_gen8_results_are_untouched():
    for condition in ROUND1_CONDITIONS:
        reps = gen8_reference(ROOT, condition)
        assert reps[0]["provider"] == "membukkit"
        assert reps[0]["distractors"] == ROUND1_CONDITIONS[condition]


@pytest.mark.parametrize("policy", POLICIES)
def test_comparison_reports_deltas_for_every_round1_metric(policy):
    cmp_ = _json(MANIFEST / "comparison.json")
    for condition in ROUND1_CONDITIONS:
        block = cmp_["conditions"][policy][condition]
        for key in ("hit@5", "mrr", "all_relevant@5", "prohibited@5", "useful_before_harmful"):
            assert key in block["delta_intended_minus_fallback"]
        assert isinstance(block["queries_with_different_retrieved_ids"], list)


def test_pins_reconcile_for_all_four_snapshots():
    pins = _json(MANIFEST / "pins.json")
    for config, roles in CONFIGURATIONS.items():
        for role, spec in roles.items():
            got = pins[config][role]
            assert got["revision"] == spec["revision"]
            assert got["reconciliation"]["mismatched"] == []
            assert got["reconciliation"]["local_only"] == []
