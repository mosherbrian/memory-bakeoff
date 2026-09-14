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
    mask_quotes,
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
    assert operator_texts(_user(
        "Condense the tool payload below to under 12800 characters. It is going into an observation record.")) == ""
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
    # 5 unique correction turns + 1 deduped neutral sentence (identical
    # neutral fixtures across dirs = continuation-copy shape)
    assert stats["user_text_turns"] == len(cases) + 1


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


def test_by_project_breakdown_counts_files_and_turns_per_project(tmp_path):
    d1 = tmp_path / "projects" / f"{PROJECT}"
    d1.mkdir(parents=True, exist_ok=True)
    (d1 / "a.jsonl").write_text(json.dumps(_user("one neutral turn")) + "\n", encoding="utf-8")
    d2 = tmp_path / "projects" / f"{PROJECT}-drafter"
    d2.mkdir(parents=True, exist_ok=True)
    (d2 / "b.jsonl").write_text(
        json.dumps(_user("turn one")) + "\n" + json.dumps(_user("turn two")) + "\n",
        encoding="utf-8")
    stats = _scan(tmp_path)
    assert stats["by_project"] == {
        PROJECT: {"files": 1, "user_turns": 1},
        f"{PROJECT}-drafter": {"files": 1, "user_turns": 2},
    }
    assert "one neutral turn" not in json.dumps(stats)  # counts only


def test_pattern_tables_are_named_per_dispatch():
    assert {"wrong", "negation", "i_said", "env_fact_correction", "actually"} <= {
        name for name, _ in CORRECTION_PATTERNS}
    assert {"convention", "env_fact"} <= {name for name, _ in FACT_PATTERNS}


def test_quoted_model_speech_does_not_fire_corrections(tmp_path):
    """The pilot's main residual false positive: the operator QUOTING a
    model ("it said, \\"...use bun, not npm...\\"") is not a correction."""
    _write_session(tmp_path, "a.jsonl", [
        _user('I\'m chatting with a design chat and it said, "Exactly. '
              'Use bun, not npm, always." That is the whole update.'),
        _user("Use bun, not npm for real this time."),  # unquoted: fires
    ])
    stats = _scan(tmp_path)
    events = [json.loads(e) for e in
              (tmp_path / "out" / "correction-events.jsonl").read_text().splitlines()]
    env_facts = [e for e in events if e["class"] == "env_fact_correction"]
    assert len(env_facts) == 1  # only the unquoted turn
    assert "for real this time" in env_facts[0]["excerpt"]


def test_mask_quotes_keeps_unquoted_text_intact():
    # the quoted span is replaced by whitespace; patterns are
    # whitespace-insensitive so matching semantics are unchanged
    assert mask_quotes('use bun, not npm "and the rest says things"').strip() == "use bun, not npm"


def test_closed_sessions_rule_and_record_ids(tmp_path):
    import os
    import time

    projects = tmp_path / "projects"
    closed_dir = projects / PROJECT
    closed_dir.mkdir(parents=True)
    closed = closed_dir / "closed.jsonl"
    closed.write_text(json.dumps(_user("a quiet status note")) + "\n", encoding="utf-8")
    fresh_dir = projects / f"{PROJECT}-live"
    fresh_dir.mkdir(parents=True, exist_ok=True)
    fresh = fresh_dir / "live.jsonl"
    fresh.write_text(json.dumps(_user("a quiet status note")) + "\n", encoding="utf-8")
    # make 'closed' look 2 hours old; 'fresh' stays now
    old = time.time() - 2 * 3600
    os.utime(closed, (old, old))

    stats = scan(projects, f"{PROJECT}*", tmp_path / "out",
                 exclude_mtime_within_minutes=60)
    assert stats["files_scanned"] == 1  # only the closed session
    assert stats["files_excluded_open"] == 1  # the live file, excluded
    assert stats["excluded_open_names"] and "live.jsonl" in stats["excluded_open_names"][0]

    # records carry stable ids
    events = (tmp_path / "out" / "correction-events.jsonl").read_text().splitlines()
    for line in events:
        rid = json.loads(line)["record_id"]
        assert rid.startswith("tm-") and len(rid) == 19


def test_pasted_output_flagged_but_not_dropped(tmp_path):
    """A genuine correction sentence followed by a big terminal paste is
    LABELED pasted_output=True — labeled, never dropped (the correction
    sentence must survive for consumers)."""
    from scripts.experiment_20260912_transcript_mining.mine import pasted_output_ratio

    paste = ("That's wrong — it doesn't seem to be running.\n"
             "bmosher@cds-ai-a5410:~$ systemctl --user is-active llama-swap\n"
             "active\n"
             "bmosher@cds-ai-a5410:~$ journalctl --user -u llama-swap -n 50\n"
             "Jul 28 12:21:01 cds-ai-a5410 llama-swap[9757]: started\n"
             "Jul 28 12:21:02 cds-ai-a5410 llama-swap[9757]: ready\n")
    assert pasted_output_ratio(paste) >= 0.5
    assert pasted_output_ratio("No, use the raw tool instead.") == 0.0  # short + no indicators

    _write_session(tmp_path, "a.jsonl", [_user(paste)])
    stats = scan(tmp_path / "projects", f"{PROJECT}*", tmp_path / "out")
    events = (tmp_path / "out" / "correction-events.jsonl").read_text().splitlines()
    flagged = [json.loads(e) for e in events if json.loads(e).get("pasted_output")]
    assert flagged and all(e["pasted_output"] for e in flagged)


def test_personal_context_turns_are_excluded_and_only_counted(tmp_path):
    _write_session(tmp_path, "a.jsonl", [
        _user("Check Redfin for new home listings in the 97365 ZIP area."),
        _user("Always run the linter before pushing."),  # genuine convention
        _user("The store lives at /home/bmosher/.pi/agent/lcm."),  # genuine env fact
    ])
    stats = _scan(tmp_path)
    assert stats["personal_turns_excluded"] == 1
    assert stats["fact_classes"].get("convention") == 1
    assert stats["fact_classes"].get("env_fact") == 1
    blob = (tmp_path / "out" / "durable-facts.jsonl").read_text()
    assert "Redfin" not in blob and "97365" not in blob  # personal excerpt never persisted
    events = (tmp_path / "out" / "correction-events.jsonl").read_text()
    assert "Redfin" not in events


def test_digest_dedupes_groups_and_ranks_by_strength(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.experiment_20260912_transcript_mining.digest import main

    facts = tmp_path / "durable-facts.jsonl"
    rows = [
        {"record_id": "tm-1", "class": "env_fact", "excerpt": "The store lives at /srv/mem/db.",
         "file": "a.jsonl", "line": 1, "session": "s1", "timestamp": "t"},
        {"record_id": "tm-2", "class": "env_fact", "excerpt": "the store lives at /srv/mem/db",
         "file": "b.jsonl", "line": 2, "session": "s2", "timestamp": "t"},
        {"record_id": "tm-3", "class": "convention", "excerpt": "Always run the linter first.",
         "file": "a.jsonl", "line": 3, "session": "s2", "timestamp": "t"},
    ]
    facts.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    out = tmp_path / "digest.md"
    rc = main(["--facts", str(facts), "--out", str(out)])
    assert rc == 0
    digest = out.read_text(encoding="utf-8")
    assert "candidates: 3 | unique (normalized): 2" in digest  # dedupe by normalized text
    assert digest.index("env_fact") < digest.index("convention")  # 2 sessions rank above 1
    assert "a.jsonl:1" in digest and "b.jsonl:2" in digest  # source pointers retained


def test_digest_handles_empty_input(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.experiment_20260912_transcript_mining.digest import main

    facts = tmp_path / "durable-facts.jsonl"
    facts.write_text("", encoding="utf-8")
    out = tmp_path / "digest.md"
    assert main(["--facts", str(facts), "--out", str(out)]) == 0
    assert "candidates: 0" in out.read_text(encoding="utf-8")


def test_digest_tolerates_repeated_instruction_shape(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.experiment_20260912_transcript_mining.digest import main

    facts = tmp_path / "correction-events.jsonl"
    rows = [
        {"record_id": "tm-9", "class": "repeated_instruction", "occurrences": 2,
         "excerpt": "always run the focused contract suite before committing",
         "spots": [{"file": "a.jsonl", "line": 5, "session": "s1"},
                   {"file": "b.jsonl", "line": 9, "session": "s2"}]},
        {"record_id": "tm-10", "class": "negation", "excerpt": "No, keep the old vault path.",
         "file": "c.jsonl", "line": 3, "session": "s3", "timestamp": "t"},
    ]
    facts.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    out = tmp_path / "corrections-digest.md"
    assert main(["--facts", str(facts), "--out", str(out)]) == 0
    digest = out.read_text(encoding="utf-8")
    assert "candidates: 2 | unique (normalized): 2" in digest
    assert "seen 2x in 2 session(s)" in digest  # spots expanded as occurrences
    assert "a.jsonl:5" in digest  # source pointers from spots retained


def test_digest_reclasses_scheduled_templates(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.experiment_20260912_transcript_mining.digest import main

    facts = tmp_path / "correction-events.jsonl"
    rows = []
    for day in range(1, 9):  # 8 consecutive days, same time-of-day
        rows.append({"record_id": f"tm-{day}", "class": "env_fact_correction",
                     "excerpt": "Check whether the upstream patch has been merged.",
                     "file": f"d{day}.jsonl", "line": 3,
                     "session": f"s{day}",
                     "timestamp": f"2026-09-{day:02d}T17:00:00Z"})
    rows.append({"record_id": "tm-x", "class": "negation",
                 "excerpt": "No, keep the old vault path.",
                 "file": "d9.jsonl", "line": 1, "session": "s9",
                 "timestamp": "2026-09-13T10:00:00Z"})
    facts.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    out = tmp_path / "corrections-digest.md"
    assert main(["--facts", str(facts), "--out", str(out)]) == 0
    digest = out.read_text(encoding="utf-8")
    assert "SCHEDULED TASK (template, not per-event corrections)" in digest
