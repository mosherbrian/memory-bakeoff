"""Gen121: exact response bytes reach disk before anything interprets them.

Sol's ruling: "once an HTTP response begins existing as a scientific outcome, its
exact bytes must be durably captured before decoding, parsing, grading, retry
classification, or any later call can erase it."

Three defects sat behind that sentence, and the runner's own docstring denied all
three. `r.read().decode()` was inside the transport `try`, so an HTTP 200 whose
body was not valid UTF-8 raised inside the retry handler, lost its bytes, and got
asked again - retrying a scientific outcome. Nothing was written to disk until all
sixty calls returned, so a crash at call 59 destroyed fifty-nine answers that had
already been given. And `reader_raw.jsonl` was re-serialised Python objects, not
raw bytes at all.

These drive the real `call_once` against a fake endpoint. Helper return values
would have passed against the defective code.
"""
from __future__ import annotations

import base64
import importlib.util
import io
import json
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_reader_v6.py"

GOOD = json.dumps({"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}],
                   "model": "test-model"}).encode()
NOT_UTF8 = b'{"choices":[{"message":{"content":"\xff\xfe caf\xe9"}}]}'
BAD_JSON = b"this is a 200 but it is not json"


def _runner():
    spec = importlib.util.spec_from_file_location("runner_g121", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _drive(monkeypatch, tmp_path, body: bytes, fail_times: int = 0, cases: int = 1):
    """Run N cases against a fake endpoint, returning (results, journal, call count)."""
    mod = _runner()
    calls = {"n": 0}

    class _Resp(io.BytesIO):
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=None):
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise OSError("connection reset")
        return _Resp(body)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    schedule = json.loads((mod.CANONICAL / "reader_interference_v6_schedule.json").read_text())
    journal = tmp_path / mod.JOURNAL
    out = [mod.call_once(c, journal) for c in schedule["cases"][:cases]]
    return out, journal, calls


def _lines(journal: Path) -> list[dict]:
    return [json.loads(l) for l in journal.read_text().splitlines() if l.strip()]


# ------------------------------------------- F1: bytes on disk before parsing
def test_exact_bytes_are_persisted_before_any_decode(monkeypatch, tmp_path):
    """The record carries bytes and nothing derived from reading them.

    It used to assert a literal `captured_before_any_decode: True` written by the
    same function it vouched for - the authored-attestation shape this file's own
    contract disavows ("to be read from server evidence, never authored"). Raised
    by glm-5.3 at Gen121. The property is now structural: a journal record holds
    raw bytes and none of the products of decoding them.
    """
    _, journal, _ = _drive(monkeypatch, tmp_path, GOOD)
    rec = _lines(journal)[0]
    assert base64.b64decode(rec["response_bytes_b64"]) == GOOD, (
        "the journal must reproduce the exact bytes received")
    for derived in ("text", "served_model", "finish_reason", "raw_response"):
        assert derived not in rec, (
            f"{derived!r} is a product of decoding; its presence would mean the "
            "journal was written after a parse, not before one")


def test_the_journal_reproduces_non_utf8_bytes_exactly(monkeypatch, tmp_path):
    """The bytes that cannot be decoded are exactly the ones worth keeping."""
    _, journal, _ = _drive(monkeypatch, tmp_path, NOT_UTF8)
    rec = _lines(journal)[0]
    assert base64.b64decode(rec["response_bytes_b64"]) == NOT_UTF8
    assert rec["response_len"] == len(NOT_UTF8)


def test_the_parsed_view_is_not_called_raw(monkeypatch, tmp_path):
    src = RUNNER.read_text()
    assert "reader_records.jsonl" in src
    assert '"raw_path": JOURNAL' in src, "the raw artifact must be the journal"
    assert 'write_raw(out, "reader_raw.jsonl"' not in src, (
        "re-serialised objects may not be called raw bytes")


# --------------------------------------- F2: after bytes arrive, never retry
def test_an_undecodable_200_is_terminal_and_not_retried(monkeypatch, tmp_path):
    results, journal, calls = _drive(monkeypatch, tmp_path, NOT_UTF8)
    assert results[0]["terminal_disposition"] == "TERMINAL_UNDECODABLE_RESPONSE"
    assert calls["n"] == 1, f"an undecodable answer was retried {calls['n']} times"
    assert results[0]["decode_error"]
    assert len(_lines(journal)) == 1, "its bytes must still be journalled"


def test_a_valid_utf8_but_malformed_json_200_is_terminal_and_not_retried(monkeypatch, tmp_path):
    results, journal, calls = _drive(monkeypatch, tmp_path, BAD_JSON)
    assert results[0]["terminal_disposition"] == "TERMINAL_MALFORMED_RESPONSE"
    assert calls["n"] == 1
    assert base64.b64decode(_lines(journal)[0]["response_bytes_b64"]) == BAD_JSON


def test_a_true_transport_failure_still_retries(monkeypatch, tmp_path):
    """The negative control: the frozen retry policy must survive the repair."""
    results, journal, calls = _drive(monkeypatch, tmp_path, GOOD, fail_times=2)
    assert results[0]["terminal_disposition"] == "COMPLETED"
    assert calls["n"] == 3
    assert len(_lines(journal)) == 1, (
        "only the answered attempt produces bytes; failed transport has none")


def test_transport_exhaustion_journals_nothing_and_is_terminal(monkeypatch, tmp_path):
    results, journal, calls = _drive(monkeypatch, tmp_path, GOOD, fail_times=99)
    assert results[0]["terminal_disposition"] == "TERMINAL_TRANSPORT_FAILURE"
    assert not journal.exists() or _lines(journal) == [], (
        "no bytes were ever received, so there is nothing to capture")


# ------------------------------- F3: interruption leaves N durable captures
def test_an_interruption_leaves_the_earlier_captures_on_disk(monkeypatch, tmp_path):
    """Simulate the process dying immediately after response N."""
    mod = _runner()
    calls = {"n": 0}

    class _Resp(io.BytesIO):
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=None):
        calls["n"] += 1
        if calls["n"] == 4:
            raise KeyboardInterrupt("process interrupted at call 4")
        return _Resp(GOOD)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    schedule = json.loads((mod.CANONICAL / "reader_interference_v6_schedule.json").read_text())
    journal = tmp_path / mod.JOURNAL
    with pytest.raises(KeyboardInterrupt):
        for c in schedule["cases"][:6]:
            mod.call_once(c, journal)

    got = _lines(journal)
    assert len(got) == 3, f"expected 3 durable captures before the interruption, got {len(got)}"
    assert calls["n"] == 4, "no call may be made after the interruption"
    assert [r["case_id"] for r in got] == [c["case_id"] for c in schedule["cases"][:3]]


def test_an_interrupted_exposed_run_refuses_to_resume(tmp_path):
    """An interrupted exposed run is finished, not paused.

    The guard is given the GENERATION directory, not the fresh attempt directory.
    The first version was handed the output of `EV.next_attempt` - chosen because
    it does not exist - so its journal never could, and the gate was dead at the
    call site while this witness passed by calling the function directly with a
    hand-built journal. Both reviewers found it at Gen121. The witness now builds
    the real shape: a committed, interrupted attempt sitting beside a fresh one.
    """
    mod = _runner()
    gen = tmp_path / "gen999"
    (gen / "attempt1").mkdir(parents=True)
    (gen / "attempt1" / mod.JOURNAL).write_text(json.dumps({"case_id": "c1"}) + "\n")

    with pytest.raises(SystemExit) as excinfo:
        mod.refuse_to_resume_an_exposed_run(gen)
    message = str(excinfo.value)
    assert "may not be replayed" in message
    assert "1 captured response" in message

    # A run that REACHED a marker is finished, not interrupted, and must not block
    # a later authorised generation forever.
    (gen / "attempt1" / "NON_EVIDENCE.json").write_text('{"marker": "NON_EVIDENCE"}')
    mod.refuse_to_resume_an_exposed_run(gen)

    mod.refuse_to_resume_an_exposed_run(tmp_path / "gen998")  # absent, no objection


def test_the_guard_is_wired_to_the_generation_not_the_fresh_attempt():
    """The wiring, not the function. The function was always fine."""
    src = RUNNER.read_text()
    assert 'refuse_to_resume_an_exposed_run(ROOT / "results" / f"gen{args.generation}")' in src, (
        "the guard must be handed the generation directory")
    # Compare against the attempt directory that CAPTURES, not the first textual
    # match - there is another EV.next_attempt in the preflight-failure branch,
    # which never exposes anything. My first version of this assertion took
    # src.index() and got that one, which is the same "assert on what you found
    # rather than what matters" error the guard itself was fixed for.
    guard = src.index("refuse_to_resume_an_exposed_run(ROOT")
    capture = src.index("journal = out / JOURNAL")
    assert guard < capture, (
        "prior exposure must be checked before the run directory is used to capture")


def test_the_journal_is_append_only_across_calls(monkeypatch, tmp_path):
    results, journal, _ = _drive(monkeypatch, tmp_path, GOOD, cases=3)
    got = _lines(journal)
    assert len(got) == 3, "each call appends; none overwrites"
    assert len({r["case_id"] for r in got}) == 3


def test_the_capture_is_fsynced_not_merely_flushed(monkeypatch, tmp_path):
    """`flush` moves bytes to the OS, not to the platter. The fsync is the point.

    This was a source grep for `os.fsync(...)`, which is the decayed-prose shape
    this apparatus keeps diagnosing - it would pass against a file whose fsync
    call had been commented out one line below. It now OBSERVES the syscall.
    Raised by glm-5.3 at Gen121.
    """
    import os as _os
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from memory_bakeoff import evidence as EV

    synced = []
    real = _os.fsync
    monkeypatch.setattr(_os, "fsync", lambda fd: (synced.append(fd), real(fd))[1])

    journal = tmp_path / "j.jsonl"
    EV.journal_append(journal, {"case_id": "c1"})
    assert len(synced) >= 1, "the appended bytes were never fsynced"
    first_count = len(synced)
    EV.journal_append(journal, {"case_id": "c2"})
    assert len(synced) > first_count, "every append must be fsynced, not just the first"
    assert len([l for l in journal.read_text().splitlines() if l.strip()]) == 2


# ------------------- a partial or failed run must still reach its marker
def test_the_marker_survives_a_run_mixing_completed_and_terminal_responses():
    """`sorted()` over {str, None} raises TypeError.

    Any run with one terminal disposition beside one completed response crashed
    here - AFTER the evidence was sealed and graded, but BEFORE the marker was
    written - leaving the attempt permanently marker-less, with backfill
    forbidden. So the graceful NON_EVIDENCE path built across four rounds could
    never execute for exactly the partial-failure runs it was built for. Both
    reviewers reproduced it independently at Gen121.
    """
    responses = [{"served_model": "qwen", "terminal_disposition": "COMPLETED"},
                 {"served_model": None, "terminal_disposition": "TERMINAL_MALFORMED_RESPONSE"},
                 {"served_model": None, "terminal_disposition": "TERMINAL_TRANSPORT_FAILURE"}]
    with pytest.raises(TypeError):
        sorted({r["served_model"] for r in responses})          # the old expression
    served = sorted(m for m in {r["served_model"] for r in responses} if m is not None)
    assert served == ["qwen"]
    assert sum(1 for r in responses if r["served_model"] is None) == 2

    src = RUNNER.read_text()
    assert 'sorted({r["served_model"] for r in responses})' not in src, "the crash is back"
    assert "responses_without_a_served_model" in src


def test_a_run_where_every_case_failed_transport_still_seals(tmp_path):
    """No bytes ever arrived, so the journal does not exist.

    `manifest_existing` raised FileNotFoundError, killing the run before its
    marker - the same family as the crash above: failed runs never reaching the
    disposition machinery built to record them. Found by glm-5.3-flash.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from memory_bakeoff import evidence as EV
    mod = _runner()

    with pytest.raises(FileNotFoundError):
        EV.manifest_existing(tmp_path, mod.JOURNAL)          # the old path

    (tmp_path / mod.JOURNAL).write_text("")                  # what the runner now does
    EV.manifest_existing(tmp_path, mod.JOURNAL)
    assert mod.JOURNAL in json.loads((tmp_path / EV.MANIFEST).read_text())["artifacts"]

    src = RUNNER.read_text()
    assert "if not journal.exists():" in src and 'journal.write_text("")' in src


def test_the_graded_view_is_reconciled_against_the_captured_bytes():
    """Nothing compared what was GRADED against what was CAPTURED.

    Grading consumes in-memory objects re-serialised into reader_records.jsonl.
    The manifest binds both files and the seal binds the journal, but a desync
    between arrival and scoring - an ordinary bug, not tamper - would pass every
    gate including closure and the three-way seal. Raised by glm-5.3-flash.
    """
    src = RUNNER.read_text()
    assert "records_match_journal" in src
    assert "linkage_ok=linkage_ok and records_match_journal" in src, (
        "the reconciliation must gate the marker, not merely be reported"
    )
    assert "cases_whose_graded_bytes_differ_from_capture" in src
    assert "cases_captured_but_never_graded" in src

    # The comparison itself, exercised.
    captured = {"c1": "aaa", "c2": "bbb"}
    responses = [{"case_id": "c1", "response_sha256": "aaa"},
                 {"case_id": "c2", "response_sha256": "ZZZ"}]
    mismatched = sorted(r["case_id"] for r in responses
                        if r.get("response_sha256") is not None
                        and captured.get(r["case_id"]) != r["response_sha256"])
    assert mismatched == ["c2"], "a desync must be visible by case"
