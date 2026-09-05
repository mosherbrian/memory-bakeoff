"""The backfill fixture must be answerable, and the valid_at defect must stay visible.

The second half matters more than the first: Gen73's finding is that a harness
substitution made one arm of the Gen72 mirror untestable, and a later change that
quietly hides it would resurrect a retracted claim.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff import backfill as B
from memory_bakeoff.longitudinal import (build_longitudinal_fixture,
                                         score_longitudinal_case)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results/backfill_gen73/valid_at_audit.json"


def test_the_fixture_carries_backfills_at_three_depths():
    assert set(B.BACKFILL_DEPTH.values()) == {"shallow", "deep", "very_deep"}
    assert len(B.BACKFILL_DEPTH) == 4


def test_both_backfill_fates_are_represented():
    assert set(B.BACKFILL_FATE.values()) == {"historical_only", "later_corrected"}


def test_belief_retention_is_measured_more_than_once():
    fixture = B.build_backfill_fixture()
    beliefs = [c for c in fixture.cases
               if str(c.target_kind) == "historical_belief"]
    assert len(beliefs) >= 2
    assert len({c.truth_key for c in beliefs}) >= 2


def test_a_perfect_answer_scores_clean_on_every_case():
    fixture = B.build_backfill_fixture()
    for case in fixture.cases:
        assert not score_longitudinal_case(
            fixture, case, case.expected_ids).failure_classes, case.id


def test_every_expected_observation_is_ingested_by_its_checkpoint():
    fixture = B.build_backfill_fixture()
    for case in fixture.cases:
        visible = {o.id for o in fixture.prefix(case.checkpoint_id)}
        assert set(case.expected_ids) <= visible, case.id


def test_queries_match_the_terse_style_of_longitudinal_v1():
    """A full-sentence question is a different retrieval task; comparability needs parity."""
    fixture = B.build_backfill_fixture()
    for case in fixture.cases:
        assert not case.query.endswith("?"), case.id
        assert len(case.query.split()) <= 6, case.id


def test_the_original_fixture_is_untouched():
    original = build_longitudinal_fixture()
    assert len(original.observations) == 16 and len(original.cases) == 20


def test_the_audit_shows_every_backfill_is_unreachable_by_construction():
    payload = json.loads(AUDIT.read_text())
    backfill = next(a for a in payload["audits"] if a["fixture"] == "backfill-v1")
    assert sorted(backfill["unreachable"]) == ["B004", "B006", "B008", "B011"]


def test_the_defect_also_affects_the_original_fixtures_one_backfill():
    """This is why the Gen72 late-arrival arm has to be retracted, not just noted."""
    payload = json.loads(AUDIT.read_text())
    original = next(a for a in payload["audits"] if a["fixture"] == "longitudinal-v1")
    assert original["unreachable"] == ["L011"]


def test_the_audit_records_the_substitution_and_why_it_hid():
    payload = json.loads(AUDIT.read_text())
    assert "TRANSACTION-time instant" in payload["defect"]
    assert "clocks coincide" in payload["why_it_hid"]
    assert payload["engines_run"] == 0
