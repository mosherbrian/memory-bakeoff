"""Adversarial tests for the Gen34 reporting layer.

Each test names a way the Round-2 reporting layer failed on 2026-09-03. The
reporter must RAISE rather than produce a plausible zero.
"""
import copy
import json
from pathlib import Path

import pytest

from memory_bakeoff import round2_reporting as R
from memory_bakeoff.longitudinal import fixture_sha256, scorer_contract_sha256

LEDGER = Path("results/round2_gen34_integrity/evidence-ledger.json")
DERIVED = Path("results/round2_gen34_integrity/four-engine-derived.json")
SOURCE = Path("results/hindsight_gen31_longitudinal/repetition-1.json")
CONTRACT_SHA = "9673f1d98091e89fec9758425fc640f7fe8addc84e885ad64edc1cab3b82b149"


def evidence():
    return json.loads(SOURCE.read_text())


def test_contract_is_frozen_and_registry_is_closed():
    assert R.contract_sha256() == CONTRACT_SHA
    assert R.contract_payload()["fixture_sha256"] == fixture_sha256()
    assert R.contract_payload()["scorer_contract_sha256"] == scorer_contract_sha256()
    with pytest.raises(R.ReportingError, match="unknown failure class"):
        R.legal_stream("invented_class", R.Stream.CASE)


def test_lifecycle_only_class_cannot_be_read_from_case_stream():
    """The Gen31 defect: false_supersession read from case totals yielded a fake zero."""
    with pytest.raises(R.ReportingError, match="may not be sourced from case_scorer"):
        R.legal_stream("false_supersession", R.Stream.CASE)
    R.legal_stream("false_supersession", R.Stream.LIFECYCLE)


def test_unmeasured_never_becomes_zero():
    unmeasured = R.Measurement.unmeasured("lifecycle stream absent")
    assert unmeasured.count is None
    assert unmeasured.payload()["status"] == "unmeasured"
    with pytest.raises(R.ReportingError):
        unmeasured.value_or_raise()
    assert R.Measurement.measured(0).payload()["status"] == "measured_zero"
    assert R.Measurement.measured(0).value_or_raise() == 0


def test_missing_file_raises_rather_than_returning_empty():
    with pytest.raises(R.ReportingError, match="missing"):
        R.load_json(Path("results/does-not-exist/repetition-1.json"))


def test_missing_required_key_raises():
    broken = evidence()
    del broken["lifecycle"]
    with pytest.raises(R.ReportingError, match="lifecycle"):
        R.validate_repetition(broken, "test")


def test_empty_lifecycle_checkpoint_is_fatal():
    """A collector returning nothing must never read as 'no records retired'."""
    broken = evidence()
    first = sorted(broken["lifecycle"])[0]
    broken["lifecycle"][first] = []
    with pytest.raises(R.ReportingError, match="empty lifecycle evidence"):
        R.validate_repetition(broken, "test")


def test_missing_canonical_id_field_is_fatal():
    broken = evidence()
    first = sorted(broken["lifecycle"])[0]
    entry = copy.deepcopy(broken["lifecycle"][first][0])
    del entry["canonical_id"]
    broken["lifecycle"][first][0] = entry
    with pytest.raises(R.ReportingError, match="canonical_id"):
        R.validate_repetition(broken, "test")


def test_wrong_case_count_and_duplicates_are_fatal():
    short = evidence(); short["cases"] = short["cases"][:19]
    with pytest.raises(R.ReportingError, match="expected 20 cases"):
        R.validate_repetition(short, "test")
    duped = evidence(); duped["cases"][1] = copy.deepcopy(duped["cases"][0])
    with pytest.raises(R.ReportingError, match="duplicate case_id"):
        R.validate_repetition(duped, "test")


def test_unknown_failure_class_in_evidence_is_fatal():
    broken = evidence()
    broken["cases"][0]["failure_classes"] = ["not_a_real_class"]
    with pytest.raises(R.ReportingError, match="unknown failure class"):
        R.validate_repetition(broken, "test")


def test_stored_aggregate_disagreeing_with_leaf_evidence_is_fatal():
    """A corrupted summary must not corrupt the derived result - it must be caught."""
    data = evidence()
    rebuilt = R.rebuild_case_totals(data)
    corrupted = {name: m.value_or_raise() for name, m in rebuilt.items()}
    corrupted["stale_persistence"] = corrupted.get("stale_persistence", 0) + 99
    with pytest.raises(R.ReportingError, match="stored aggregate disagrees"):
        R.reconcile(corrupted, rebuilt, "test", R.Stream.CASE)


def test_case_totals_are_rebuilt_from_leaf_cases_not_stored_totals():
    data = evidence()
    rebuilt = R.rebuild_case_totals(data)
    manual: dict[str, int] = {}
    for case in data["cases"]:
        for name in case["failure_classes"]:
            manual[name] = manual.get(name, 0) + 1
    for name, count in manual.items():
        assert rebuilt[name].value_or_raise() == count
    assert "false_supersession" not in rebuilt, "case stream must never carry a lifecycle-only class"


def test_lifecycle_replay_uses_the_frozen_scorer():
    replayed = R.replay_lifecycle(evidence())
    assert replayed["false_supersession"].payload()["status"] == "measured_zero"
    assert replayed["false_supersession"].value_or_raise() == 0


@pytest.mark.skipif(not LEDGER.exists(), reason="ledger is produced by build_round2_ledger.py")
def test_published_ledger_separates_streams_and_carries_lineage():
    ledger = json.loads(LEDGER.read_text())
    assert ledger["contract_sha256"] == CONTRACT_SHA
    for engine, entry in ledger["engines"].items():
        assert "false_supersession" not in entry["case_scorer"], f"{engine} leaked a lifecycle class into case totals"
        assert entry["lineage"], f"{engine} has no evidence lineage"
        for cell in entry["case_scorer"].values():
            assert cell["status"] in ("present", "measured_zero")


@pytest.mark.skipif(not DERIVED.exists(), reason="derived report is produced by build_round2_ledger.py")
def test_round2_conclusions_survive_independent_derivation():
    derived = json.loads(DERIVED.read_text())
    assert derived["preregistered_seven_recur_in_all_append_only"] is True
    assert set(derived["identical_across_append_only"]) == {
        "configuration_collapse", "failed_procedure_adoption", "false_persistence",
        "late_history_corruption", "unsupported_evidence"}
    fs = derived["false_supersession_lifecycle"]
    assert fs["gen33_agentmemory"] == 3
    assert fs["gen29_perseus"] == 0 and fs["gen31_hindsight"] == 0 and fs["gen32_mem0"] == 0
    assert derived["false_supersession_unique_to_retiring_engine"] is True
    assert derived["claim_retirement_halves_configuration_collapse"] is True
    assert derived["claim_retirement_reduces_false_persistence"] is True
