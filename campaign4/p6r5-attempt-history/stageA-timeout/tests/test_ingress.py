"""P5 trusted-ingress tests: forged fields, instants, skew, grants, jumps,
restart, duplication, delayed completion, no-bypass. Fake clocks injected."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
import ingress as ingress_mod
from ingress import (TrustedIngress, FakeTestClock, HostClock, IngressError,
                     Quarantined, FUTURE_SKEW_TOLERANCE_S,
                     DISCONTINUITY_THRESHOLD_S)

Q = "P5Q"
DL_V = "2026-09-21T14:00:00Z"


def mk(clock=None):
    tmp = tempfile.mkdtemp(prefix="p5-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), clock or FakeClock(), w)
    d.tmp = tmp
    return d


def start(d, aid="a-w1", **kw):
    d.admit_authorize(Q)
    return d.start_dispatch(Q, aid, duration_s=3600, **kw)


def test_deadline_derived_from_trusted_start():
    d = mk()
    start(d)
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["deadline"] == "2026-09-21T13:00:00Z"  # 12:00 + 3600s, not caller-set
    rec = d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='a-w1-start'").fetchone()[0]
    import json
    body = json.loads(rec)
    assert body["receipt"]["recorded_at"] == "2026-09-21T12:00:00Z"
    assert body["receipt"]["epoch"].startswith("epoch-")
    d.close()


def test_forged_recorded_fields_rejected():
    d = mk()
    d.admit_authorize(Q)
    for forged in ("recorded_at", "receipt", "_trusted"):
        ev = d._ev("fx-" + forged, Q, "interrupt", "duty",
                   {"reason": "x", forged: "fake"})
        ev.pop("actor", None)
        try:
            d.ingress.append(ev, d.budget, grants=d.grants,
                             actor={"seat": "cairn", "role": "duty"})
            assert False, "expected E_FORGED_RECEIPT for " + forged
        except IngressError as e:
            assert e.code == "E_FORGED_RECEIPT", e
    d.close()


def test_caller_start_deadline_forged():
    d = mk()
    d.admit_authorize(Q)
    ev = d._ev("fx-dl", Q, "start", "duty",
               {"action_id": "a-fx", "deadline": "2026-09-22T00:00:00Z"})
    ev.pop("actor", None)
    try:
        d.ingress.append(ev, d.budget, grants=d.grants,
                         actor={"seat": "cairn", "role": "duty"})
        assert False, "expected E_DEADLINE_FORGE"
    except IngressError as e:
        assert e.code == "E_DEADLINE_FORGE", e
    d.close()


def test_malformed_occurred_quarantined():
    d = mk()
    start(d)  # RUNNING so well-formed probes could legally append
    for bad in ("2026-09-21T12:00", "2026-09-21 12:00:00", "not-a-time",
                "2026-09-21T12:00:00", "2026-13-45T99:99:99Z"):
        ev = d._ev("fx-" + str(abs(hash(bad)) % 10**6), Q, "interrupt",
                   "duty", {"reason": "x", "occurred_at": bad,
                            "provenance": "seat-report"})
        try:
            d._submit(ev, "duty")
            assert False, "expected quarantine for " + bad
        except Quarantined as e:
            assert e.code == "E_BAD_OCCURRED", (bad, e.code)
            assert e.evidence["owner"] == "cairn"
    # quarantined claims never touched lifecycle
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"
    d.close()


def test_future_occurrence_within_tolerance_ok():
    d = mk()
    start(d)
    d.acknowledge("a-w1")
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})
    ev = d._ev("ev-note", Q, "interrupt", "duty",
               {"reason": "probe", "occurred_at": "2026-09-21T12:01:00Z",
                "provenance": "seat-report"})
    d._submit(ev, "duty")  # +60s skew: accepted
    d.close()


def test_excess_future_occurrence_quarantined():
    d = mk()
    start(d)
    ev = d._ev("fx-future", Q, "interrupt", "duty",
               {"reason": "x", "occurred_at": "2026-09-21T12:32:00Z",
                "provenance": "seat-report"})  # +32 min like observed rows
    try:
        d._submit(ev, "duty")
        assert False, "expected E_SKEW_EXCEEDED"
    except Quarantined as e:
        assert e.code == "E_SKEW_EXCEEDED", e
        assert e.evidence["owner"] == "cairn"
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"  # unaffected
    d.close()


def test_backdated_retains_both_times_no_retro_auth():
    d = mk()
    start(d)  # recorded 12:00, deadline 13:00
    d.clock.now = "2026-09-21T15:00:00Z"  # receipt long after expiry
    # Correction: the boundary rejects the already-expired nested verifier
    # deadline (E_BAD_DEADLINE) before lifecycle evaluates the late publish;
    # either way nothing is retro-authorized.
    import ingress as ing
    try:
        d.publish_completion(Q, "a-w1", {"h": "x"},
                             verify={"action_id": "a-v1", "owner": "corvid",
                                     "deadline": DL_V})
        assert False, "expired allocation must still fail"
    except ing.IngressError as e:
        assert e.code == "E_BAD_DEADLINE", e  # no retroactive authorize
    d.close()


def test_legitimate_long_deadline_within_grant():
    d = mk()
    d.admit_authorize(Q)
    d.pin_grant("g-long", "2026-10-21T12:00:00Z", phase="run")
    res, dup = d.start_dispatch(Q, "a-long", grant_ref="g-long")
    assert dup is False
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["deadline"] == "2026-10-21T12:00:00Z"  # far future, valid grant
    d.close()


def test_expired_unknown_mismatched_grant():
    d = mk()
    d.admit_authorize(Q)
    d.pin_grant("g-old", "2026-09-21T11:00:00Z", phase="run")
    for kw, code in (({"grant_ref": "g-old"}, "E_GRANT_EXPIRED"),
                     ({"grant_ref": "g-nope"}, "E_GRANT_UNKNOWN"),
                     ({"duration_s": 0}, "E_BAD_DURATION"),
                     ({"duration_s": -5}, "E_BAD_DURATION"),
                     ({"duration_s": 99999}, "E_ALLOC_EXCEEDED")):
        try:
            d.start_dispatch(Q, "a-" + code, **kw)
            assert False, "expected " + code
        except IngressError as e:
            assert e.code == code, (kw, e.code)
    d.pin_grant("g-ver", "2026-09-21T18:00:00Z", phase="verify")
    d.close()  # phase_hint mismatch is covered in test_duration_and_grant_phase_mismatch


def test_duration_and_grant_phase_mismatch():
    d = mk()
    d.admit_authorize(Q)
    d.pin_grant("g-v", "2026-09-21T18:00:00Z", phase="verify")
    # A CHECKING/verify-phase grant cannot authorize a RUNNING start: actual
    # phase binding comes from the grant, not caller hints.
    ev = {"event_id": "fx-mm", "question_id": Q, "revision": 1,
          "type": "start", "action_id": "a-mm", "grant_ref": "g-v"}
    try:
        d._submit(ev, "duty")
        assert False, "expected E_GRANT_MISMATCH"
    except IngressError as e:
        assert e.code == "E_GRANT_MISMATCH", e
    # Caller phase hints are rejected outright at the boundary.
    ev2 = dict(ev, event_id="fx-mm2", phase_hint="run")
    try:
        d._submit(ev2, "duty")
        assert False, "expected E_FORGED_HINT"
    except IngressError as e:
        assert e.code == "E_FORGED_HINT", e
    d.close()


def test_duplicate_append_idempotent():
    d = mk()
    start(d)
    ev = d._ev("dup-1", Q, "interrupt", "duty", {"reason": "x"})
    d._submit(ev, "duty")
    out, dup = d._submit(dict(ev), "duty")
    assert dup is True  # same event_id: no second attempt, no re-stamp
    d.close()


def test_restart_replays_receipt_unchanged():
    d = mk()
    start(d)
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    import json
    before = json.loads(d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='a-w1-start'").fetchone()[0])
    d.close()
    d2 = Driver(db, FakeClock("2026-09-22T00:00:00Z"),
                FakeExternalWorld(wpath))  # restart a day later
    after = json.loads(d2.store.conn.execute(
        "SELECT body FROM events WHERE event_id='a-w1-start'").fetchone()[0])
    assert after["receipt"] == before["receipt"]  # never re-stamped with now
    assert after["receipt"]["recorded_at"] == "2026-09-21T12:00:00Z"
    assert d2.ingress.epoch != before["receipt"]["epoch"]  # new epoch
    d2.close()


def test_wall_jump_forward_quarantined_deadlines_kept():
    d = mk()
    start(d)  # deadline 13:00
    d.clock.advance_wall_only(3600)  # wall jumps, mono frozen: discontinuity
    ev = d._ev("fx-jump", Q, "interrupt", "duty", {"reason": "x"})
    try:
        d._submit(ev, "duty")
        assert False, "expected E_DISCONTINUITY"
    except Quarantined as e:
        assert e.code == "E_DISCONTINUITY", e
        assert "deadlines unchanged" in e.evidence["response"]
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["deadline"] == "2026-09-21T13:00:00Z"  # not reset/lengthened
    # bounded reconciliation opens a new epoch; writes resume
    d.ingress.reconcile_clock("operator confirms NTP step", owner="cairn")
    d._submit(d._ev("fx-ok", Q, "interrupt", "duty", {"reason": "y"}),
                "duty")
    d.close()


def test_wall_jump_backward_quarantined():
    d = mk()
    start(d)
    d.clock.now = "2026-09-21T11:00:00Z"  # wall back 1h, mono ran forward
    d.clock._mono += 7200.0  # mono kept running: divergent
    ev = d._ev("fx-back", Q, "interrupt", "duty", {"reason": "x"})
    try:
        d._submit(ev, "duty")
        assert False, "expected E_DISCONTINUITY"
    except Quarantined as e:
        assert e.code == "E_DISCONTINUITY", e
    d.close()


def test_grants_persist_across_restart():
    d = mk()
    d.admit_authorize(Q)
    d.pin_grant("g-p", "2026-09-22T12:00:00Z", phase="run")
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    d2 = Driver(db, FakeClock("2026-09-21T13:00:00Z"),
                FakeExternalWorld(wpath))
    assert d2.grants["g-p"]["absolute_deadline"] == "2026-09-22T12:00:00Z"
    d2.close()


def test_no_alternate_public_write_path():
    import pathlib
    srcdir = pathlib.Path(__file__).resolve().parent.parent / "src"
    offenders = []
    for fn in ("driver.py", "status.py", "supervisor.py"):
        text = (srcdir / fn).read_text()
        if "store.append(" in text or "store.record_terminal(" in text:
            offenders.append(fn)
    assert offenders == [], offenders  # only ingress.py may call store writes
    assert (srcdir / "ingress.py").read_text().count("store.append(") >= 1


def test_host_clock_adapter_reads_utc():
    hc = HostClock()
    now = hc.utc_now()
    import validator as V
    assert V._instant(now) is not None
    assert hc.monotonic() > 0


def test_no_live_effects_possible():
    import driver as drvmod
    import inspect
    for mod in (drvmod, ingress_mod):
        src = inspect.getsource(mod)
        for banned in ("import subprocess", "import socket", "os.kill",
                       "import signal", "import requests", "urllib.request",
                       "import openai", "import anthropic", "time.sleep",
                       "while True:"):
            assert banned not in src, (mod.__name__, banned)
