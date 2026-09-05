"""Gen83: the recommended_procedure axis audited before its zero is interpreted."""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

from memory_bakeoff import procedure_reachability as audit
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_longitudinal_case,
                                         FailureClass, TargetKind)

ROOT = pathlib.Path(__file__).resolve().parents[1]

MISSING = str(FailureClass.PROCEDURE_RECOMMENDATION_MISSING)
ADOPTION = str(FailureClass.FAILED_PROCEDURE_ADOPTION)


@pytest.fixture(scope="module")
def fixture():
    return build_longitudinal_fixture()


@pytest.fixture(scope="module")
def case(fixture):
    return next(c for c in fixture.cases if c.id == audit.CASE_ID)


def test_lq10_is_the_only_procedure_case(fixture):
    procedure = [c.id for c in fixture.cases
                 if c.target_kind is TargetKind.RECOMMENDED_PROCEDURE]
    assert procedure == [audit.CASE_ID], "the whole axis rests on one case"


def test_both_classes_fire_and_the_case_can_stay_silent(fixture, case):
    control = audit.controls(score_longitudinal_case, fixture, case)
    assert control["silent_on_correct_answer"]["classes"] == ()
    assert control["silent_with_correct_plus_unrelated"]["classes"] == ()
    assert MISSING in control["missing_fires_on_empty"]["classes"]
    assert MISSING in control["missing_fires_on_unrelated"]["classes"]
    assert control["adoption_fires_on_both"]["classes"] == (ADOPTION,)


def test_the_scorer_ignores_rank(fixture, case):
    """Returning the right answer first is scored identically to returning it last."""
    first = score_longitudinal_case(fixture, case, (audit.EXPECTED, audit.PROHIBITED))
    last = score_longitudinal_case(fixture, case, (audit.PROHIBITED, audit.EXPECTED))
    assert first.failure_classes == last.failure_classes == (ADOPTION,)


def test_query_shares_no_word_with_any_record(fixture, case):
    report = audit.discriminability(fixture, case.query)
    assert report["observations_sharing_a_query_token"] == []
    assert report["pair_shares_truth_key"]
    assert report["pair_shares_scope"]
    assert report["pair_shares_configuration"]
    assert report["outcome_label_published"] is False


def test_procedure_outcome_is_never_published(fixture):
    """The label that separates the two records is withheld from every engine."""
    for observation in fixture.prefix(audit.CHECKPOINT_ID):
        assert "procedure_outcome" not in observation.public_dict()
    from memory_bakeoff.providers import perseus_longitudinal
    with pytest.raises(ValueError):
        perseus_longitudinal.assert_public_only({"procedure_outcome": "success"})


def test_committed_records_show_every_engine_retrieved_the_recommendation():
    from scripts.run_gen83_procedure_audit import committed_windows
    windows = committed_windows(ROOT)
    assert set(windows) == set(audit.OBSERVED)
    for engine, rows in windows.items():
        assert len(rows) == audit.REPETITIONS
        for row in rows:
            assert audit.EXPECTED in row["returned"], f"{engine} lost the recommendation"
            assert row["failure_classes"] == [ADOPTION]
            assert MISSING not in row["failure_classes"]


def test_the_observed_table_matches_the_committed_records():
    from scripts.run_gen83_procedure_audit import committed_windows
    windows = committed_windows(ROOT)
    for engine, entry in audit.OBSERVED.items():
        for row in windows[engine]:
            assert tuple(row["returned"]) == entry["returned"]
            assert row["expected_rank"] == entry["expected_rank"]
            assert row["prohibited_rank"] == entry["prohibited_rank"]
            assert row["limit"] == entry["limit"]


def test_the_window_covers_most_of_the_corpus(fixture):
    pressure = audit.window_pressure(len(fixture.prefix(audit.CHECKPOINT_ID)), 5)
    assert pressure["corpus_size"] == 8
    assert pressure["fraction_of_corpus_returned"] > 0.5
    assert pressure["chance_of_passing_under_uniform_sampling"] < 0.3


def test_no_runner_supplies_a_reader_answer_for_this_case():
    """Walk the AST rather than grep: the claim is about what the code does."""
    populated = []
    for path in sorted((ROOT / "scripts").glob("*.py")) + \
            sorted((ROOT / "src" / "memory_bakeoff").rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "reader_answer" \
                    and not (isinstance(node.value, ast.Constant) and node.value.value is None):
                populated.append(path.name)
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == "reader_answer" \
                            and not (isinstance(value, ast.Constant) and value.value is None):
                        populated.append(path.name)
    assert populated == [], f"reader_answer is populated somewhere: {populated}"


def test_attribution_names_a_reader_capability_not_a_memory_result():
    result = audit.attribution()
    assert result["procedure_recommendation_missing_observed"] == 0
    assert result["failed_procedure_adoption_observed"] == 12
    assert sorted(result["engines_that_retrieved_the_recommendation"]) == \
        sorted(audit.OBSERVED)
    assert result["retrievable_memory_verdict"] == audit.NOT_APPLICABLE
    assert result["reader_capability_verdict"] == audit.READER_CAPABILITY


def test_verdict_records_not_demonstrable_rather_than_a_zero():
    verdict = audit.verdict()
    assert verdict["engine_procedure_memory"] == audit.NOT_DEMONSTRABLE
    assert verdict["what_the_axis_actually_exercises"] == audit.READER_CAPABILITY
    assert verdict["harness_defect"] == audit.ADAPTER_OMISSION
    assert verdict["gen68_line_status"].startswith("REATTRIBUTED")
    assert verdict["no_engine_runs"] is True


def test_audit_payload_was_written():
    payload = json.loads((ROOT / "results" / "procedure_audit_gen83" / "audit.json").read_text())
    assert payload["contract"]["contract_version"] == audit.CONTRACT_VERSION
    assert payload["attribution"]["procedure_recommendation_missing_observed"] == 0
