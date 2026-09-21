"""P4-r2 new coverage: three director probes reproduced+corrected, genuine due
paths, cancelled/stale/early/wrong-package, repeat effects across reopen,
interrupted-effect ack, crash boundaries. Fresh tmp state; fake time only."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from supervisor import supervise
from status import status_report
import lifecycle as lc

Q = "P4R2"
DL_W = "2026-09-21T13:00:00Z"
DL_V = "2026-09-21T14:00:00Z"
DL_H = "2026-09-21T14:30:00Z"


def mk(artifacts=None):
    tmp = tempfile.mkdtemp(prefix="p4r2-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w, artifacts)
    d.tmp = tmp
    return d


def reopen(d, now):
    """Fresh Driver + fresh adapters sharing the independent world file."""
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    return Driver(db, FakeClock(now), FakeExternalWorld(wpath))


def worker_running(d, aid="a-w1", dl=DL_W):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, dl)
    d.acknowledge(aid)


def to_checking_verifier(d):
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})


# --- the three director probes: parent FAILED, here corrected ---------------
def test_probe1_stale_worker_deadline_noop_in_checking():
    d = mk()
    worker_running(d)
    to_checking_verifier(d)
    d.clock.now = "2026-09-21T13:30:00Z"  # past worker DL, before verifier DL
    r = d.on_deadline("a-w1", Q)
    assert r == ("no-op-cancelled", True), r  # rotation durably cancels worker timer
    assert d.ext.stops == [] and d.ext.wakes == []
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()


def test_probe2_early_current_deadline_noop_before_due():
    d = mk()
    worker_running(d)
    d.clock.now = "2026-09-21T12:30:00Z"  # before worker deadline
    r = d.on_deadline("a-w1", Q)
    assert r == ("no-op-early", True), r
    assert d.ext.stops == [] and d.ext.wakes == []
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"
    d.close()


def test_probe3_reopen_cannot_repeat_stop_wake():
    d = mk()
    worker_running(d)
    d.clock.now = "2026-09-21T15:00:00Z"
    assert d.on_deadline("a-w1", Q) == ("interrupted", False)
    assert len(d.ext.stops) == 1 and len(d.ext.wakes) == 1
    d2 = reopen(d, "2026-09-21T15:30:00Z")  # fresh driver + fresh adapters
    assert d2.ext.stops == [] and d2.ext.wakes == []  # unshared adapters
    r = d2.on_deadline("a-w1", Q)  # same event redelivered after reopen
    assert r == ("already-handled", True), r
    assert d2.ext.stops == [] and d2.ext.wakes == []  # durable: no repeat
    assert d2.world.delivery("stop:a-w1") == "delivered"  # world agrees
    d2.close()


# --- genuine due paths -------------------------------------------------------
def test_genuine_due_worker_interrupts_once():
    d = mk()
    worker_running(d)
    d.clock.now = "2026-09-21T13:00:00Z"  # exactly at deadline
    assert d.on_deadline("a-w1", Q) == ("interrupted", False)
    assert d.store.revisions[(Q, 1)]["phase"] == "BLOCKED"
    assert d.on_deadline("a-w1", Q) == ("already-handled", True)
    d.close()


def test_genuine_due_verifier_after_rotation():
    d = mk()
    worker_running(d)
    to_checking_verifier(d)
    d.clock.now = "2026-09-21T13:30:00Z"
    assert d.on_deadline("a-v1", Q)[1] is True  # early: no-op
    d.clock.now = "2026-09-21T14:00:00Z"
    assert d.on_deadline("a-v1", Q) == ("interrupted", False)
    assert d.store.revisions[(Q, 1)]["phase"] == "BLOCKED"
    d.close()


def test_genuine_due_handoff_owned_path():
    d = mk()
    worker_running(d)
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         handoff={"handoff_deadline": DL_H, "handoff_owner": "duty"})
    assert "handoff:" + Q in d.timer.armed  # armed from ledger facts
    d.clock.now = "2026-09-21T14:00:00Z"
    assert d.on_handoff_deadline(Q) == ("no-op-early", True)
    assert d.on_deadline("a-w1", Q) == ("no-op-cancelled", True)  # rotation cancelled worker timer; handoff path is duty-owned
    d.clock.now = "2026-09-21T14:30:00Z"
    assert d.on_handoff_deadline(Q) == ("interrupted", False)
    assert d.store.revisions[(Q, 1)]["phase"] == "BLOCKED"
    d.close()


# --- cancelled / wrong-package / trigger dedup across reopen -----------------
def test_wrong_package_and_old_generation_noop():
    d = mk()
    worker_running(d)
    d.clock.now = "2026-09-21T15:00:00Z"
    assert d.on_deadline("a-w1", "OTHER")[0].startswith("no-op")
    assert d.on_deadline("a-old", Q)[0].startswith("no-op")  # never-armed old action
    assert d.ext.stops == [] and d.ext.wakes == []
    d.close()


def test_action_due_trigger_dedup_durable_across_reopen():
    d = mk()
    assert d.dedupe_trigger("t1") is False
    d2 = reopen(d, "2026-09-21T12:00:00Z")
    assert d2.dedupe_trigger("t1") is True  # durable, not an in-memory set
    d2.close()


def test_interrupted_effect_acknowledged_in_world():
    d = mk()
    worker_running(d)
    d.clock.now = "2026-09-21T15:00:00Z"
    d.on_deadline("a-w1", Q)
    assert d.world.delivery("stop:a-w1") == "delivered"
    r = d.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "effect-already-handled", r
    d.close()


def test_crash_ambiguous_holds_no_exactly_once_claim():
    d = mk()
    worker_running(d)
    d.world.record("a-w1", "unknown")  # lost delivery evidence
    d.store.set_ack("a-w1", "intended")
    r = d.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "hold-for-reconciliation", r
    assert d.launch.launches.count("a-w1") == 1
    d.close()


def test_output_hashes_and_status_simulated():
    d = mk()
    worker_running(d)
    arts = d.world.state["a-w1"]
    assert arts["delivery"] == "dispatched"
    to_checking_verifier(d)
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    v = supervise(snap, d.ledger(), "2026-09-21T13:30:00Z")
    assert v["verdict"] == "ACTIVE", v
    rep = status_report(Q + "-r1", d.ledger()["packages"], snap, v)
    assert rep["simulated"] is True and rep["action"] == "a-v1"
    assert rep["deadline"] == DL_V and rep["duty"] == "cairn"
    assert d.ext.notifications == []
    d.close()


def test_no_live_effects_possible():
    import driver as drvmod
    import inspect
    src = inspect.getsource(drvmod)
    for banned in ("import subprocess", "import socket", "os.kill",
                   "import signal", "import requests", "urllib.request",
                   "import openai", "import anthropic", "time.sleep",
                   "while True:"):
        assert banned not in src, banned
