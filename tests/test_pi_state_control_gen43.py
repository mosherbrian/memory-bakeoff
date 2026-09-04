"""Gen43 focused tests: control, state patches, artifacts, history, composer, restart."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import contract as C  # noqa: E402
from memory_bakeoff.pi_state_control import runtime as R  # noqa: E402

BASE = ROOT / "results" / "pi_state_control_gen43"


@pytest.fixture
def proto(tmp_path):
    return R.Prototype(root=tmp_path, goal="a synthetic goal")


def _receipt(proto, passed=True, content='{"passed": true}'):
    (proto.root / "check.json").write_text(content)
    ref = proto.record_receipt("check.json", "validation_receipt", passed)
    proto.apply_patch({"base_revision": proto.revision,
                       "ops": [{"op": "set", "field": "validated_artifact_refs",
                                "value": [ref.to_dict()]}]})
    return ref


# --- control -----------------------------------------------------------------


def test_transition_table_is_executable_not_prose():
    assert C.legal_transition("inspect", "plan")
    assert not C.legal_transition("inspect", "done")
    assert C.TRANSITIONS["done"] == ()
    assert C.GATED_PHASES["done"] == "validation_receipt"


def test_illegal_transition_fails_closed_and_is_recorded(proto):
    event = proto.transition("done")
    assert event["type"] == "transition_rejected"
    assert proto.state["phase"] == "inspect"
    assert proto.history.events[-1]["type"] == "transition_rejected"


def test_done_cannot_be_claimed_without_a_receipt(proto):
    for phase in ("plan", "implement", "validate"):
        assert proto.transition(phase)["type"] == "transition_accepted"
    event = proto.transition("done")
    assert event["type"] == "transition_rejected"
    assert "completion cannot be asserted" in event["payload"]["reason"]


def test_done_is_earned_from_a_validated_artifact(proto):
    for phase in ("plan", "implement", "validate"):
        proto.transition(phase)
    _receipt(proto, passed=True)
    assert proto.transition("done")["type"] == "transition_accepted"
    assert proto.state["phase"] == "done"


def test_a_failing_receipt_does_not_open_the_gate(proto):
    for phase in ("plan", "implement", "validate"):
        proto.transition(phase)
    _receipt(proto, passed=False, content='{"passed": false}')
    assert proto.transition("done")["type"] == "transition_rejected"


# --- artifacts outrank state -------------------------------------------------


def test_mutating_the_artifact_invalidates_the_completion_claim(proto):
    for phase in ("plan", "implement", "validate"):
        proto.transition(phase)
    _receipt(proto, passed=True)
    proto.transition("done")
    assert all(s["valid"] for s in proto.artifact_status())

    (proto.root / "check.json").write_text('{"passed": true, "but": "different bytes"}')
    status = proto.artifact_status()
    assert all(not s["valid"] for s in status)
    assert "digest changed" in status[0]["reason"]
    ok, why = proto._gate_satisfied("validation_receipt", None)
    assert not ok and "digest changed" in why


def test_a_receipt_cannot_be_written_for_a_missing_artifact(proto):
    with pytest.raises(R.ArtifactError):
        proto.record_receipt("nothing-here.json", "validation_receipt", True)


# --- state patches -----------------------------------------------------------


def test_a_stale_patch_is_rejected(proto):
    proto.apply_patch({"base_revision": 0, "ops": [{"op": "append", "field": "next_actions", "value": "a"}]})
    event = proto.apply_patch({"base_revision": 0, "ops": [{"op": "append", "field": "next_actions", "value": "b"}]})
    assert event["type"] == "state_patch_rejected"
    assert "stale patch" in event["payload"]["reason"]


@pytest.mark.parametrize("ops,fragment", [
    ([{"op": "set", "field": "goal", "value": 7}], "takes str"),
    ([{"op": "set", "field": "nope", "value": 1}], "unknown field"),
    ([{"op": "explode", "field": "goal", "value": "x"}], "unknown op"),
    ([{"op": "set", "field": "phase", "value": "done"}], "control layer"),
])
def test_malformed_patches_fail_closed(proto, ops, fragment):
    event = proto.apply_patch({"base_revision": proto.revision, "ops": ops})
    assert event["type"] == "state_patch_rejected"
    assert fragment in event["payload"]["reason"]


def test_state_cannot_become_the_transcript(proto):
    huge = "x" * (C.MAX_STATE_BYTES + 1)
    event = proto.apply_patch({"base_revision": proto.revision,
                               "ops": [{"op": "set", "field": "goal", "value": huge}]})
    assert event["type"] == "state_patch_rejected"
    assert "over the" in event["payload"]["reason"]


def test_bounded_lists_archive_to_history_instead_of_dropping(proto):
    bound = C.BOUNDED_FIELDS["important_findings"]
    for index in range(bound + 3):
        proto.apply_patch({"base_revision": proto.revision,
                           "ops": [{"op": "append", "field": "important_findings",
                                    "value": f"finding {index}"}]})
    assert len(proto.state["important_findings"]) == bound
    assert "finding 0" not in proto.state["important_findings"]
    assert proto.history.search("finding 0"), "the archived entry left no trace in history"


# --- history -----------------------------------------------------------------


def test_history_is_addressable_and_chain_verified(proto):
    first = proto.observe("read", "the first observation")
    proto.observe("read", "the second observation")
    assert proto.history.get(first["id"])["payload"]["output"] == "the first observation"
    proto.history.verify_chain()
    with pytest.raises(R.HistoryError):
        proto.history.get("e999999")


def test_a_tampered_event_breaks_the_chain(proto):
    proto.observe("read", "original")
    proto.observe("read", "second")
    lines = (proto.root / "history.ndjson").read_text().splitlines()
    victim = json.loads(lines[1])
    victim["payload"]["output"] = "quietly rewritten"
    lines[1] = C.canonical(victim)
    (proto.root / "history.ndjson").write_text("\n".join(lines) + "\n")
    with pytest.raises(R.HistoryError):
        R.Prototype.restore(proto.root)


def test_history_only_output_stays_out_of_the_live_context(proto):
    big = "y" * 5000
    proto.observe("bash", big, keep_in_context=False)
    context = C.canonical(proto.compose())
    assert big not in context
    assert proto.history.search(big[:50]), "the output must still be in history"


# --- composer ----------------------------------------------------------------


def test_the_composer_never_replays_the_transcript(proto):
    for index in range(40):
        proto.observe("bash", f"turn {index} " + "z" * 400, keep_in_context=False)
    context_bytes = len(C.canonical(proto.compose()).encode())
    assert context_bytes < proto.history.bytes_total() / 5


def test_recall_is_on_demand_and_not_sticky(proto):
    event = proto.observe("read", "an old decision worth recalling")
    later = proto.compose(requested=[event["id"]])
    assert later["recalled"][0]["id"] == event["id"]
    assert proto.compose()["recalled"] == []


# --- restart -----------------------------------------------------------------


def test_restart_restores_from_persisted_evidence_only(proto):
    proto.transition("plan")
    proto.apply_patch({"base_revision": proto.revision,
                       "ops": [{"op": "set", "field": "next_actions", "value": ["carry on"]}]})
    before = (proto.state_digest(), proto.history.head_digest(), len(proto.history.events))
    restored = R.Prototype.restore(proto.root)
    assert (restored.state_digest(), restored.history.head_digest(), len(restored.history.events)) == before
    assert restored.state["next_actions"] == ["carry on"]


def test_restart_without_persisted_state_is_refused(tmp_path):
    with pytest.raises(R.StateError):
        R.Prototype.restore(tmp_path / "nothing")


# --- artifact-backed ---------------------------------------------------------


def _json(name: str) -> dict:
    path = BASE / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def test_committed_run_ends_done_with_every_corruption_case_closed():
    metrics, corruption = _json("trace_metrics.json"), _json("corruption_tests.json")
    assert metrics["final_phase"] == "done"
    assert corruption["all_failed_closed"] is True


def test_committed_run_kept_context_bounded_while_history_grew():
    series = _json("trace_metrics.json")["metrics"]
    first, last = series[0], series[-1]
    assert last["history_bytes"] > 20 * first["history_bytes"]
    assert last["composed_context_bytes"] < 4 * first["composed_context_bytes"]
    assert max(m["state_bytes"] for m in series) <= C.MAX_STATE_BYTES


def test_committed_restart_recovered_identically():
    recovery = _json("restart_recovery.json")
    assert recovery["restarts"], "no restart boundary was exercised"
    assert all(r["identical"] for r in recovery["restarts"])
    assert recovery["archived_decision_recoverable"] is True
    assert recovery["archived_decision_still_in_active_state"] is False


def test_pi_extension_loaded_and_replaced_the_context():
    identity = _json("identity.json")
    test = identity["extension_load_test"]
    assert test["extension_loaded"] is True
    assert test["load_errors"] == []
    assert test["core_patched"] is False
    assert "context" in test["registered_handlers"]
    hook = test["context_hook"]
    assert hook["transcript_replayed"] is False
    assert hook["replacement_bytes"] < hook["incoming_bytes"] / 10


def test_frozen_contract_matches_the_committed_identity():
    committed = _json("contract.json")
    assert committed["contract_sha256"] == C.contract_sha256()
    assert committed["transitions"] == {k: list(v) for k, v in C.TRANSITIONS.items()}


def test_synthetic_fixture_is_digested_and_unrelated_to_any_corpus():
    fixture = _json("synthetic_trace.json")
    assert fixture["fixture_digest"] == C.digest(fixture["steps"])
    assert fixture["step_count"] >= 55
    blob = C.canonical(fixture)
    for forbidden in ("MemConflict", "Step4_4", "membukkit", "persona"):
        assert forbidden not in blob
