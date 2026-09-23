"""P4-r2 sole-repair tests: D1 per-effect crash boundaries with true reopen;
D2 explicit durable cancellation vs accidental loss. Fresh tmp state."""
import os
import sys
import tempfile

sys.path.insert(0, "/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/candidate/src/r3harness")  # ADAPTED P6-r13: exercise NEW core

from driver import (Driver, FakeClock, FakeExternalWorld, SimulatedCrash,
                    CRASH_AFTER_INTERRUPT, CRASH_AFTER_STOP,
                    CRASH_AFTER_STOP_ACK, CRASH_AFTER_WAKE,
                    CRASH_AFTER_WAKE_ACK)
from supervisor import supervise

Q = "P4R2X"
DL_W = "2026-09-21T13:00:00Z"
NOW_DUE = "2026-09-21T15:00:00Z"


def mk():
    tmp = tempfile.mkdtemp(prefix="p4r2r-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


def reopen(d, now=NOW_DUE):
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    return Driver(db, FakeClock(now), FakeExternalWorld(wpath))


def world_stops(w):
    return [k for k, v in w.state.items()
            if k.startswith("stop:") and v.get("delivery") == "delivered"]


def world_wakes(w):
    return [k for k, v in w.state.items()
            if k.startswith("wake:") and v.get("delivery") == "delivered"]


def crash_replay(point):
    """Crash at `point`, reopen with fresh driver/adapters, replay."""
    d = mk()
    running(d)
    d.clock.now = NOW_DUE
    d.crash_points = {point}
    try:
        d.on_deadline("a-w1", Q)
        assert False, "expected SimulatedCrash at " + point
    except SimulatedCrash:
        pass
    d2 = reopen(d)  # true reopen: fresh Driver, fresh adapters, file-backed world
    assert d2.ext.stops == [] and d2.ext.wakes == []
    r = d2.on_deadline("a-w1", Q)
    return d2, r


# --- D1: crash after each call; delivered effects never repeat ---------------
def test_d1_crash_after_stop_before_wake():
    # Stop delivered+acked, wake never attempted: replay completes the
    # pending wake without repeating the delivered stop.
    d2, r = crash_replay(CRASH_AFTER_STOP_ACK)
    assert r[1] is False, r  # pending wake completed on replay
    assert world_stops(d2.world) == ["stop:a-w1"]  # exactly one stop delivery
    assert world_wakes(d2.world) == ["wake:tern:deadline-expired:" + Q]
    assert d2.ext.stops == []  # replay did NOT repeat stop
    assert d2.ext.wakes == [("tern", "deadline-expired:" + Q)]
    d2.close()


def test_d1_crash_after_stop_call_before_local_ack():
    d2, r = crash_replay(CRASH_AFTER_STOP)  # stop delivered in world, ack lost
    assert r[1] is False, r
    assert world_stops(d2.world) == ["stop:a-w1"]  # reconciled, never resent
    assert d2.ext.stops == []  # no repeat despite missing local ack
    assert len(d2.ext.wakes) == 1
    d2.close()


def test_d1_crash_after_wake_before_combined_ack():
    d2, r = crash_replay(CRASH_AFTER_WAKE_ACK)  # both delivered, combined ack lost
    assert r == ("already-handled", True), r  # receipts reconcile; nothing resent
    assert d2.ext.stops == [] and d2.ext.wakes == []
    d2.close()


def test_d1_crash_after_interrupt_before_stop():
    d2, r = crash_replay(CRASH_AFTER_INTERRUPT)
    assert r[1] is False, r
    assert world_stops(d2.world) == ["stop:a-w1"]
    assert d2.ext.stops == [("a-w1", "deadline-expired")]
    # interrupt recorded exactly once (same event_id idempotent across reopen)
    n_int = sum(1 for (qq, _rv), rec in d2.store.revisions.items()
                for _e in rec["history"] if _e == "a-w1-int")
    assert n_int == 1
    d2.close()


def test_d1_ambiguous_receipt_holds_owned():
    d = mk()
    running(d)
    d.world.record("a-w1", "unknown")
    d.store.set_ack("a-w1", "intended")
    r = d.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "hold-for-reconciliation", r
    assert d.launch.launches.count("a-w1") == 1  # never blind replay
    d.close()


# --- D2: explicit cancellation vs accidental loss -----------------------------
def test_d2_cancel_current_timer_then_due_callback_noop():
    d = mk()
    running(d)
    assert d.cancel_deadline("a-w1", Q, owner="cairn",
                             reason="owned-hold") == ("cancelled", True)
    d.clock.now = NOW_DUE
    r = d.on_deadline("a-w1", Q)
    assert r == ("no-op-cancelled", True), r
    assert d.ext.stops == [] and d.ext.wakes == []
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"  # genuine state kept
    d.close()


def test_d2_cancellation_survives_reopen_loss_does_not():
    d = mk()
    running(d)
    d.cancel_deadline("a-w1", Q, owner="cairn", reason="owned-hold")
    d2 = reopen(d)
    # Explicit cancellation: still invalid after reopen; no reconstruction.
    assert "deadline:a-w1" not in d2.timer.armed
    assert d2.on_deadline("a-w1", Q) == ("no-op-cancelled", True)
    assert d2.ext.stops == [] and d2.ext.wakes == []
    r = d2.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "cancelled-owned", r  # owned follow-up, not silence
    d2.close()
    # Accidental loss: fresh DB copy without the cancel record reconstructs
    # the still-valid deadline and enforces it.
    d3 = mk()
    running(d3)
    d4 = reopen(d3)  # no cancellation recorded: loss, not cancel
    assert "deadline:a-w1" in d4.timer.armed  # reconstructed valid deadline
    assert d4.on_deadline("a-w1", Q)[0] in ("interrupted", "recovered")
    assert len(d4.ext.stops) == 1  # genuine enforcement preserved
    d4.close()


def test_d2_cancelled_package_stays_ledger_accountable():
    d = mk()
    running(d)
    d.cancel_deadline("a-w1", Q, owner="cairn", reason="owned-hold")
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    # Cancelling delivery does not cancel the ledger deadline: supervision
    # still flags the overdue flight (no unowned-silence escape).
    v = supervise(snap, d.ledger(), NOW_DUE)
    assert v["verdict"] == "INVALID", v
    d.close()
