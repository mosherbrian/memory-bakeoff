"""P6-r5 repair-2 residual tests: L2 evidence authenticity (launcher-verified
bindings; invented identifiers rejected even with unrelated valid streams;
idle runtime needs no end) and L4 timing honesty (onset->detection gated;
dispatch duration separate; unknown onset is UNMEASURABLE, never gates-hold).
Injected boundaries only; no live seats/services."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import harness as harness_mod
from host_adapter import OwnedFault

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
SESS_FIX = os.path.join(PKG, "fixtures", "launcher-sessions-sanitized.json")

SESS = "p6h-session-1"
SK = "p6h-main"
WSK = "p6h-w-stream"
VSK = "p6h-v-stream"


def mktree(streams=("p6h-w-stream", "p6h-v-stream"), with_ends=False):
    tmp = tempfile.mkdtemp(prefix="p6r2-")
    os.makedirs(os.path.join(tmp, "sock"))
    os.makedirs(os.path.join(tmp, "stream"))
    open(os.path.join(tmp, "sock", SESS + ".sock"), "w").write("")
    for s in streams:
        body = '{"t":"end","item":"iOld"}\n' if with_ends else ""
        open(os.path.join(tmp, "stream", s + ".jsonl"), "w").write(body)
    return tmp


def prep(tmp, extra=()):
    return subprocess.run(
        [sys.executable, os.path.join(SRC, "prepare_evidence.py"),
         "--producer-root", os.path.join(tmp, "stream"),
         "--session", SESS, "--stream-key", SK,
         "--worker-stream-key", WSK, "--verifier-stream-key", VSK,
         "--sock-dir", os.path.join(tmp, "sock"),
         "--session-list-file", SESS_FIX] + list(extra),
        capture_output=True, text=True, timeout=60)


# --- L2 ---------------------------------------------------------------------
def test_l2_idle_genuine_runtime_passes_without_end():
    tmp = mktree(with_ends=False)  # files bound, no end emitted yet
    r = prep(tmp)
    assert r.returncode == 0, r.stderr
    ev = json.loads(r.stdout)
    assert ev["launcher_source"].startswith("fixture-injected")
    assert ev["worker_socket"].endswith(SESS + ".sock")


def test_l2_invented_identifiers_rejected_despite_unrelated_streams():
    tmp = mktree(streams=("some-other-valid",))
    r = prep(tmp)
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] in ("E_UNKNOWN_SESSION",
                                             "E_UNBOUND"), r.stdout


def test_l2_unknown_session_rejected_on_empty_root():
    tmp = tempfile.mkdtemp(prefix="p6r2-empty-")
    os.makedirs(os.path.join(tmp, "stream"))
    os.makedirs(os.path.join(tmp, "sock"))
    r = subprocess.run(
        [sys.executable, os.path.join(SRC, "prepare_evidence.py"),
         "--producer-root", os.path.join(tmp, "stream"),
         "--session", "invented-session", "--stream-key", "invented-main",
         "--worker-stream-key", "invented-worker",
         "--verifier-stream-key", "invented-verifier",
         "--sock-dir", os.path.join(tmp, "sock"),
         "--session-list-file", SESS_FIX],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 3, r.stdout  # director probe case now fails closed
    assert json.loads(r.stdout)["error"] in ("E_UNKNOWN_SESSION",
                                             "E_NO_SOCKET", "E_UNBOUND")


def test_l2_missing_socket_fails_closed():
    tmp = mktree()
    os.remove(os.path.join(tmp, "sock", SESS + ".sock"))
    r = prep(tmp)
    assert r.returncode == 3
    assert json.loads(r.stdout)["error"] == "E_NO_SOCKET"


def test_l2_setup_propagates_launcher_binding():
    tmp = mktree()
    out = os.path.join(tmp, "m.json")
    plan = os.path.join(tmp, "plan.json")
    json.dump({"fixture_id": "p6-fixture-handoff-1", "package_id": "P6H",
               "worker_action": "p6h-w1", "verify_action": "p6h-v1",
               "seats": {"fixture_seats": ["p6-fixture-worker",
                                           "p6-fixture-verifier"]},
               "bounds": {"stream_dir": os.path.join(tmp, "stream")},
               "task_texts": {}, "routes": {}}, open(plan, "w"))
    r = prep(tmp, ["--out", os.path.join(tmp, "ev.json")])
    assert r.returncode == 0, r.stderr
    import shlex
    evcmd = ("python3 " + os.path.join(SRC, "prepare_evidence.py")
             + " --producer-root " + os.path.join(tmp, "stream")
             + " --session " + SESS + " --stream-key " + SK
             + " --worker-stream-key " + WSK + " --verifier-stream-key "
             + VSK + " --sock-dir " + os.path.join(tmp, "sock")
             + " --session-list-file " + SESS_FIX)
    m = harness_mod.setup_manifest(plan, out, None, None, None, None,
                                   evidence_cmd=shlex.split(evcmd))
    assert m["launcher_source"].startswith("fixture-injected")
    assert m["worker_socket"].endswith(SESS + ".sock")
    assert m["incarnation_mtime"] is not None


# --- L4 ---------------------------------------------------------------------
def _row(outcome, dispatch, onset, detected, committed):
    return {"action": "p6h-w1", "dispatch_at": dispatch,
            "detected_at": detected, "committed_at": committed,
            "outcome": outcome, "source_at": None,
            "source_time_known": False, "onset_at": onset,
            "onset_provenance": "fixture-producer-seat" if onset else None,
            "onset_uncertainty_s": 1 if onset else None,
            "onset_known": onset is not None,
            "detection_latency_s": None, "worker_duration_s": None,
            "recovery_latency_s": None, "note": "t"}


def _check(rows):
    tmp = tempfile.mkdtemp(prefix="p6r2-lat-")
    lp = os.path.join(tmp, "lat.jsonl")
    with open(lp, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return harness_mod.check_latency(lp)


def test_l4_unknown_onset_is_unmeasurable_never_gates_hold():
    v = _check([_row("terminal-rest", "2026-09-22T03:00:00Z", None,
                     "2026-09-22T03:00:01Z", "2026-09-22T03:00:02Z")])
    assert v["verdict"] == "unmeasurable-incomplete", v  # director case
    assert v["unmeasured"] == 1


def test_l4_long_work_then_prompt_detection_passes():
    v = _check([_row("terminal-rest", "2026-09-22T01:00:00Z",
                     "2026-09-22T03:00:00Z", "2026-09-22T03:00:02Z",
                     "2026-09-22T03:00:05Z")])
    assert v["verdict"] == "gates-hold", v  # 2h dispatch ago is irrelevant


def test_l4_late_detection_fails_its_bound():
    try:
        _check([_row("terminal-rest", "2026-09-22T03:00:00Z",
                     "2026-09-22T03:00:00Z", "2026-09-22T03:05:00Z",
                     "2026-09-22T03:05:05Z")])
        assert False, "expected E_GATE_DETECT"
    except OwnedFault as e:
        assert e.code == "E_GATE_DETECT", e


def test_l4_receipt_recovery_reported_and_bounded():
    try:
        _check([_row("terminal-rest", "2026-09-22T03:00:00Z",
                     "2026-09-22T03:00:00Z", "2026-09-22T03:00:01Z",
                     "2026-09-22T03:05:00Z")])
        assert False, "expected E_GATE_RECOVER"
    except OwnedFault as e:
        assert e.code == "E_GATE_RECOVER", e
