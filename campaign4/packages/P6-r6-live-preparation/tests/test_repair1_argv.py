"""P6-r6 repair-1 regression: parser-safe idle launch argv, exact returned
identity (no silent title-only fallback), partial-creation journal without
retry. Real-binary parser probe creates NO seats (all probes fail before
any creation; registry pinned at 4 seats throughout)."""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import prepare_live as pl
from prepare_live import PrepFault

LANE = "/home/bmosher/.config/agent-deck/acp-go"


class FakeProc:
    def __init__(self, rc=0, stdout="", stderr=""):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr


# --- exact argv ----------------------------------------------------------------
def test_launch_argv_parser_safe_single_equal_token_no_message():
    seen = []

    def runner(cmd, **kw):
        seen.append(cmd)
        return FakeProc(0, json.dumps({"id": "w1", "title": "p6w"}))
    out = pl.launch_idle("/tmp", "p6-fixture-worker", LANE, "campaign4",
                         "25m", "/tmp/p6r6-r1-wd", runner=runner)
    assert out["id"] == "w1"
    cmd = seen[0]
    assert "--idle-timeout=25m" in cmd  # one token, never split by passes
    assert "-idle-timeout" not in cmd and " 25m" not in " " + " ".join(cmd)
    assert "-m" not in cmd and "-message" not in cmd  # idle: no task
    assert "-json" in cmd and "-q" in cmd
    assert cmd[cmd.index("-cmd") + 1] == LANE  # lane adjacent to -cmd


def test_launch_without_returned_id_refuses_title_fallback():
    def runner(cmd, **kw):
        return FakeProc(0, json.dumps({"title": "p6-fixture-worker"}))
    with pytest.raises(PrepFault) as e:
        pl.launch_idle("/tmp", "p6-fixture-worker", LANE, "campaign4",
                       "25m", "/tmp/p6r6-r1-wd", runner=runner)
    assert e.value.code == "E_LAUNCH_NO_ID"


# --- real installed binary, parser-only, zero effects ---------------------------
def _seats():
    p = subprocess.run(["agent-deck", "list", "--json"], capture_output=True,
                       text=True, timeout=60,
                       env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
    return json.loads(p.stdout or "[]")


def test_installed_parser_old_argv_misbinds_new_argv_safe():
    before = _seats()
    assert len(before) == 4  # main seats only
    old = ["agent-deck", "launch", "/tmp", "-t", "probe-old",
           "-cmd", LANE, "-idle-timeout", "25m", "-json", "-q"]
    r = subprocess.run(old, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
    assert r.returncode != 0
    assert 'invalid --idle-timeout "-json"' in (r.stderr or r.stdout), \
        (r.stdout, r.stderr)  # original P6r6-prepare-1 failure, reproduced
    new = ["agent-deck", "launch", "/tmp/p6r6-probe-nodir", "-t", "probe-new",
           "-cmd", LANE, "--idle-timeout=25m", "-json", "-q"]
    r = subprocess.run(new, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
    assert r.returncode != 0
    body = json.loads(r.stdout)  # -json honored => flags bound correctly
    assert body["code"] == "NOT_FOUND" and "probe-nodir" in body["error"]
    after = _seats()
    assert len(after) == 4 and \
        sorted(s["id"] for s in after) == sorted(s["id"] for s in before)


# --- partial creation recorded, never retried ------------------------------------
def test_partial_journal_records_completed_side_without_retry(tmp_path,
                                                              monkeypatch):
    calls = []

    real_launch = pl.launch_idle

    def runner(cmd, **kw):
        calls.append(cmd)
        if "-t" in cmd and cmd[cmd.index("-t") + 1] == "p6-fixture-worker":
            return FakeProc(0, json.dumps({"id": "w1"}))
        return FakeProc(1, "", "boom-verifier")
    monkeypatch.setattr(pl.subprocess, "run", runner)
    # first call: pre-check empty; second call: worker present
    seq = [[], [{"id": "w1", "title": "p6-fixture-worker",
                 "profile": "campaign4", "command": LANE}]]
    monkeypatch.setattr(pl, "list_sessions",
                        lambda profile, inject="": (seq.pop(0),
                                                    "live-agent-deck"))
    monkeypatch.setattr(pl, "check_socket_real",
                        lambda p: {"mtime": 1.0, "ino": 7})
    man_out = str(tmp_path / "manifest.json")
    rc = pl.main(["--profile", "campaign4", "--manifest-out", man_out,
                  "--workdir-base", str(tmp_path)])
    assert rc == 3  # E_LAUNCH_PARTIAL path
    assert len(calls) == 2  # exactly one attempt per role: no retry
    partial = json.load(open(man_out + ".partial"))
    assert partial["pending_role"] == "verifier"
    assert partial["worker"]["session_id"] == "w1"
    assert "--idle-timeout=25m" in partial["worker"]["preparation_argv"]
    assert partial["launch_error"]["code"] == "E_LAUNCH"
