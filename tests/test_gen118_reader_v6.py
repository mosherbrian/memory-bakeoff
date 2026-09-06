"""Gen118: v6 must reject every near-miss the control plane enumerated.

Gen117 failed because a correct selection expressed as the distinguishing word
alone scored UNSUPPORTED_VALUE. The ruling was NOT to accept the token - that
acceptance class was suggested by the observed failures - but to require the
complete phrase and say so in the prompt. These tests are the boundary.
"""
import re

import pytest

from memory_bakeoff import reader_interference_v5 as V5
from memory_bakeoff import reader_interference_v6 as V6

FIX = V6.build_fixture()
CASES = {c["case_id"]: c for c in FIX["cases"]}
CASE = CASES["core01|CONFLICT_CURRENT_FIRST"]
VALS = {int(k): v for k, v in CASE["canonical_values"].items()}
FULL, OTHER = VALS[2], VALS[1]
HEAD, TOKEN = FULL.split()


def body(**kw):
    b = {"ok": True, "disposition": "RESOLVED",
         "selected_record_id": CASE["expected_record_id"],
         "selected_value": FULL, "prior_values": [],
         "citations": [CASE["expected_record_id"]]}
    b.update(kw)
    return b


# --- freshness ----------------------------------------------------------------
def test_no_v5_string_survives_into_v6():
    v5 = " ".join(V5.project_prompt(c) for c in V5.build_fixture()["cases"]).casefold()
    v6 = " ".join(V6.project_prompt(c) for c in FIX["cases"]).casefold()
    burned = {v.split()[0] for c in V5.CORES for v in V5.canonical_values(c).values()}
    burned |= {v.split()[1] for c in V5.CORES for v in V5.canonical_values(c).values()}
    burned |= {c["subject"].split()[1].casefold() for c in V5.CORES}
    leaked = [w for w in burned if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", v6)]
    assert leaked == [], f"v5 material reused in v6: {leaked}"
    assert len(set(V6.build_fixture()["cases"][0]["records"][0]["record_id"]) & set()) == 0
    v5_ids = {r["record_id"] for c in V5.build_fixture()["cases"] for r in c["records"]}
    v6_ids = {r["record_id"] for c in FIX["cases"] for r in c["records"]}
    assert not (v5_ids & v6_ids), "record ids collide with v5"


def test_structure_matches_the_frozen_shape():
    assert len(V6.CORES) == 12 and len(CASES) == 60
    assert len({V6.project_prompt(c) for c in FIX["cases"]}) == 60
    assert len(V6.ONTOLOGY) == 9


def test_the_prompt_states_the_verbatim_rule():
    p = V6.project_prompt(CASE)
    assert "copy the ENTIRE value phrase exactly" in p
    assert "only the distinguishing word" in p
    assert "inside a sentence" in p


# --- the boundary the ruling draws -------------------------------------------
@pytest.mark.parametrize("bad,why", [
    (None,                          "no value at all"),
    ("",                            "empty"),
])
def test_missing_value_is_not_a_selection(bad, why):
    assert V6.classify_answer(body(selected_value=bad), VALS) != V6.CURRENT_ONLY


def test_the_distinguishing_token_alone_fails():
    """The Gen117 failure. It must still fail - that is the whole ruling."""
    assert V6.classify_answer(body(selected_value=TOKEN), VALS) == V6.UNSUPPORTED_VALUE


def test_the_shared_head_noun_alone_fails():
    assert V6.classify_answer(body(selected_value=HEAD), VALS) == V6.UNSUPPORTED_VALUE


@pytest.mark.parametrize("bad", [
    lambda: f"The terminal berths at {FULL}.",     # embedded in a sentence
    lambda: f"{FULL}.",                            # trailing punctuation
    lambda: f"the {FULL}",                         # prefix
    lambda: f"{FULL}s",                            # suffix
    lambda: " ".join(reversed(FULL.split())),      # reordered
    lambda: FULL.replace("o", "ο", 1),        # Greek omicron lookalike
    lambda: FULL + " " + OTHER,                    # both values
])
def test_near_misses_are_not_the_exact_value(bad):
    cls = V6.classify_answer(body(selected_value=bad()), VALS)
    assert cls != V6.CURRENT_ONLY, f"{bad()!r} must not pass as the exact value"


@pytest.mark.parametrize("ok", [
    lambda: FULL,
    lambda: FULL.upper(),                          # casefolded
    lambda: FULL.replace(" ", "  "),               # collapsed whitespace
    lambda: f"  {FULL}  ",                         # stripped
])
def test_canonicalisation_accepts_exactly_what_it_says(ok):
    assert V6.classify_answer(body(selected_value=ok()), VALS) == V6.CURRENT_ONLY


def test_the_policy_is_written_down_and_matches_behaviour():
    assert "casefold" in V6.CANONICALISATION and "whitespace" in V6.CANONICALISATION
    assert "fuzzy" in V6.CANONICALISATION and "edit-distance" in V6.CANONICALISATION
    assert V6.CANONICALISATION in str(V6.contract_payload())


# --- the other three legs of success are still load-bearing -------------------
def test_right_value_wrong_record_fails():
    wrong = CASE["records"][1]["record_id"]
    assert V6.grade(body(selected_record_id=wrong), CASE)["meets_success_state"] is False


def test_right_value_and_record_but_no_citation_fails():
    assert V6.grade(body(citations=[]), CASE)["meets_success_state"] is False


def test_right_value_and_record_but_unshown_citation_fails():
    assert V6.grade(body(citations=["REC-NOTSHOWN"]), CASE)["meets_success_state"] is False


def test_the_complete_conjunction_passes():
    g = V6.grade(body(), CASE)
    assert g["meets_success_state"] is True
    assert g["answer_class"] == V6.CURRENT_ONLY


def test_insufficient_with_any_selection_is_refused():
    bad = ('{"disposition":"INSUFFICIENT","selected_record_id":"R",'
           '"selected_value":null,"prior_values":[],"citations":[]}')
    assert V6.parse_response(bad)["ok"] is False


def test_unresolved_with_a_selection_is_refused():
    bad = ('{"disposition":"UNRESOLVED","selected_record_id":null,'
           f'"selected_value":"{FULL}","prior_values":[],"citations":[]}}')
    assert V6.parse_response(bad)["ok"] is False


def test_history_cannot_manufacture_a_contradiction():
    hist = body(prior_values=[OTHER])
    assert V6.classify_answer(hist, VALS) == V6.CURRENT_WITH_HISTORY
    assert V6.grade(hist, CASE)["meets_success_state"] is True


def test_every_response_maps_to_exactly_one_class():
    seen = {r["answer_class"] for r in V6._ontology_table()}
    assert seen <= set(V6.ONTOLOGY)
    assert set(V6.ONTOLOGY) - seen == set(), "every class must be reachable"
