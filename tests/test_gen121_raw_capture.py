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
    _, journal, _ = _drive(monkeypatch, tmp_path, GOOD)
    rec = _lines(journal)[0]
    assert rec["captured_before_any_decode"] is True
    assert base64.b64decode(rec["response_bytes_b64"]) == GOOD, (
        "the journal must reproduce the exact bytes received")


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

    Replaying already-exposed cases would re-use a schedule that is only valid
    once. Whether a FRESH experiment happens is a control-plane decision.
    """
    mod = _runner()
    (tmp_path / mod.JOURNAL).write_text(json.dumps({"case_id": "c1"}) + "\n")
    with pytest.raises(SystemExit) as excinfo:
        mod.refuse_to_resume_an_exposed_run(tmp_path)
    message = str(excinfo.value)
    assert "may not be replayed" in message
    assert "1 captured response" in message

    clean = tmp_path / "fresh"
    clean.mkdir()
    mod.refuse_to_resume_an_exposed_run(clean)  # no journal, no objection


def test_the_journal_is_append_only_across_calls(monkeypatch, tmp_path):
    results, journal, _ = _drive(monkeypatch, tmp_path, GOOD, cases=3)
    got = _lines(journal)
    assert len(got) == 3, "each call appends; none overwrites"
    assert len({r["case_id"] for r in got}) == 3


def test_the_capture_is_fsynced_not_merely_flushed():
    """`flush` moves bytes to the OS, not to the platter. The fsync is the point."""
    src = (ROOT / "src/memory_bakeoff/evidence.py").read_text()
    block = src[src.index("def journal_append("):src.index("def manifest_existing(")]
    assert "os.fsync(handle.fileno())" in block
    assert 'open("a"' in block, "the journal must be opened for append, never write"
