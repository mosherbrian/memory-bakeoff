"""Gen107: provenance and composition guards for the Round 3 closure.

These are structured assertions, not prose greps. The one place a substring
check appears, it is checking for a MACHINE-readable marker that the readout
itself owns, not for phrasing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_bakeoff import evidence as EV
from memory_bakeoff import round3_closure as C

ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = ROOT / "results" / "gen107" / "attempt1"


def payload():
    path = ATTEMPT / "round3_closure.json"
    if not path.exists():
        pytest.skip("closure artifact not built in this checkout")
    return json.loads(path.read_text())


# --- 1. heterogeneous mechanisms may never be pooled -------------------------
def test_closure_carries_no_pooled_mechanism_score():
    C.assert_no_pooled_mechanism_score(payload())


def test_pooling_guard_fires_on_a_real_pooled_field():
    with pytest.raises(ValueError, match="not commensurable"):
        C.assert_no_pooled_mechanism_score({"supersession_score": 0.7})


def test_pooling_guard_fires_on_an_aggregate_spanning_kinds():
    with pytest.raises(ValueError, match="spans"):
        C.assert_no_pooled_mechanism_score(
            {"mechanism_kind": C.EXPLICIT_LINEAGE, "inner":
                {"mechanism_kind": C.STATE_TRANSITION, "removed": 12}})


def test_pooling_guard_tolerates_prose_about_the_thing_it_forbids():
    """The first version fired on our own line saying there is no such score."""
    C.assert_no_pooled_mechanism_score(
        {"note": "There is no supersession score; kinds are incommensurable."})


# --- 2. Gen102 is superseded, never canonical --------------------------------
def test_gen102_is_recorded_superseded_and_preserved():
    C.assert_gen102_is_superseded(payload())


def test_supersession_guard_fires_when_gen102_is_missing():
    with pytest.raises(ValueError, match="superseded AND preserved"):
        C.assert_gen102_is_superseded({"supersessions": []})


def test_gen102_report_still_exists_and_is_marked():
    report = ROOT / "research" / "PI_SUPERSESSION_ABLATION_GEN102.md"
    assert report.exists(), "superseded evidence must be preserved, not deleted"
    assert "superseded-by: ROUND3_SUPERSESSION_RESULT.md" in report.read_text()[:400]


# --- 3. legacy evidence may not be called manifest-verified ------------------
def test_gen104_and_gen105_evidence_is_not_manifest_verified():
    C.assert_legacy_not_called_verified(payload()["source_registry"])
    from_104_105 = [e for e in payload()["source_registry"]
                    if e["source_generation"] in (104, 105)]
    assert from_104_105
    # The rule is that none may claim verification - not that all are legacy.
    # The blast radius is a deterministic recomputation from committed fixtures,
    # so COMMITTED_REPORT is the honest label for it.
    assert all(e["evidence"] != C.MANIFEST_VERIFIED for e in from_104_105)
    assert any(e["evidence"] == C.LEGACY_UNMANIFESTED for e in from_104_105)


def test_legacy_guard_fires_on_a_false_verified_label():
    with pytest.raises(ValueError, match="cannot be MANIFEST_VERIFIED"):
        C.assert_legacy_not_called_verified(
            [{"id": "x", "source_generation": 105,
              "evidence": C.MANIFEST_VERIFIED}])


def test_no_round3_conclusion_claims_manifest_verification():
    assert payload()["evidence_class_counts"][C.MANIFEST_VERIFIED] == 0


# --- 4. the v3-only blast radius may not retract Gen97 or Gen99 --------------
def test_gen97_and_gen99_are_not_retracted():
    C.assert_v1_v2_not_retracted(payload())
    retracted = " ".join(str(r["claim"]) for r in payload()["retractions"])
    assert "Gen97" not in retracted and "Gen99" not in retracted


def test_blast_radius_guard_fires_on_a_wrongful_retraction():
    with pytest.raises(ValueError, match="cannot be retracted by a v3-only"):
        C.assert_v1_v2_not_retracted(
            {"retractions": [{"claim": "Gen99's replication verdict"}]})


def test_blast_radius_is_recorded_with_all_three_fixtures():
    entry = next(e for e in payload()["source_registry"]
                 if e["id"] == "ingest-order-blast-radius")
    for fragment in ("0/4", "0/16", "16/16"):
        assert fragment in entry["measure"]


# --- 5. the closure artifact lives under the evidence contract --------------
def test_closure_artifact_is_manifested_and_verifies():
    if not ATTEMPT.exists():
        pytest.skip("closure artifact not built in this checkout")
    result = EV.verify(ATTEMPT)
    assert result["manifest_present"] and result["verified"] is True
    assert result["missing"] == [] and result["mismatched"] == []


def test_closure_attempt_cannot_be_overwritten(tmp_path):
    out = EV.next_attempt(tmp_path, 107)
    EV.write_evidence(out, "round3_closure.json", {"a": 1})
    with pytest.raises(FileExistsError):
        EV.write_evidence(out, "round3_closure.json", {"a": 2})


def test_closure_path_is_attempt_scoped():
    assert ATTEMPT.parent.name == "gen107" and ATTEMPT.name.startswith("attempt")


# --- round-level composition -------------------------------------------------
def test_round3_is_closed_with_exactly_one_recommendation():
    p = payload()
    assert p["status"] == "CLOSED"
    assert isinstance(p["next_line"]["recommendation"], str)
    assert p["next_line"]["explicitly_not_opened_here"] is True


def test_every_registry_entry_declares_its_evidence_class():
    for entry in payload()["source_registry"]:
        assert entry["evidence"] in C.EVIDENCE_CLASSES, entry["id"]
        assert entry.get("mechanism_kind") in (None,) + C.MECHANISM_KINDS


def test_provenance_limitation_is_recorded_and_not_reconstructed():
    ids = {l["id"] for l in payload()["limitations"]}
    assert "cell-level-diff-irrecoverable" in ids
    assert all(l["not_reconstructed"] and l["no_backdated_manifest"]
               for l in payload()["limitations"])
