"""P6-r6 repair-2 regression: SUCCESS JSON vs quiet suppression, raw
persistence pre-validation, ambiguous EFFECT never zero, strict id
correlation, partial ownership on post-create binding failure. Injected
effects + private tmp only; the one real-binary probe is parser-only
(zero creations; registry pinned)."""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import prepare_live as pl
from prepare_live import PrepFault

LANE = "/home/bmosher/.config/agent-deck/acp-go"
VLane = "/home/bmosher/.config/agent-deck/acp-go-deepseek"


class FakeProc:
    def __init__(self, rc=0, stdout="", stderr=""):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr


def clioutput_runner(cmd, succeed=True, payload=None, timeout=False,
                     transport_error=False):
    """Inspected CLIOutput semantics (cli_utils.go): Success returns early
    on quietMode (no output at all, even with -json); Error renders JSON
    whenever -json is set. NOT a runner that always returns the desired
    shape: quiet+success yields empty rc0; errors yield JSON."""
    def run(cmd, **kw):
        run.cmd = cmd
        if timeout:
            raise subprocess.TimeoutExpired(cmd, 180)
        if transport_error:
            raise OSError("spawn failed")
        if succeed:
            if "-q" in cmd or "--quiet" in cmd:
                return FakeProc(0, "", "")
            return FakeProc(0, json.dumps(payload or {"id": "w1"}))
        if "-json" in cmd:
            return FakeProc(1, json.dumps({"success": False,
                                           "error": "boom",
                                           "code": "E_X"}))
        return FakeProc(1, "", "Error: boom")
    return run


def test_quiet_success_is_ambiguous_effect_with_raw(tmp_path):
    # Old-failure reproduction at unit level: -json -q + success.
    run = clioutput_runner(None, succeed=True)
    raw = str(tmp_path / "raw.json")
    with pytest.raises(PrepFault) as e:
        pl.launch_idle("/tmp", "p6-fixture-worker", LANE, "campaign4",
                       "25m", "/tmp/x",
                       runner=lambda cmd, **kw: run(
                           ["agent-deck", "launch", "/tmp", "-t", "n",
                            "-cmd", LANE, "--idle-timeout=25m",
                            "-json", "-q"], **kw),
                       raw_path=raw)
    assert e.value.code == "E_LAUNCH_AMBIGUOUS"
    rec = json.load(open(raw))
    assert rec["rc"] == 0 and rec["stdout"] == ""  # suppressed, retained


def test_corrected_argv_success_returns_exact_id(tmp_path):
    run = clioutput_runner(None, succeed=True, payload={"id": "abc-1"})
    raw = str(tmp_path / "raw.json")
    out = pl.launch_idle("/tmp", "p6-fixture-worker", LANE, "campaign4",
                         "25m", "/tmp/x", runner=run, raw_path=raw)
    assert out["id"] == "abc-1"
    assert "-q" not in run.cmd and "--idle-timeout=25m" in run.cmd
    assert json.load(open(raw))["rc"] == 0


def test_empty_malformed_timeout_transport_are_ambiguous(tmp_path):
    import subprocess as _sp
    cases = [
        (FakeProc(0, "", ""), "empty rc0"),
        (FakeProc(0, "{not json", ""), "malformed"),
        (_sp.TimeoutExpired("x", 1), "timeout"),
        (OSError("nope"), "transport"),
    ]
    for effect, label in cases:
        def run(cmd, **kw):
            if isinstance(effect, BaseException):
                raise effect
            return effect
        raw = str(tmp_path / ("raw-%s.json" % label.split()[0]))
        with pytest.raises(PrepFault) as e:
            pl.launch_idle("/tmp", "p6-fixture-worker", LANE, "campaign4",
                           "25m", "/tmp/x", runner=run, raw_path=raw)
        assert e.value.code == "E_LAUNCH_AMBIGUOUS", label
        assert os.path.exists(raw), label  # evidence retained


def test_second_side_failure_retains_partial_no_retry(tmp_path, monkeypatch):
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        if cmd[cmd.index("-t") + 1] == "p6-fixture-worker":
            return FakeProc(0, json.dumps({"id": "w1"}))
        return FakeProc(0, "", "")  # quiet-suppressed-style empty success
    monkeypatch.setattr(pl.subprocess, "run", run)
    seq = [[], [{"id": "w1", "title": "p6-fixture-worker",
                 "profile": "campaign4", "command": LANE}]]
    monkeypatch.setattr(pl, "list_sessions",
                        lambda profile, inject="": (seq.pop(0),
                                                    "live-agent-deck"))
    man_out = str(tmp_path / "manifest.json")
    assert pl.main(["--manifest-out", man_out,
                    "--workdir-base", str(tmp_path)]) == 3
    assert len(calls) == 2
    partial = json.load(open(man_out + ".partial"))
    assert partial["worker"]["session_id"] == "w1"
    assert partial["pending_role"] == "verifier"
    assert os.path.exists(partial["raw_records"]["verifier"])


def test_postcreate_binding_failure_retains_both_sides(tmp_path, monkeypatch):
    def run(cmd, **kw):
        name = cmd[cmd.index("-t") + 1]
        sid = "w1" if name == "p6-fixture-worker" else "v1"
        return FakeProc(0, json.dumps({"id": sid}))
    monkeypatch.setattr(pl.subprocess, "run", run)
    recs = [{"id": "w1", "title": "p6-fixture-worker", "profile":
             "campaign4", "command": LANE},
            {"id": "v1", "title": "p6-fixture-verifier", "profile":
             "campaign4", "command": VLane}]
    monkeypatch.setattr(pl, "list_sessions",
                        lambda profile, inject="": ([], "live-agent-deck")
                        if not hasattr(run, "n") else (recs, "live-agent-deck"))
    # first list call (pre-check) empty, second (post-launch) full:
    calls = {"n": 0}

    def fake_list(profile, inject=""):
        calls["n"] += 1
        return ([], "live-agent-deck") if calls["n"] == 1 else (
            recs, "live-agent-deck")
    monkeypatch.setattr(pl, "list_sessions", fake_list)

    def no_socket(path):
        raise PrepFault("E_NO_SOCKET", "gone: " + path)
    monkeypatch.setattr(pl, "check_socket_real", no_socket)
    man_out = str(tmp_path / "manifest.json")
    assert pl.main(["--manifest-out", man_out,
                    "--workdir-base", str(tmp_path)]) == 3
    partial = json.load(open(man_out + ".partial"))
    assert partial["worker"]["session_id"] == "w1"  # ownership retained
    assert partial["verifier"]["session_id"] == "v1"
    assert partial["pending_role"] == "bind-worker"
    assert partial["launch_error"]["code"] == "E_NO_SOCKET"


def test_error_json_probe_still_parser_only():
    before = json.loads(subprocess.run(
        ["agent-deck", "list", "--json"], capture_output=True, text=True,
        timeout=60, env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
        .stdout or "[]")
    r = subprocess.run(
        ["agent-deck", "launch", "/tmp/p6r6-probe-nodir", "-t", "probe-e",
         "-cmd", LANE, "--idle-timeout=25m", "-json"], capture_output=True,
        text=True, timeout=60,
        env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
    assert r.returncode != 0
    assert json.loads(r.stdout)["code"] == "NOT_FOUND"
    # SUCCESS JSON cannot be probed without creating a seat (documented
    # limit); it is covered above via inspected CLIOutput semantics.
    after = json.loads(subprocess.run(
        ["agent-deck", "list", "--json"], capture_output=True, text=True,
        timeout=60, env=dict(os.environ, AGENTDECK_PROFILE="campaign4"))
        .stdout or "[]")
    assert sorted(s["id"] for s in after) == sorted(s["id"] for s in before)
