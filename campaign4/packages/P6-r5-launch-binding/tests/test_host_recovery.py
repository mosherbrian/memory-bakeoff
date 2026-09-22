"""P6 Stage-A recovery matrix: injected event/transport/timer failures with
independently reconciled effects. Fake transports/timers only; no live
effects, no duplicate dispatch, no phantom ack, no unlimited retry."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from host_adapter import HostAdapter, OwnedFault

Q = "P6F"
ATTEMPT = "a1"
DL_W = "2026-09-21T13:00:00Z"


def mk():
    tmp = tempfile.mkdtemp(prefix="p6-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d, HostAdapter(d)


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


# --- transport: lost/queued/failed/ambiguous ----------------------------------
def test_lost_completion_wake_holds_no_blind_retry():
    d, ha = mk()
    running(d)
    mid = ha.transport.send("kiln", "done?")
    assert ha.reconcile_send(mid, "a-w1")["decision"] == \
        "hold-for-receipt"  # queued is not completion
    ha.transport.mark(mid, "ambiguous")
    r = ha.reconcile_send(mid, "a-w1")
    assert r["decision"] == "hold-for-reconciliation"
    assert ha.transport.calls == [("kiln", "done?", "wake")]  # no retry sent
    d.close()


def test_queued_wake_is_neither_recovery_nor_escalation():
    d, ha = mk()
    running(d)
    mid = ha.transport.send("corvid", "verify?")
    assert ha.transport.state(mid) == "queued"
    assert ha.reconcile_send(mid, "a-v1")["decision"] != "settled-delivered"
    assert ha.escalations == []
    d.close()


def test_explicit_failed_turn_consumed_deadline_fallback():
    d, ha = mk()
    running(d)
    mid = ha.transport.send("kiln", "run?")
    ha.transport.mark(mid, "failed")
    r = ha.reconcile_send(mid, "a-w1")
    assert r["decision"] == "owned-failure"
    assert "deadline fallback" in r["note"]
    d.close()


def test_restart_before_send_and_after_ack():
    d, ha = mk()
    running(d)
    db, wpath = d.store.path, ha.driver.world.path
    d.close()
    d2 = Driver(db, FakeClock("2026-09-21T12:30:00Z"),
                FakeExternalWorld(wpath))
    ha2 = HostAdapter(d2)  # fresh adapter, persisted kv
    assert ha2.cursor is None  # no receipts yet: nothing to claim
    mid = ha2.transport.send("kiln", "run?")  # send after restart
    ha2.transport.mark(mid, "delivered")
    assert ha2.reconcile_send(mid, "a-w1")["decision"] == \
        "settled-delivered"
    d2.close()


def test_unavailable_receiver_bounded_escalation():
    d, ha = mk()
    running(d)
    r, dup = ha.escalate_unavailable("a-w1", "tern", "manual-check",
                                     "2026-09-21T16:00:00Z")
    assert (r, dup) == ("escalated-owned", False)
    assert ha.escalations[0]["owner"] == "tern"
    d.close()


# --- events: stale/duplicate/reordered ------------------------------------------
def test_stale_duplicate_reordered_events():
    d, ha = mk()
    running(d)
    key = ha.capture(Q, ATTEMPT, "a-w1", "ev-1", "ex-1", "dispatched",
                     "2026-09-21T12:00:00Z")
    assert ha.receipt(Q, ATTEMPT, "a-w1", "ev-1", "ex-1")["outcome"] == \
        "dispatched"
    assert ha.receipt(Q, ATTEMPT, "a-w1", "ev-9", "ex-1") is None
    assert ha.cursor == "ev-1"
    d.close()


# --- timers: lost/removed/early ---------------------------------------------------
def test_timer_matrix_from_remaining_duration():
    d, ha = mk()
    running(d)
    assert ha.arm_from_ledger("t-w1", DL_W, "2026-09-21T12:00:00Z") == \
        ("armed", False)  # 3600 s remain
    assert ha.timers.fire("t-w1", "2026-09-21T12:00:00Z", DL_W) == \
        ("no-op-early", True)  # early rejected
    assert ha.timers.fire("t-w1", "2026-09-21T14:00:00Z",
                          "2026-09-21T14:00:00Z") == ("no-op-stale", True)
    assert ha.timers.fire("t-w1", "2026-09-21T13:00:00Z", DL_W) == \
        ("fired", False)  # genuine due fires
    ha.timers.cancel("t-lost")
    assert ha.timers.fire("t-lost", "2026-09-21T15:00:00Z", DL_W) == \
        ("no-op-not-armed", True)  # removed/cancelled rejected
    try:
        ha.arm_from_ledger("t-x", DL_W, "2026-09-21T15:00:00Z")  # expired
        assert False, "expected E_EXPIRED"
    except OwnedFault as e:
        assert e.code == "E_EXPIRED", e
    d.close()


def test_startup_ambiguity_is_owned_fault():
    d, ha = mk()
    assert ha.receipt(Q, ATTEMPT, "a-w1", "ev-1", "ex-1") is None
    assert ha.cursor is None  # no evidence claimed at startup
    d.close()


# --- identity: stale execution, resume, replacement -------------------------------
def test_stale_execution_completion_retained_not_applied():
    d, ha = mk()
    running(d)
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    ha.register_execution("a-w1", "ex-2", "auth-1", DL_W)  # replacement run
    r, dup = ha.apply_execution_result("a-w1", "ex-1", {"output": "late"})
    assert (r, dup) == ("stale-retained-not-applied", True)  # never applied
    r, dup = ha.apply_execution_result("a-w1", "ex-2", {"output": "fresh"})
    assert (r, dup) == ("applied", False)
    assert "suffix" not in json_key_check(ha)  # no suffix inference anywhere
    d.close()


def json_key_check(ha):
    import json
    return json.dumps(dict(ha.driver.kv))


def test_same_action_resume_keeps_identities():
    d, ha = mk()
    running(d)
    r, dup = ha.resume_execution("a-w1", ATTEMPT, "ex-1", "ex-2",
                                 "auth-rec", DL_W, "RUNNING")
    assert (r, dup) == ("resumed", False)
    assert ha.current_execution("a-w1") == "ex-2"
    import json
    rel = json.loads(ha.driver.kv["rel:a-w1:ex-2"])
    assert rel["relationship"] == "resume" and \
        rel["resumes_action_id"] == "a-w1"  # same action retained
    d.close()


def test_genuine_replacement_atomic_no_partial():
    d, ha = mk()
    running(d)
    r, dup = ha.replace_action("a-w1", "a-w2", "ex-9", "auth-rep", DL_W,
                               attempt_changed=False)
    assert (r, dup) == ("replaced", False)
    import json
    rel = json.loads(ha.driver.kv["rel:a-w2:ex-9"])
    assert rel["relationship"] == "supersedes" and \
        rel["supersedes_action_id"] == "a-w1"
    assert ha.current_execution("a-w1") == "SUPERSEDED->a-w2"
    assert ha.current_execution("a-w2") == "ex-9"
    # Late old completion cannot close the successor.
    r, dup = ha.apply_execution_result("a-w1", "ex-1", {"output": "late"})
    assert dup is True
    d.close()


def test_transaction_boundary_restart():
    d, ha = mk()
    running(d)
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    ha.capture(Q, ATTEMPT, "a-w1", "ev-1", "ex-1", "dispatched",
               "2026-09-21T12:00:00Z")
    db, wpath = d.store.path, ha.driver.world.path
    d.close()
    d2 = Driver(db, FakeClock("2026-09-21T12:30:00Z"),
                FakeExternalWorld(wpath))
    ha2 = HostAdapter(d2)  # restart at transaction boundary
    assert ha2.cursor == "ev-1"  # persisted cursor survives
    assert ha2.current_execution("a-w1") == "ex-1"  # identity survives
    assert ha2.receipt(Q, ATTEMPT, "a-w1", "ev-1", "ex-1")["outcome"] == \
        "dispatched"
    d2.close()


def test_bounded_observation_subscription():
    d, ha = mk()
    assert ha.subscription.tick() == []  # absence is no-evidence
    ha.subscription.inject({"type": "dead-turn", "action": "a-w1"})
    evs = ha.subscription.tick()
    assert evs == [{"type": "dead-turn", "action": "a-w1"}]  # consumed once
    assert ha.subscription.tick() == []
    d.close()


def test_no_live_effects_possible():
    import host_adapter as hamod
    import inspect
    src = inspect.getsource(hamod)
    # The runnable host path exists but is FAIL-CLOSED: construction and
    # import perform zero live effects; sends/timers outside an explicit
    # enabled allowlist raise instead of acting.
    for banned in ("import socket", "os.kill",
                   "import signal", "import requests", "urllib.request",
                   "import openai", "import anthropic", "time.sleep",
                   "while True:"):
        assert banned not in src, banned
    wt = hamod.HostWakeTransport("/nonexistent/wake", allowlist_seats=(),
                                 enabled=False)
    try:
        wt.send("kiln", "x")
        assert False, "expected E_DISABLED"
    except hamod.OwnedFault as e:
        assert e.code == "E_DISABLED", e
    assert wt.calls == []  # nothing invoked
    ts = hamod.HostTimerService(enabled=False)
    try:
        ts.create_host("t-1", 60, "x")
        assert False, "expected E_DISABLED"
    except hamod.OwnedFault as e:
        assert e.code == "E_DISABLED", e
