"""The closure must record all six conditions and refuse to reopen the branch.

Reads the committed closure file, so if a later generation quietly changes the
recorded arc these fail rather than the story drifting.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "results/pi_gate_branch_closed_gen67/gate_question.json"


def payload() -> dict:
    return json.loads(CLOSURE.read_text())


def test_every_condition_is_recorded():
    rows = payload()["generations"]
    assert set(rows) == {"gen60", "gen61", "gen62", "gen64", "gen66"}


def test_the_unsafe_rate_never_moved_except_by_destruction():
    rows = payload()["generations"]
    for label in ("gen60", "gen61", "gen64", "gen66"):
        assert rows[label]["unsafe_banks"] == 4, label
    # The one exception, and it is the run that emptied its banks.
    assert rows["gen62"]["unsafe_banks"] == 0
    assert rows["gen62"]["removal_precision"] < 0.15


def test_repository_context_did_not_help():
    rows = payload()["generations"]
    assert rows["gen66"]["unsafe_banks"] == rows["gen64"]["unsafe_banks"]
    assert rows["gen66"]["retention_min"] > 0.5      # nothing hollowed
    assert rows["gen66"]["wrongs_caught"] == 12      # detection intact


def test_detection_held_across_every_usable_condition():
    rows = payload()["generations"]
    for label in ("gen60", "gen61", "gen64", "gen66"):
        assert rows[label]["wrongs_caught"] == rows[label]["wrongs_in_population"]
        assert rows[label]["detection_losses_vs_baseline"] == []


def test_the_branch_is_recorded_as_closed():
    conclusion = payload()["conclusion"]
    assert "closed" in conclusion["branch_closed"].lower()
    assert "non-independent" in conclusion["explicitly_not_the_next_iteration"]


def test_a_candidate_inspecting_checker_is_not_the_next_iteration():
    note = payload()["conclusion"]["explicitly_not_the_next_iteration"]
    assert "must not be reported as one" in note


def test_the_scope_stays_bounded():
    conclusion = payload()["conclusion"]
    assert "one run per condition" in conclusion["scope"]
    assert "not a" in conclusion["scope"]


def test_the_arc_names_the_context_ablation():
    arc = payload()["conclusion"]["decisive_arc"]
    assert len(arc) == 6
    assert any("candidate-blind" in step and "STILL 4 of 8" in step for step in arc)
