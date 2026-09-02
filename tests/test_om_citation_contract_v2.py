import glob
import json
import socket
from pathlib import Path

import pytest

from memory_bakeoff.om_context_production import CASES, fixture_sha256, grade_reader, scorer_contract_sha256
from memory_bakeoff.om_citation_contract_v2 import CONTRACT_VERSION, SCORER_VERSION, contract_sha256, grade_reader_v2, regrade, reproduces_frozen_support, resolve_citation, responses_fingerprint, typed_projection

V1_FIXTURE_SHA = "cce9fdf494ad6965897646beff1ef535d4aeb73ba81f3ea83e6fe68e1218acdc"
V1_SCORER_SHA = "f69068bbb3a76bf9ca64edeb3a5b14411538d6e4494211d765efa82e50e702bd"
V2_CONTRACT_SHA = "f6250dc2acb3b168eb994261763d931b671ff9236bf57370484aa6722b331286"

CONTROL_PLANE = Path(".control-plane")
GEN27_RUNS = (("gen27-context-valid-r1c", 1), ("gen27-context-valid-r23", 1), ("gen27-context-valid-r23", 2))

DETAILS = {
    "type": "om.folded",
    "observations": [
        {"id": "aaaaaaaaaaaa", "sourceEntryIds": ["native-a"]},
        {"id": "bbbbbbbbbbbb", "sourceEntryIds": ["native-b"]},
        {"id": "cccccccccccc", "sourceEntryIds": []},
    ],
    "reflections": [
        {"id": "dddddddddddd", "supportingObservationIds": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]},
        {"id": "aaaaaaaaaaaa", "supportingObservationIds": ["aaaaaaaaaaaa"]},
        {"id": "eeeeeeeeeeee", "supportingObservationIds": []},
    ],
}
NATIVE_TO_ANCHOR = {"native-a": "A01", "native-b": "A02"}


def projection():
    return typed_projection(DETAILS, NATIVE_TO_ANCHOR)


def case(case_id):
    return {item.id: item for item in CASES}[case_id]


def test_v1_contract_is_immutable_under_v2():
    assert fixture_sha256() == V1_FIXTURE_SHA
    assert scorer_contract_sha256() == V1_SCORER_SHA
    prefixed = {"answer": "quartz", "citations": ["obs-aaaaaaaaaaaa"]}
    assert grade_reader(case("Q01"), prefixed, {"aaaaaaaaaaaa": {"A08"}})["invalid_citations"] == ["obs-aaaaaaaaaaaa"]


def test_v2_contract_identity_is_frozen():
    assert CONTRACT_VERSION == "om-context-production-v2"
    assert SCORER_VERSION == "om-context-production-scorer-v2"
    assert contract_sha256() == V2_CONTRACT_SHA


def test_typed_projection_keeps_roles_apart_and_resolves_support_chains():
    proj = projection()
    assert proj["observation"]["aaaaaaaaaaaa"] == {"A01"}
    assert proj["reflection"]["dddddddddddd"] == {"A01", "A02"}
    assert proj["reflection"]["eeeeeeeeeeee"] == set()
    assert reproduces_frozen_support(proj, {"aaaaaaaaaaaa": ["A01"], "bbbbbbbbbbbb": ["A02"], "cccccccccccc": [], "dddddddddddd": ["A01", "A02"], "eeeeeeeeeeee": []})


def test_prefixed_and_dual_role_citations_resolve_to_captured_roles():
    proj = projection()
    assert resolve_citation("obs-bbbbbbbbbbbb", proj) == (frozenset({"A02"}), "observation", None)
    assert resolve_citation("ref-dddddddddddd", proj) == (frozenset({"A01", "A02"}), "reflection", None)
    assert resolve_citation("obs-aaaaaaaaaaaa", proj)[1] == "observation"
    assert resolve_citation("ref-aaaaaaaaaaaa", proj)[1] == "reflection"
    assert resolve_citation("aaaaaaaaaaaa", proj) == (frozenset({"A01"}), "observation+reflection", None)


def test_citation_resolution_fails_closed():
    proj = projection()
    assert resolve_citation("mem-aaaaaaaaaaaa", proj)[2] == "unknown_prefix"
    assert resolve_citation("obs-ffffffffffff", proj)[2] == "unknown_id"
    assert resolve_citation("obs-NOTHEX", proj)[2] == "malformed_id"
    assert resolve_citation("obs-dddddddddddd", proj)[2] == "type_mismatch"
    assert resolve_citation("ref-bbbbbbbbbbbb", proj)[2] == "type_mismatch"
    assert resolve_citation("", proj)[2] == "malformed"
    conflicting = typed_projection({"observations": [{"id": "aaaaaaaaaaaa", "sourceEntryIds": ["native-a"]}], "reflections": [{"id": "aaaaaaaaaaaa", "supportingObservationIds": ["bbbbbbbbbbbb"]}]}, NATIVE_TO_ANCHOR)
    assert resolve_citation("aaaaaaaaaaaa", conflicting)[2] == "ambiguous_role"


def test_support_is_never_inferred_from_answer_text():
    proj = projection()
    graded = grade_reader_v2(case("Q10"), {"answer": "no, the deployment failed", "citations": []}, proj)
    assert graded["unsupported_citation"] and not graded["pass"]


def test_regrade_consumes_stored_responses_and_makes_no_network_call(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("regrade must not open a socket")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    stored = [{"grade": {"case_id": "Q01"}, "response": {"answer": "quartz", "citations": ["obs-aaaaaaaaaaaa"]}}]
    result = regrade(stored, projection())
    assert result["case_count"] == 1
    assert result["details"][0]["response"] is stored[0]["response"]
    assert responses_fingerprint(stored) == responses_fingerprint(stored)


def frozen_repetition(run, rep_no):
    summary = json.loads((CONTROL_PLANE / run / "summary.json").read_text())
    rep = [item for item in summary["repetitions"] if item["rep"] == rep_no][0]
    entry_id = rep["captured_compaction"]["entry_id"]
    path = glob.glob(f"external/pi-observational-memory/.control-plane/{run}/rep{rep_no}/sessions/*.jsonl")[0]
    for line in open(path):
        if entry_id in line:
            record = json.loads(line)
            if record.get("id") == entry_id:
                return rep, record["details"]
    raise AssertionError(f"frozen fold {entry_id} not found")


@pytest.mark.skipif(not (CONTROL_PLANE / "gen27-context-valid-r1c" / "summary.json").exists(), reason="frozen Gen27 capture is local-only")
def test_gen27_q10_passes_only_through_its_exact_native_id():
    rep, details = frozen_repetition("gen27-context-valid-r1c", 1)
    proj = typed_projection(details, rep["native_anchor_mapping"])
    assert reproduces_frozen_support(proj, rep["captured_compaction"]["visible_support"])
    stored = [item for item in rep["reader"]["details"] if item["grade"]["case_id"] == "Q10"][0]
    assert stored["response"]["citations"] == ["obs-82e397393ad2"]
    assert not stored["grade"]["pass"]
    anchors, role, reason = resolve_citation("obs-82e397393ad2", proj)
    assert reason is None and role == "observation" and "A04" in anchors
    assert grade_reader_v2(case("Q10"), stored["response"], proj)["pass"]
    swapped = {"answer": stored["response"]["answer"], "citations": ["obs-7fee3f56ae22"]}
    assert not grade_reader_v2(case("Q10"), swapped, proj)["pass"]


@pytest.mark.skipif(not (CONTROL_PLANE / "gen27-context-valid-r1c" / "summary.json").exists(), reason="frozen Gen27 capture is local-only")
def test_every_frozen_repetition_reproduces_v1_support_before_regrade():
    for run, rep_no in GEN27_RUNS:
        rep, details = frozen_repetition(run, rep_no)
        proj = typed_projection(details, rep["native_anchor_mapping"])
        assert reproduces_frozen_support(proj, rep["captured_compaction"]["visible_support"])
