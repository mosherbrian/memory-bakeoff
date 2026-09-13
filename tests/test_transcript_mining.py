"""Self-test for the transcript miner's detectors on SYNTHETIC fixtures.

No real transcript content is used here — every fixture is constructed.
Locks: operator-text extraction (tool results / command wrappers / meta
records are not operator speech), each correction class firing on a true
positive and staying quiet on neutral turns, durable-fact classes,
repeat detection across files, and the local-only output contract (stats
carry no excerpts).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.experiment_20260912_transcript_mining.mine import (  # noqa: E402
    CORRECTION_PATTERNS,
    FACT_PATTERNS,
    normalize_for_repeat,
    operator_texts,
    scan,
)

PROJECT = "-var-home-bmosher-memory-bake-off"


def _user(text: str, meta: bool = False) -> dict:
    r = {"type": "user", "message": {"role": "user", "content": text},
         "timestamp": "2026-09-13T00:00:00Z", "sessionId": "s1"}
    if meta:
        r["isMeta"] = True
    return r


def _tool_result() -> dict:
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "t1", "content": "some tool output"}]}}


def _write_session(root: Path, name: str, records: list[dict]) -> None:
    d = root / "projects" / PROJECT
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def _scan(tmp_path: Path) -> dict:
    return scan(tmp_path / "projects", f"{PROJECT}*", tmp_path / "out")


def _event_classes(out: Path) -> set[str]:
    events = (out / "correction-events.jsonl").read_text().splitlines()
    return {json.loads(line)["class"] for line in events}


def test_operator_text_extraction_rules(tmp_path):
    assert operator_texts(_user("fix the imports")) == "fix the imports"
    assert operator_texts(_tool_result()) == ""  # tool output is not speech
    assert operator_texts(_user("generated marker text", meta=True)) == ""
    assert operator_texts(_user("<command-name>/compact</command-name>")) == ""
    # system-voice records that masquerade as user turns (seen in the pilot)
    assert operator_texts(_user(
        "This session is being continued from a previous conversation that ran out of context.")) == ""
    assert operator_texts(_user("<task-notification> <task-id>x</task-id>")) == ""
    assert operator_texts(_user("fsync — watch tick: post your utilization report")) == ""
    assert operator_texts(_user("RETRO-1 (Brian's ask; one turn): read the prompt file")) == ""
    blocky = {"type": "user", "message": {"role": "user", "content": [
        {"type": "text", "text": "real operator words"}]}}
    assert operator_texts(blocky) == "real operator words"


def test_each_correction_class_fires_on_true_positives(tmp_path):
    cases = {
        "wrong": "That's wrong — the port is 8080.",
        "negation": "No, keep the old vault path.",
        "i_said": "As I said yesterday, the ledger lives in trial-ledger.py.",
        "env_fact_correction": "Use bun, not npm for this.",
        "actually": "Actually, the server runs on the work machine.",
    }
    for cls, text in cases.items():
        d = tmp_path / "projects" / f"{PROJECT}-{cls}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "s.jsonl").write_text(
            json.dumps(_user("a neutral status report sentence for balance")) + "\n"
            + json.dumps(_user(text)) + "\n", encoding="utf-8")
    stats = _scan(tmp_path)
    found = _event_classes(tmp_path / "out")
    for cls in cases:
        assert cls in found, f"{cls} did not fire"
    assert stats["user_text_turns"] == len(cases) * 2


def test_neutral_turns_do_not_fire(tmp_path):
    _write_session(tmp_path, "s.jsonl", [
        _user("Please summarize the experiment results and commit them."),
        _user("The suite passed 12 tests in 3 seconds."),
    ])
    stats = _scan(tmp_path)
    assert _event_classes(tmp_path / "out") == set()
    assert stats["fact_classes"] == {}


def test_repeated_instruction_detected_across_turns(tmp_path):
    instruction = "always run the focused contract suite before committing any portfolio code"
    _write_session(tmp_path, "a.jsonl", [_user(instruction)])
    d2 = tmp_path / "projects" / f"{PROJECT}-two"
    d2.mkdir(parents=True, exist_ok=True)
    (d2 / "b.jsonl").write_text(json.dumps(_user(instruction + " please")) + "\n", encoding="utf-8")
    stats = _scan(tmp_path)
    assert stats["repeated_instruction_groups"] >= 1
    events = (tmp_path / "out" / "correction-events.jsonl").read_text().splitlines()
    repeat = next(json.loads(e) for e in events if json.loads(e)["class"] == "repeated_instruction")
    assert repeat["occurrences"] == 2
    assert len(repeat["spots"]) == 2  # both locations receipted, excerpts once


def test_fact_classes_fire_and_stats_carry_no_excerpts(tmp_path):
    _write_session(tmp_path, "a.jsonl", [
        _user("Always run the linter before you push to the shared repo."),
        _user("The store lives at /home/bmosher/.pi/agent/lcm and LCM_DB_DIR=/tmp/x overrides it."),
    ])
    stats = _scan(tmp_path)
    assert stats["fact_classes"].get("convention", 0) >= 1
    assert stats["fact_classes"].get("env_fact", 0) >= 1
    blob = json.dumps(stats)
    assert "linter" not in blob and "/home/bmosher" not in blob  # stats are excerpt-free


def test_normalize_for_repeat_is_punctuation_agnostic():
    assert (normalize_for_repeat("Always run it, please!") ==
            normalize_for_repeat("always run it please"))


def test_pattern_tables_are_named_per_dispatch():
    assert {"wrong", "negation", "i_said", "env_fact_correction", "actually"} <= {
        name for name, _ in CORRECTION_PATTERNS}
    assert {"convention", "env_fact"} <= {name for name, _ in FACT_PATTERNS}
