"""The report must state the numbers and refuse to summarise them.

The whole point of Gen65 is that a single word tracked none of the movement in
the underlying evidence, so these tests pin down that no verdict is produced and
that cross-run comparisons only compare what both runs actually scored.
"""
from __future__ import annotations

import json
from pathlib import Path

from memory_bakeoff.evidence_ruler import gate_suitability as G

ROOT = Path(__file__).resolve().parents[1]


def run(statuses, population, wrongs, retention=None) -> dict:
    return {
        "statuses": statuses,
        "primary_population": {"tasks": population, "wrong_candidates": len(wrongs)},
        "flagged_wrongs": sum(1 for v in wrongs.values() if v),
        "tasks": {task: {"wrongs": {name: {"passed": not flagged}
                                    for name, flagged in items.items()}}
                  for task, items in _by_task(wrongs).items()},
        "retention": retention or {},
    }


def _by_task(wrongs):
    grouped: dict[str, dict] = {}
    for key, flagged in wrongs.items():
        task, name = key.split("/")
        grouped.setdefault(task, {})[name] = flagged
    return grouped


def test_it_reaches_no_verdict():
    payload = G.report("x", run({"a": "REFERENCE_VALID"}, ["a"], {"a/w": True}))
    assert payload["gate_suitable"] is None
    assert "not a single number" in payload["why_no_verdict"]


def test_the_unsafe_rate_ignores_tasks_with_no_bank():
    statuses = {"a": "UNSAFE_AS_GATE", "b": "REFERENCE_VALID", "c": "NO_BANK"}
    assert G.unsafe_rate({"statuses": statuses}) == (1, 2)


def test_a_hollowed_bank_is_not_counted_as_unsafe():
    """It is inadmissible for a different reason, and conflating them hides it."""
    statuses = {"a": "HOLLOWED", "b": "REFERENCE_VALID"}
    assert G.unsafe_rate({"statuses": statuses}) == (0, 2)


def test_detection_losses_only_compare_tasks_both_runs_scored():
    baseline = run({"a": "REFERENCE_VALID", "b": "UNSAFE_AS_GATE"}, ["a"],
                   {"a/w1": True, "b/w2": True})
    later = run({"a": "REFERENCE_VALID", "b": "REFERENCE_VALID"}, ["a", "b"],
                {"a/w1": True, "b/w2": False})
    # b/w2 was "caught" by a bank the baseline had already ruled unusable, so it
    # is not a loss - b was never in the baseline's scored population.
    assert G.detection_losses(later, baseline) == []


def test_a_real_loss_inside_a_shared_task_is_named():
    baseline = run({"a": "REFERENCE_VALID"}, ["a"], {"a/w1": True, "a/w2": True})
    later = run({"a": "REFERENCE_VALID"}, ["a"], {"a/w1": True, "a/w2": False})
    assert G.detection_losses(later, baseline) == ["a/w2"]


def test_retention_range_is_reported_when_a_filter_ran():
    payload = G.report("x", run({"a": "REFERENCE_VALID"}, ["a"], {"a/w": True},
                                retention={"a": 0.9, "b": 0.5}))
    assert payload["retention_min"] == 0.5 and payload["retention_max"] == 0.9


def test_the_recorded_synthesis_matches_the_committed_outcomes():
    payload = json.loads(
        (ROOT / "results/pi_gate_question_gen65/gate_question.json").read_text())
    rows = payload["generations"]
    assert rows["gen60"]["unsafe_banks"] == 4
    assert rows["gen61"]["unsafe_banks"] == 4
    assert rows["gen64"]["unsafe_banks"] == 4
    assert rows["gen62"]["unsafe_banks"] == 0
    assert rows["gen62"]["removal_precision"] < 0.15
    assert rows["gen64"]["removal_precision"] > 0.25
    assert rows["gen64"]["retention_min"] > 0.8
    for label in rows:
        assert rows[label]["gate_suitable"] is None


def test_the_conclusion_is_recorded_with_its_scope():
    payload = json.loads(
        (ROOT / "results/pi_gate_question_gen65/gate_question.json").read_text())
    conclusion = payload["conclusion"]
    assert conclusion["answer"].startswith("not demonstrated")
    assert "reviewer" in conclusion["supported_use"]
    assert "one run per condition" in conclusion["scope"]
    assert len(conclusion["decisive_arc"]) == 5
