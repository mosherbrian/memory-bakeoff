"""P6 sole-repair tests: D1 runnable host path (fakes injected, live
disabled), D2 single-transaction replacement, D3 trusted receipt time,
D4 durable one-shot timers. Each proves the repaired behavior; comments
mark the initial failure each test guards."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from host_adapter import (HostAdapter, HostTimerService, HostWakeTransport,
                          ACPOutcomeObserver, OwnedFault)

Q = "P6R"
ATT = "a1"
DL_W = "2026-09-21T13:00:00Z"


def mk(clock=None):
    tmp = tempfile.mkdtemp(prefix="p6r-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), clock or FakeClock(), w)
    d.tmp = tmp
    return d, HostAdapter(d)


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


def reopen(d):
    db, wpath = d.store.path, os.path.join(d.tmp, "world.json")
    clk = FakeClock(d.clock.now)
    d.close()
    return Driver(db, clk, FakeExternalWorld(wpath))


# --- D1 -----------------------------------------------------------------------
def test_d1_exact_commands_bind_fixture_plan():
    wt = HostWakeTransport("/home/bmosher/.config/agent-deck/wake",
                           allowlist_seats=("p6-fixture-worker",),
                           enabled=False)
    assert wt.command_for("p6-fixture-worker", "run?") == [
        "/home/bmosher/.config/agent-deck/wake", "p6-fixture-worker", "run?"]
    ts = HostTimerService(enabled=False,
                          allowlist=("p6-fixture-recovery-1.timer",))
    cb = ["python3", "src/harness.py", "timer-callback", "--timer",
          "p6-fixture-recovery-1"]
    cmd = ts.command_for("p6-fixture-recovery-1", 60, cb)
    # Correction (P6-r2): the callback is the executable candidate
    # reconciler, and unit identity is shared with cancel/query.
    assert cmd[:5] == ["systemd-run", "--user",
                       "--unit=p6-fixture-recovery-1",
                       "--on-active=60s", "python3"]
    assert ts.unit_for("p6-fixture-recovery-1") == \
        "p6-fixture-recovery-1.timer"
    plan = json.load(open(os.path.join(
        os.path.dirname(__file__), "..", "fixture-plan.json")))
    assert plan["fixture_id"] == "p6-fixture-recovery-1"  # plan binds IDs
    assert "p6-fixture-worker" in plan["seats"]["fixture_seats"]


def test_d1_observed_outcome_feeds_reconciliation():
    # Adapted to the real ACP turn schema (kind/id/status/at): the observer
    # reads actual-format rows; the adapter binds session->execution.
    d, ha = mk()
    running(d)
    hist = os.path.join(d.tmp, "sess.jsonl")
    with open(hist, "w") as fh:
        fh.write(json.dumps({"role": "user", "text": "run",
                             "at": "2026-09-21T12:00:00Z"}) + "\n")
        fh.write(json.dumps({"id": "t-1", "kind": "execute",
                             "title": "run", "status": "failed",
                             "at": "2026-09-21T12:01:00Z"}) + "\n")
    ha.observer = ACPOutcomeObserver(hist)
    ha.bind_session(hist, "ex-1", "a-w1")
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    matched, stale, note = ha.observe_bound(hist, hist)
    assert len(matched) == 1 and matched[0]["status"] == "failed"
    assert matched[0]["execution_id"] == "ex-1"  # bound, not inferred
    d.close()


def test_d1_trail_correlates_dispatch_to_outcome():
    d, ha = mk()
    running(d)
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    ha.capture(Q, ATT, "a-w1", "ev-1", "ex-1", "dispatched",
               occurred_at="2026-09-21T12:00:00Z", provenance="wake-receipt")
    ha.apply_execution_result("a-w1", "ex-1", {"output_hash": "sha256:x"})
    trail = ha.trail("a-w1")
    assert trail["executions"] and trail["receipts"] and trail["applied"]
    assert trail["receipts"][0]["receipt_at_utc"] == "2026-09-21T12:00:00Z"
    d.close()


# --- D2 --------------------------------------------------------------------------
def test_d2_crash_mid_replace_leaves_no_partial_state():
    d, ha = mk()
    running(d)
    ha.register_execution("a-w1", "ex-1", "auth-1", DL_W)
    real_execute = d.store.conn.execute
    calls = []
    orig_put_many = d._kv_put_many

    def flaky(pairs):
        pairs = list(pairs)
        real_execute(
            "INSERT OR REPLACE INTO driver_kv (key, value) VALUES (?, ?)",
            pairs[0])
        d._kv_reload()
        raise RuntimeError("injected crash before remaining writes")

    d._kv_put_many = flaky
    try:
        ha.replace_action("a-w1", "a-w2", "ex-9", "auth-r", DL_W, False)
        assert False, "expected injected crash"
    except RuntimeError:
        pass
    finally:
        d._kv_put_many = orig_put_many
    # Initial failure was: old='SUPERSEDED->new', new=None. Now: neither.
    assert ha.current_execution("a-w1") == "ex-1"  # projection refreshed
    assert ha.current_execution("a-w2") is None
    d2 = reopen(d)
    assert HostAdapter(d2).current_execution("a-w1") == "ex-1"
    assert HostAdapter(d2).current_execution("a-w2") is None
    d2.close()


def test_d2_receipt_cursor_atomic_no_skip_loss():
    d, ha = mk()
    running(d)
    ha.capture(Q, ATT, "a-w1", "ev-1", "ex-1", "dispatched",
               occurred_at="2026-09-21T12:00:00Z")
    d2 = reopen(d)
    ha2 = HostAdapter(d2)  # restart: both receipt and cursor present
    assert ha2.cursor == "ev-1"
    assert ha2.receipt(Q, ATT, "a-w1", "ev-1", "ex-1")["outcome"] == \
        "dispatched"
    assert ha2.resume_from_cursor() == "ev-1"  # resumes, never skips
    d2.close()


# --- D3 --------------------------------------------------------------------------
def test_d3_caller_2099_not_persisted_as_receipt():
    d, ha = mk()
    running(d)
    # Initial failure persisted the caller value directly. Now quarantined.
    try:
        ha.capture(Q, ATT, "a-w1", "ev-9", "ex-1", "dispatched",
                   occurred_at="2099-01-01T00:00:00Z", provenance="seat")
        assert False, "expected E_SKEW_EXCEEDED"
    except OwnedFault as e:
        assert e.code == "E_SKEW_EXCEEDED", e
    assert ha.receipt(Q, ATT, "a-w1", "ev-9", "ex-1") is None
    d.close()


def test_d3_conflict_rejected_identical_dedups():
    d, ha = mk()
    running(d)
    ha.capture(Q, ATT, "a-w1", "ev-1", "ex-1", "dispatched",
               occurred_at="2026-09-21T12:00:00Z", provenance="wake")
    key, dup = ha.capture(Q, ATT, "a-w1", "ev-1", "ex-1", "dispatched",
                          occurred_at="2026-09-21T12:00:00Z",
                          provenance="wake")
    assert dup is True  # identical: idempotent
    try:
        ha.capture(Q, ATT, "a-w1", "ev-1", "ex-1", "failed",
                   occurred_at="2026-09-21T12:00:00Z", provenance="wake")
        assert False, "expected E_CONFLICT"
    except OwnedFault as e:
        assert e.code == "E_CONFLICT", e  # no overwrite-as-dedup
    assert ha.receipt(Q, ATT, "a-w1", "ev-1", "ex-1")["outcome"] == \
        "dispatched"  # durable identity kept
    d.close()


def test_d3_escalation_is_not_acknowledged_delivery():
    d, ha = mk()
    running(d)
    mid = ha.transport.send("tern", "help")
    ha.escalate_unavailable("a-w1", "tern", "manual-check",
                            "2026-09-21T16:00:00Z")
    r = ha.reconcile_send(mid, "a-w1")  # transport still queued
    assert r["decision"] == "hold-for-receipt"  # escalation != ack
    d.close()


# --- D4 --------------------------------------------------------------------------
def test_d4_repeat_rejected_durably_across_restart():
    d, ha = mk()
    running(d)
    ha.arm_from_ledger("t-w1", DL_W, "2026-09-21T12:00:00Z")
    d.clock.now = "2026-09-21T13:00:00Z"
    assert ha.timers.fire("t-w1", d.clock.now, DL_W) == ("fired", False)
    # Initial failure returned fired twice. Now durably handled:
    assert ha.timers.fire("t-w1", d.clock.now, DL_W) == \
        ("already-handled", True)
    d2 = reopen(d)
    ha2 = HostAdapter(d2)  # fresh process + fresh adapter
    assert ha2.timers.fire("t-w1", d2.clock.now, DL_W) == \
        ("already-handled", True)  # no repeat, zero new effects
    d2.close()


def test_d4_cancelled_rejected_across_restart_and_armed_from_ledger():
    d, ha = mk()
    running(d)
    ha.arm_from_ledger("t-w1", DL_W, "2026-09-21T12:00:00Z")
    ha.timers.cancel("t-w1")
    d2 = reopen(d)
    ha2 = HostAdapter(d2)
    assert ha2.timers.fire("t-w1", d2.clock.now, DL_W)[0] == \
        "no-op-not-armed"  # durable cancellation survives restart
    # arm_current reads the authoritative deadline with trusted now.
    assert ha2.arm_current("t-w2", Q) == ("armed", False)
    assert ha2.timers.timers["t-w2"]["deadline"] == DL_W  # not caller-set
    d2.close()
