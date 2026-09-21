"""End-to-end + fault matrix. Fresh tmp state per test; fake time/adapters only."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from supervisor import supervise, dedupe_action_due, load_snapshot
from status import status_report
import lifecycle as lc

Q = "P4R"
DL_W = "2026-09-21T13:00:00Z"
DL_V = "2026-09-21T14:00:00Z"


def mk(artifacts=None, world=None):
    tmp = tempfile.mkdtemp(prefix="p4r2-")
    w = world if world is not None else FakeExternalWorld(
        os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w, artifacts)
    d.tmp = tmp
    return d


def test_happy_path_authz_to_close():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    h = {"output_hash": "sha256:deadbeef"}
    d.publish_completion(Q, "a-w1", h,
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    d.acknowledge("a-v1")
    d.verify(Q, "ev-pass", True)
    # held terminal (row-17 hold) closed by director decide, then accept is n/a;
    # record disposition directly:
    d.store.append(d._ev("ev-dec", Q, "decide", "director",
                         {"disposition": {"kind": "question_answered", "decision_ref": "tern-1",
                                          "reason": "rehearsal ok", "evidence_refs": ["sha256:deadbeef"]}}), d.budget)
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    v = supervise(snap, d.ledger(), "2026-09-21T12:30:00Z")
    assert v["verdict"] == "REST", v
    d.close()


def test_duplicate_delivery_no_new_attempt():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    _, dup = d.start_dispatch(Q, "a-w1", DL_W)
    assert dup is True
    assert d.store.revisions[(Q, 1)]["attempt"] == 1
    d.close()


def test_crash_before_delivery_redelivers_same_action():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    # simulate crash: close without ack, reopen same db
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    d2 = Driver(db, FakeClock("2026-09-21T12:10:00Z"), FakeExternalWorld(wpath))
    r = d2.reconcile_restart(Q, "a-w1")
    # Correction: the independent world durably shows dispatched delivery, so
    # reconciliation settles without redispatch; the attempt count is unchanged.
    assert r["decision"] == "settled-acknowledged", r
    assert d2.store.revisions[(Q, 1)]["attempt"] == 1
    assert d2.launch.launches == []  # never blind-redispatched
    d2.close()


def test_ambiguous_delivery_holds_no_redispatch():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.world.record("a-w1", "unknown")  # ambiguous (world is independent of Driver)
    r = d.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "hold-for-reconciliation"
    assert d.launch.launches.count("a-w1") == 1  # no blind redispatch
    d.close()


def test_crash_after_ack_settled():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    r = d.reconcile_restart(Q, "a-w1")
    assert r["decision"] == "settled-acknowledged", r
    d.close()


def test_repeated_completion_deadline_trigger_dedup():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         handoff={"handoff_deadline": DL_V, "handoff_owner": "duty"})
    # duplicate publish rejected (not CHECKING anymore)
    try:
        d.publish_completion(Q, "a-w1", {"h": "x"}, eid="dup-pub-2",
                             handoff={"handoff_deadline": DL_V, "handoff_owner": "duty"})
        assert False, "expected rejection"
    except lc.TransitionError:
        pass
    # deadline handling is one-shot; worker action is stale after handoff publish
    d.clock.now = "2026-09-21T15:00:00Z"
    r1 = d.on_deadline("a-w1", Q)
    assert r1[1] is True and d.ext.stops == []
    r2 = d.on_deadline("a-w1", Q)
    assert r2[1] is True
    assert d.ext.stops.count(("a-w1", "deadline-expired")) <= 1
    d.close()


def test_lost_timer_reconstructed_no_duplicate_stopwake():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    w = FakeExternalWorld(wpath)
    d2 = Driver(db, FakeClock("2026-09-21T15:00:00Z"), w)  # fresh driver+adapters
    # Correction: restart reconstructs arming from ledger facts in __init__;
    # no caller-supplied re-arming.
    assert "deadline:a-w1" in d2.timer.armed  # reconstructed from ledger facts
    d2.on_deadline("a-w1", Q)
    d2.on_deadline("a-w1", Q)
    assert len(d2.ext.stops) == 1 and len(d2.ext.wakes) == 1
    d2.close()


def test_blocked_verifier_resume_never_reruns_worker():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    d.store.append(d._ev("ev-int", Q, "interrupt", "duty",
                         {"reason": "verifier-blocked", "remaining_verifier_s": 600}),
                   d.budget)
    n_launch = len(d.launch.launches)
    d.store.append(d._ev("ev-res", Q, "resolve", "duty", {}), d.budget)
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    assert d.store.revisions[(Q, 1)]["attempt"] == 1
    assert len(d.launch.launches) == n_launch  # verifier resume, no worker rerun
    d.close()


def test_rest_after_last_package_no_auto_authorize():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    d.verify(Q, "ev-pass", True)
    # held terminal (row-17 hold) closed by director decide, then accept is n/a;
    # record disposition directly:
    d.store.append(d._ev("ev-dec2", Q, "decide", "director",
                         {"disposition": {"kind": "question_answered", "decision_ref": "t-1",
                                          "reason": "done", "evidence_refs": ["h"]}}), d.budget)
    assert d.store.revisions[(Q, 1)]["phase"] == "COMPLETE"
    # finishing must not auto-authorize another: no new revision/attempt exists
    assert (Q, 2) not in d.store.revisions
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    v = supervise(snap, d.ledger(), "2026-09-21T12:30:00Z")
    assert v["verdict"] == "REST"
    d.close()


def test_missing_disposition_reproduces_tern_omission():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    body = {"elapsed_s": 60, "pass_budget_s": 1800, "finding": "positive"}
    try:
        d.store.append(d._ev("ev-pass", Q, "verify_pass", "verifier", body), d.budget)
        assert False, "expected E_MISSING_DISPOSITION"
    except lc.TransitionError as e:
        assert e.code == "E_MISSING_DISPOSITION", e
    finally:
        d.close()


def test_supervision_faults_and_masks():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    led = d.ledger()
    # missing snapshot -> owned fault
    v = supervise(None, led, d.clock.now)
    assert v["verdict"] == "INVALID" and v["action"]["owner"] == "cairn"
    # stale snapshot -> owned fault
    stale = dict(snap, ledger_revision=snap["ledger_revision"] - 1)
    v = supervise(stale, led, d.clock.now)
    assert v["verdict"] == "INVALID"
    # INVALID not masked by file activity / busy seats
    bad = dict(snap)
    bad["in_flight"] = [dict(bad["in_flight"][0], owner="mallory")]
    v = supervise(bad, led, d.clock.now, file_activity=["lots"],
                  busy_seats=["everyone-busy"])
    assert v["verdict"] == "INVALID", v
    # ledger failure -> owned fault, never silent success
    v = supervise(snap, {"broken": 1}, d.clock.now)
    assert v["verdict"] == "INVALID"
    d.close()


def test_stale_worker_timer_cannot_expire_verifier():
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    snap = d.snapshot(os.path.join(d.tmp, "s.json"))
    # ACTIVE must use current verifier deadline DL_V, not stale worker DL_W
    item = [i for i in snap["in_flight"] if i.get("action_id") == "a-v1"][0]
    assert item["deadline"] == DL_V
    v = supervise(snap, d.ledger(), "2026-09-21T13:30:00Z")  # past worker DL, before verifier DL
    assert v["verdict"] == "ACTIVE", v
    # Correction: the stale worker deadline event itself must not interrupt CHECKING.
    d.clock.now = "2026-09-21T13:30:00Z"
    r = d.on_deadline("a-w1", Q)
    assert r == ("no-op-cancelled", True), r  # rotation durably cancels worker timer
    assert d.ext.stops == [] and d.ext.wakes == []
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()


def test_action_due_dedup_across_restart_and_status():
    d = mk()
    snap = {"schema_version": 1, "ledger_revision": 0, "terminal": {
        "P-old-r1": {"state": "TERMINATED",
                     "disposition": {"kind": "blocked",
                                     "blocker": {"id": "b1", "owner": "cairn",
                                                 "resumption": "revisit",
                                                 "wake_trigger": {"event_id": "t1",
                                                                  "revisit_at": "2026-09-21T11:00:00Z"}},
                                     "decision_ref": "t-0", "reason": "blocked"},
                     "decided_by": "tern", "decision_ref": "t-0", "reason": "blocked"}},
            "in_flight": []}
    led = {"revision": 0, "packages": {
        "P-old-r1": {"phase": "TERMINATED", "verdict": "TERMINATED",
                     "disposition": snap["terminal"]["P-old-r1"]["disposition"],
                     "decision_task": None, "blocked": None, "flight": None,
                     "handoff": None, "receipt": None}}}
    v = supervise(snap, led, "2026-09-21T12:00:00Z")
    assert v["verdict"] == "ACTION_DUE", v
    seen = set()
    v2, dup = dedupe_action_due(seen, v)
    assert dup is False
    v3, dup2 = dedupe_action_due(seen, v)  # restart with durable seen set
    assert dup2 is True and v3["verdict"] == "ACTIVE"
    rep = status_report("P-old-r1", led["packages"], snap, v)
    assert rep["simulated"] is True and rep["duty"] == "cairn"
    assert d.ext.notifications == []  # no Brian notification
    d.close()


def test_no_live_effects_possible():
    import driver as drvmod
    import inspect
    src = inspect.getsource(drvmod)
    for banned in ("import subprocess", "import socket", "os.kill", "import signal", "import requests",
                   "urllib.request", "import openai", "import anthropic", "time.sleep", "while True:"):
        assert banned not in src, banned
    d = mk()
    assert d.ext.notifications == []
    d.close()


def test_removed_deadline_is_noop():
    # Correction: cancellation is the publish rotation (worker timer cancelled,
    # verifier deadline armed from ledger facts). Past the worker deadline but
    # before the verifier deadline, the stale worker callback must no-op.
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", DL_W)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid", "deadline": DL_V})
    assert "deadline:a-w1" not in d.timer.armed  # rotated/cancelled
    d.clock.now = "2026-09-21T13:30:00Z"
    res = d.on_deadline("a-w1", Q)
    assert res == ("no-op-cancelled", True), res  # rotation durably cancels worker timer
    assert d.ext.stops == [] and d.ext.wakes == []
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"  # no interrupt
    d.close()


def test_never_armed_deadline_is_noop():
    d = mk()
    d.admit_authorize(Q)
    res = d.on_deadline("a-never", Q)
    # Correction: with no current action at all, the authoritative no-op code
    # is no-op-no-current-action; any no-op never interrupts nor stops/wakes.
    assert res[1] is True and res[0].startswith("no-op"), res
    assert d.ext.stops == [] and d.ext.wakes == []
    d.close()
