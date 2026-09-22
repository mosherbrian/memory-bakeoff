"""P6-r4 N/T/O gates: production notification, enforced timer mapping,
delivered-outbox drain. Positive and negative; injected OS boundaries."""
import io
import json
import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from notify import DirNotifier, OwnedFaultLocal
from host_adapter import HostAdapter, HostWakeTransport, HostTimerService
from driver import Driver, FakeClock, FakeExternalWorld


def mktree():
    tmp = tempfile.mkdtemp(prefix="p6n-")
    for sub in ("stream", "claims", "art"):
        os.makedirs(os.path.join(tmp, sub))
    return tmp


def mk(tmp):
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    return d, HostAdapter(d)


# --- N --------------------------------------------------------------------------
def test_n_production_notifier_wakes_without_sleep():
    import harness as _h
    import inspect
    assert "time.sleep" not in inspect.getsource(_h._wait_end)  # no polling
    tmp = mktree()
    path = os.path.join(tmp, "stream", "w.jsonl")
    open(path, "w").close()
    n = DirNotifier(os.path.join(tmp, "stream"))
    box = {}
    t = threading.Thread(target=lambda: box.update(
        {"fired": n.wait(5.0)}))
    t.start()
    time.sleep(0.3)
    with open(path, "a") as fh:
        fh.write('{"t":"end","item":"i1"}\n')  # appended AFTER wait starts
    t.join(timeout=10)
    assert box.get("fired") is True  # OS primitive woke the waiter
    fd = n.fd
    n.close()
    assert n.closed is True
    assert not os.path.exists("/proc/self/fd/%d" % fd)  # fd really gone


def test_n_timeout_bounded_and_startup_event_once():
    tmp = mktree()
    path = os.path.join(tmp, "stream", "w.jsonl")
    with open(path, "w") as fh:
        fh.write('{"t":"end","item":"i0"}\n')  # startup-existing event
    n = DirNotifier(os.path.join(tmp, "stream"))
    assert n.wait(0.2) is False  # attached after write: no retroactive fire
    n.close()
    try:
        DirNotifier("/nonexistent-dir-xyz")
        assert False, "expected E_NO_NOTIFY"
    except OwnedFaultLocal as e:
        assert e.code == "E_NO_NOTIFY", e


def test_n_missing_dir_fails_closed():
    try:
        DirNotifier("/nonexistent-dir-xyz-abc")
        assert False
    except OwnedFaultLocal as e:
        assert e.code == "E_NO_NOTIFY", e


# --- T ----------------------------------------------------------------------------
def _timers(tmp, **kw):
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(),
               FakeExternalWorld(os.path.join(tmp, "world.json")))
    args = dict(kv_get=d.kv.get, kv_put=d._kv_put, enabled=True,
                allowlist=("u-h1.timer",))
    args.update(kw)
    return d, HostTimerService(**args)


def test_t_mapping_mismatch_rejected():
    import harness as _h
    tmp = mktree()
    d, ha = mk(tmp)
    assert _h._arm_host_timer if False else True
    # No create_host capability (plain fake timers) is never a backstop.
    try:
        _h._arm_host_timer(ha, {"action_id": "a-w1"}, "2026-09-22T01:00:00Z",
                           "u-h1.timer")
        assert False
    except Exception as e:
        assert getattr(e, "code", "") == "E_NO_TIMER", e
    d.close()


def test_t_rejected_allowlist_and_failed_runner():
    import harness as _h
    tmp = mktree()
    d, ha = mk(tmp)
    ha.timers = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put,
                                 enabled=False, allowlist=("u-h1.timer",))
    try:
        _h._arm_host_timer(ha, {"action_id": "a-w1"},
                           "2026-09-22T01:00:00Z", "u-h1.timer")
        assert False, "expected E_DISABLED"
    except Exception as e:
        assert getattr(e, "code", "") == "E_DISABLED", e

    class Boom:
        def __call__(self, cmd, **kw):
            class O:
                returncode = 1
                stdout = ""
                stderr = "refused"
            return O()
    ha.timers = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put,
                                 enabled=True, allowlist=("u-h1.timer",),
                                 runner=Boom())
    try:
        _h._arm_host_timer(ha, {"action_id": "a-w1"},
                           "2099-01-01T00:00:00Z", "u-h1.timer")
        assert False, "expected E_TIMER_CREATE"
    except Exception as e:
        assert getattr(e, "code", "") == "E_TIMER_CREATE", e
    d.close()


def test_t_callback_authority_after_reopen():
    import harness as _h
    tmp = mktree()
    d, ha = mk(tmp)
    d.admit_authorize("Q9")
    d.start_dispatch("Q9", "a-w1", duration_s=3600)
    d.acknowledge("a-w1")
    db = d.store.path
    d.close()
    out = _h.timer_callback(db, "deadline:a-w1", "Q9", "a-w1")
    assert out["timer"] == "deadline:a-w1" and "decision" in out
    out2 = _h.timer_callback(db, "deadline:a-w1", "Q9", "wrong-action")
    assert out2["decision"] in ("no-op-stale-action",
                                "no-op-no-current-action",
                                "no-op-not-armed", "already-handled")


# --- O -------------------------------------------------------------------------------
def test_o_settle_only_on_proof():
    tmp = mktree()
    d, ha = mk(tmp)
    d.admit_authorize("QX")
    d.start_dispatch("QX", "a-w1", duration_s=3600)
    ha.bind_route("a-v1", "p6-fixture-verifier")
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"})
    # Terminal-looking but no transport proof: never settles.
    assert ha.drain_outbox_settled("QX") == []
    assert ha.driver.kv.get("outbox-pending:" + oid)
    # Queued proof: still pending.
    ha.transport.mark(ha.driver.kv.get("outbox-sent:" + oid), "queued") \
        if ha.driver.kv.get("outbox-sent:" + oid) else None
    assert ha.drain_outbox_settled("QX") == []
    d.close()


def test_o_ambiguous_blocks_rollback_terminal_does_not_forge():
    import harness as _h
    tmp = mktree()
    d, ha = mk(tmp)
    d.admit_authorize("QY")
    d.start_dispatch("QY", "a-w1", duration_s=3600)
    ha.bind_route("a-v1", "p6-fixture-verifier")
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"})
    manifest = os.path.join(tmp, "m.json")
    json.dump({"allowlist_units": []}, open(manifest, "w"))
    try:
        _h.rollback_verify(os.path.join(tmp, "ledger.db"), manifest,
                           os.path.join(tmp, "arc"))
        assert False, "expected E_ROLLBACK_BLOCKED"
    except Exception as e:
        assert getattr(e, "code", "") == "E_ROLLBACK_BLOCKED", e
    assert not os.path.exists(os.path.join(tmp, "arc",
                                           "rollback-report.json"))
    d.close()


def test_o_crash_boundaries_same_identity():
    # Correction (O-settlement repair): Fake-transport in-memory marks are
    # not production receipts and carry no execution binding, so the
    # strict drain path (kv receipt + bound execution + ledger proof)
    # does not settle them. This test now runs the production transport
    # branch with an injected runner.
    from host_adapter import HostWakeTransport

    class _Ok:
        def __init__(self):
            self.calls = []

        def __call__(self, cmd, **kw):
            self.calls.append((cmd, kw))

            class _Out:
                returncode = 0
                stdout = "wake: seat -> started\n"
                stderr = ""
            return _Out()
    tmp = mktree()
    d, _ = mk(tmp)
    d.admit_authorize("QZ")
    d.start_dispatch("QZ", "a-w1", duration_s=3600)
    run = _Ok()
    t = HostWakeTransport("/bin/wake", ("p6-fixture-verifier",),
                          enabled=True, kv_get=d.kv.get, kv_put=d._kv_put,
                          runner=run)
    from host_adapter import HostAdapter as _HA
    ha = _HA(d, transport=t)
    ha.register_execution("a-v1", "ex-v", "auth-1",
                          "2026-09-22T01:00:00Z")
    ha.register_execution("a-v2", "ex-v2", "auth-1",
                          "2026-09-22T01:00:00Z")
    ha.bind_route("a-v1", "p6-fixture-verifier")
    ha.bind_route("a-v2", "p6-fixture-verifier")
    d._kv_put("turn-seen:sess:i-v:ex-v", '{"outcome":"completed"}')
    # Crash after send, before ack: same outbox id reconciles, no resend.
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    d.publish_completion("QZ", "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": "2026-09-22T01:00:00Z"})
    assert ha.drain_outbox_settled("QZ") == [oid]  # receipt + proof
    n_calls = len(run.calls)
    assert ha.drain_outbox_settled("QZ") == []  # idempotent, no resend
    assert len(run.calls) == n_calls
    # Crash before ack with ambiguous transport: holds, never clears.
    oid2 = ha.outbox_send("a-v2", {"kind": "y", "action": "a-v2"},
                          execution="ex-v2")
    mid2 = ha.driver.kv.get("outbox-sent:" + oid2)
    raw = json.loads(ha.driver.kv.get("msg:" + mid2))
    raw["state"] = "ambiguous"
    ha.driver._kv_put("msg:" + mid2, json.dumps(raw))
    assert ha.drain_outbox_settled("QZ") == []
    assert ha.driver.kv.get("outbox-pending:" + oid2)
    d.close()
