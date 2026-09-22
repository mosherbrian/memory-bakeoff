"""P6-r2 connected corrections: entrypoint, production transport/timer
branches under injected runners, real ACP schema, executable plan. No
live effects; runners are injected fakes with real signatures."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from host_adapter import (HostAdapter, HostWakeTransport, HostTimerService,
                          ACPOutcomeObserver, FakeWakeTransport, OwnedFault)
import harness as harness_mod

Q = "P6X"
DL_W = "2026-09-21T13:00:00Z"
WAKE = "/home/bmosher/.config/agent-deck/wake"


def mk(**kw):
    tmp = tempfile.mkdtemp(prefix="p6x-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d, HostAdapter(d, **kw)


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


class ScriptedRunner:
    """Injected runner with the real subprocess signature."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        return self.script.pop(0)

    class Out:
        def __init__(self, rc, out, err=""):
            self.returncode = rc
            self.stdout = out
            self.stderr = err


def R(rc, out, err=""):
    return ScriptedRunner.Out(rc, out, err)


# --- (1) entrypoint -------------------------------------------------------------
def test_entrypoint_live_gate_fail_closed():
    try:
        harness_mod.build_adapter("/tmp/x.db", live=True)
        assert False, "expected E_DISABLED"
    except OwnedFault as e:
        assert e.code == "E_DISABLED", e
    try:
        harness_mod.build_adapter("/tmp/x.db", live=True, plan_hash="abc",
                                  transport=FakeWakeTransport())
        assert False, "expected E_DISABLED for fake default in live mode"
    except OwnedFault as e:
        assert e.code == "E_DISABLED", e


def test_entrypoint_run_step_injected_production_branches():
    tmp = tempfile.mkdtemp(prefix="p6x-")
    import driver as _drv
    dd = _drv.Driver(__import__("os").path.join(tmp, "ledger.db"),
                     _drv.FakeClock(), FakeExternalWorld(
                         __import__("os").path.join(tmp, "world.json")))
    dd.tmp = tmp
    run = ScriptedRunner([R(0, "wake: p6-fixture-worker -> started\n")])
    ha = HostAdapter(dd, transport=HostWakeTransport(
        WAKE, ("p6-fixture-worker",), enabled=True,
        kv_get=dd.kv.get, kv_put=dd._kv_put, runner=run))
    d = dd
    ha.timers = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put)
    out = harness_mod.run_step(ha, {
        "question_id": Q, "action_id": "a-w1", "execution_id": "ex-1",
        "authorization_ref": "auth-1", "deadline_hint_utc": DL_W,
        "duration_s": 3600, "seat": "p6-fixture-worker", "text": "run?",
        "occurred_at": "2026-09-21T12:00:00Z"})
    assert out["reconcile"]["decision"] == "hold-for-receipt"  # sent, queued
    assert out["timer"][0] == "armed"
    assert ha.receipt(Q, "a1", "a-w1", "a-w1-dispatched", "ex-1") is not None
    d.close()


def test_timer_callback_executable_path():
    d, _ = mk()
    running(d, "a-cb")
    db = d.store.path
    d.close()
    # Far-future ledger deadline: callback executes, finds nothing due.
    out = harness_mod.timer_callback(db, "t-cb", Q, "a-cb")
    assert out["timer"] == "t-cb" and "decision" in out


# --- (2) production transport ------------------------------------------------------
def test_transport_matrix_real_kwargs_and_states():
    d, ha = mk()
    run = ScriptedRunner([
        R(0, "wake: s -> started\n"),
        R(3, "wake: s -> queued for worker\n"),
        R(1, "wake: s -> unknown\n"),
        R(0, "garbage-no-prefix\n"),
    ])
    t = HostWakeTransport(WAKE, ("s",), enabled=True,
                          kv_get=d.kv.get, kv_put=d._kv_put, runner=run)
    m1 = t.send("s", "a", action="a-w1", execution="ex-1")
    m2 = t.send("s", "b", action="a-w1", execution="ex-1")
    m3 = t.send("s", "c", action="a-w1", execution="ex-1")
    m4 = t.send("s", "d", action="a-w1", execution="ex-1")
    assert [t.state(m) for m in (m1, m2, m3, m4)] == \
        ["sent", "queued", "failed", "ambiguous"]
    cmd, kwargs = run.calls[0]  # real API kwargs + campaign4 env
    assert cmd == [WAKE, "s", "a"]
    assert kwargs["capture_output"] is True and kwargs["text"] is True
    assert isinstance(kwargs["timeout"], int)
    assert kwargs["env"]["AGENTDECK_PROFILE"] == "campaign4"
    # Stable identity across fresh instances sharing kv.
    t2 = HostWakeTransport(WAKE, ("s",), enabled=True,
                           kv_get=d.kv.get, kv_put=d._kv_put, runner=run)
    assert t2.state(m1) == "sent" and t2.state(m2) == "queued"
    # Queued is ack, never completion: adapter holds, never redispatches.
    ha.transport = t
    r = ha.reconcile_send(m2, "a-w1")
    assert r["decision"] == "hold-for-receipt"
    assert t.calls == [("s", "a", "wake"), ("s", "b", "wake"),
                       ("s", "c", "wake"), ("s", "d", "wake")]
    d.close()


def test_transport_timeout_maps_ambiguous():
    d, _ = mk()

    def boom(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, timeout=kwargs["timeout"])

    t = HostWakeTransport(WAKE, ("s",), enabled=True,
                          kv_get=d.kv.get, kv_put=d._kv_put, runner=boom)
    mid = t.send("s", "a", action="a-w1", execution="ex-1")
    assert t.state(mid) == "ambiguous"
    d.close()


# --- (3) production timers ------------------------------------------------------------
def test_timer_host_identity_and_restart():
    d, ha = mk()
    running(d)
    cb = ["python3", "src/harness.py", "timer-callback", "--timer", "t-h1"]
    run = ScriptedRunner([R(0, ""), R(0, ""), R(0, ""),
                          R(0, "ActiveState=inactive\nSubState=dead\n")])
    ts = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put, enabled=True,
                          allowlist=("t-h1",), runner=run, callback_argv=cb)
    assert ts.create_host("t-h1", DL_W, 60, cb)[0] == "armed-host"
    create_cmd = run.calls[0][0]
    assert "--unit=t-h1" in create_cmd and cb[-1] in create_cmd  # executable
    assert "true" not in create_cmd  # never a no-op callback
    ts.cancel_host("t-h1")  # same unit identity in stop commands
    stop_units = [c[0][3] for c in run.calls[1:3]]
    assert stop_units == ["t-h1.timer", "t-h1.timer"], stop_units
    props = ts.query_host("t-h1")  # same unit identity in query
    assert run.calls[3][0][3] == "t-h1.timer"
    assert props == {"ActiveState": "inactive", "SubState": "dead"}
    # Durable handled survives fresh instances (restart) on a live timer.
    ha.timers = ts
    d.clock.now = "2026-09-21T13:00:00Z"
    assert ts.create("t-h2", DL_W) == ("armed", False)
    assert ts.fire("t-h2", d.clock.now, DL_W) == ("fired", False)
    assert ts.fire("t-h2", d.clock.now, DL_W) == ("already-handled", True)
    ts2 = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put)
    assert ts2.fire("t-h2", d.clock.now, DL_W) == ("already-handled", True)
    assert ts2.fire("t-h2", d.clock.now, DL_W)[0] != "fired"
    d.close()


# --- (4) real ACP schema ------------------------------------------------------------------
SAMPLE = os.path.join(os.path.dirname(__file__), "..", "fixtures",
                      "acp-schema-sample.jsonl")


def test_acp_real_schema_completion_failed_partial():
    obs = ACPOutcomeObserver(SAMPLE)
    outcomes, cursor, note = obs.observe(0)
    assert note == "ok" and cursor > 0
    by_status = {}
    for o in outcomes:
        by_status.setdefault(o["status"], []).append(o)
    assert set(by_status) == {"completed", "failed"}  # partial rows skipped
    assert all(o["row_id"] and o["at"] for os_ in by_status.values()
               for o in os_)
    # Incremental: second scan from cursor yields nothing new.
    outcomes2, cursor2, _ = obs.observe(cursor)
    assert outcomes2 == [] and cursor2 == cursor


def test_acp_truncation_rotation_unavailable():
    import shutil
    tmp = tempfile.mkdtemp(prefix="p6o-")
    p = os.path.join(tmp, "h.jsonl")
    shutil.copy(SAMPLE, p)
    obs = ACPOutcomeObserver(p)
    _, c1, _ = obs.observe(0)
    assert c1 > 0
    with open(p, "w") as fh:  # truncation
        fh.write('{"id":"n","kind":"execute","status":"completed"}\n')
    outcomes, c2, note = obs.observe(c1)
    assert note == "truncated-reset" and len(outcomes) == 1
    os.remove(p)  # rotation
    outcomes, _, note = obs.observe(c2)
    assert outcomes == [] and note == "rotated-missing"


def test_acp_binding_stale_and_completion_drives_next():
    d, ha = mk()
    running(d)
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    ha.bind_session("sess-1", "ex-9", "a-w1")  # bound elsewhere
    ha.observer = ACPOutcomeObserver(SAMPLE)
    matched, stale, _ = ha.observe_bound(SAMPLE, "sess-1")
    assert matched == [] and len(stale) > 0  # binding mismatch: stale only
    import shutil
    sample2 = os.path.join(d.tmp, "sample2.jsonl")
    shutil.copy(SAMPLE, sample2)  # fresh cursor: the first scan consumed SAMPLE
    ha.bind_session(sample2, "ex-1", "a-w1")
    matched, stale, _ = ha.observe_bound(sample2, sample2)
    assert len(matched) > 0 and stale == []
    first = [m for m in matched if m["status"] == "completed"][0]
    ok, ev = ha.verify_artifacts("a-w1", "ex-1", first,
                                 {"sha256:fake-a-w1": True})
    assert ok and ev["mode"] == "structural-presence"
    # Completion drives the next bounded action through code.
    d._kv_put("harness-qid", Q)
    res, dup = ha.drive_next("a-w1", "a-v1", "2026-09-21T14:00:00Z",
                             {"output_hash": "sha256:obs"})
    assert dup is False and res["next_action"] == "a-v1"
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["action_id"] == "a-v1"  # verifier flight created in-ledger
    d.close()


def test_escalation_ack_evidence():
    d, ha = mk()
    running(d)
    r, dup = ha.escalate_unavailable("a-w1", "tern", "manual-check",
                                     "2026-09-21T16:00:00Z")
    assert (r, dup) == ("escalated-owned", False)
    assert ha.confirm_escalation_ack("a-w1") == \
        ("escalation-pending", False)  # fake transport: queued, not acked
    ha.transport.mark(ha.escalations[0]["message_id"], "delivered")
    assert ha.confirm_escalation_ack("a-w1") == \
        ("escalated-acknowledged", True)  # actual ack evidence
    d.close()


# --- (5) executable plan ---------------------------------------------------------------------
def test_fixture_plan_executable_no_placeholders():
    import json
    plan = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                       "fixture-plan.json")))
    import re
    text = json.dumps(plan)
    assert not re.findall(r"<[A-Za-z_][A-Za-z_0-9-]*>", text)  # no placeholders
    assert plan["seats"]["fixture_seats"] == ["p6-fixture-worker",
                                             "p6-fixture-verifier"]
    assert len(plan["setup"]) >= 3 and len(plan["run"]) >= 1
    assert len(plan["assertions"]) >= 2 and len(plan["cleanup"]) >= 3
    for cmd in plan["setup"] + plan["run"] + plan["assertions"] + \
            plan["cleanup"]:
        # Correction (r2.1 amendment): plan IDs are p6h-handoff scoped.
        assert "P6F" in cmd or "p6f" in cmd or "p6h" in cmd or "P6H" in cmd \
            or "p6-fixture" in cmd or \
            "harness" in cmd or "manifest" in cmd or "latency" in cmd or \
            "rollback" in cmd or "mkdir" in cmd or "sha256sum" in cmd or \
            "systemctl" in cmd or "test " in cmd or "cat " in cmd or \
            "AID" in cmd or "VID" in cmd or "EXEC" in cmd, cmd
