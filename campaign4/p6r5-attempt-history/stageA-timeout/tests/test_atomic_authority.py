"""P5-r2 atomic authority: one unambiguous validation/stamping path per
atomic op. Mixed/malformed rejected before mutation; genuine hold and both
genuine decide forms preserved; no partial rows."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from ingress import IngressError, Quarantined

Q = "P5X"
DL_V = "2026-09-21T14:00:00Z"
HOLD = "2026-09-21T15:00:00Z"
DISP = {"kind": "question_answered", "decision_ref": "t-1",
        "reason": "atomic ok", "evidence_refs": ["h"]}
VER = {"seat": "corvid", "role": "verifier"}
DIR = {"seat": "tern", "role": "director"}


def mk():
    tmp = tempfile.mkdtemp(prefix="p5x-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d


def checking(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)
    d.publish_completion(Q, aid, {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})


def verdict_eid(n):
    return {"event_id": "mx-v%d" % n, "question_id": Q, "revision": 1,
            "type": "verify_pass", "elapsed_s": 60, "pass_budget_s": 1800,
            "finding": "positive"}


def decide_sub(n, **kw):
    sub = {"event_id": "mx-d%d" % n, "question_id": Q, "revision": 1,
           "type": "decide", "disposition": dict(DISP)}
    sub.update(kw)
    return sub


def count(d):
    return d.store.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]


def test_mixed_both_orders_rejected_pre_mutation():
    for n, atomic in (
            (1, {"hold": HOLD, "decide": decide_sub(1)}),
            (2, {"decide": decide_sub(2), "hold": HOLD})):
        d = mk()
        checking(d)
        before = count(d)
        try:
            d.ingress.append(verdict_eid(n), d.budget, atomic=atomic,
                             grants=d.grants, actor=dict(VER))
            assert False, "expected E_MIXED_ATOMIC"
        except IngressError as e:
            assert e.code == "E_MIXED_ATOMIC", e
        assert count(d) == before  # neither event persisted
        assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
        d.close()


def test_mixed_forged_sub_rejected_no_rows():
    d = mk()
    checking(d)
    before = count(d)
    sub = decide_sub(1, actor={"seat": "kiln", "role": "director"},
                     at="2099-01-01T00:00:00Z")
    try:
        d.ingress.append(verdict_eid(1), d.budget,
                         atomic={"hold": HOLD, "decide": sub},
                         grants=d.grants, actor=dict(VER))
        assert False, "expected rejection"
    except IngressError as e:
        assert e.code in ("E_MIXED_ATOMIC", "E_FORGED_ATTRIBUTION"), e
    assert count(d) == before
    for eid in ("mx-v1", "mx-d1"):
        assert d.store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id=?",
            (eid,)).fetchone()[0] == 0
    d.close()


def test_atomic_schema_variants_rejected():
    d = mk()
    checking(d)
    cases = [
        ({}, "empty form"),
        ({"freeze": 1}, "unknown key"),
        ({"hold": HOLD, "melt": 1}, "hold plus unknown key"),
        ("hold", "non-dict string"),
        (["decide"], "non-dict list"),
        ({"hold": "not-a-time"}, "malformed hold value"),
        ({"hold": "2099-01-01T00:00:00Z"}, "unauthorized hold deadline"),
        ({"decide": "x"}, "non-dict decide"),
        ({"decide": decide_sub(9)}, "missing trusted actor"),
    ]
    for n, (atomic, _label) in enumerate(cases):
        before = count(d)
        try:
            d.ingress.append(verdict_eid(100 + n), d.budget, atomic=atomic,
                             grants=d.grants, actor=dict(VER))
            assert False, "expected rejection for %r" % (atomic,)
        except IngressError as e:
            assert e.code in ("E_BAD_ATOMIC", "E_MIXED_ATOMIC",
                              "E_BAD_DEADLINE", "E_DEADLINE_UNAUTHORIZED",
                              "E_UNTRUSTED_ACTOR"), (atomic, e.code)
        assert count(d) == before
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()


def test_forged_sub_receipt_and_time_rejected():
    d = mk()
    checking(d)
    for n, (extra, label) in enumerate((
            ({"receipt": {"recorded_at": "x"}}, "receipt"),
            ({"recorded_at": "2026-09-21T12:00:00Z"}, "time"),
            ({"actor": dict(DIR)}, "actor"))):
        before = count(d)
        sub = decide_sub(20 + n, **extra)
        try:
            d.ingress.append(verdict_eid(20 + n), d.budget,
                             atomic={"decide": sub}, grants=d.grants,
                             actor=dict(VER), atomic_actor=dict(DIR))
            assert False, "expected rejection for " + label
        except IngressError as e:
            assert e.code in ("E_FORGED_ATTRIBUTION", "E_FORGED_RECEIPT",
                              "E_UNTRUSTED_ACTOR"), e
        assert count(d) == before
    d.close()


def test_genuine_hold_preserved_with_owned_task():
    d = mk()
    checking(d)
    out, dup = d.ingress.append(
        verdict_eid(30), d.budget, atomic={"hold": HOLD}, grants=d.grants,
        actor=dict(VER))
    assert dup is False
    rec = d.store.revisions[(Q, 1)]
    assert rec["phase"] == "COMPLETE"  # held terminal, verdict committed
    assert (rec.get("decision_task") or {}).get("owner") == "director"
    snap = d.snapshot(__import__("os").path.join(d.tmp, "s.json"))
    tasks = [i for i in snap["in_flight"] if i.get("phase") == "DECISION"]
    assert len(tasks) == 1 and tasks[0]["owner"] == "tern"  # owned task
    d.close()


def test_genuine_decide_forms_still_commit():
    import os
    for n, form in enumerate(("terminal", "atomic")):
        d = mk()
        checking(d)
        if form == "terminal":
            d.terminal_close(
                Q, "gx-v%d" % n, "gx-d%d" % n,
                {"type": "verify_pass", "who": "verifier",
                 "body": {"elapsed_s": 60, "pass_budget_s": 1800}},
                dict(DISP))
        else:
            d.ingress.append(
                dict(verdict_eid(n), event_id="gx-v%d" % n), d.budget,
                atomic={"decide": decide_sub(n, event_id="gx-d%d" % n)},
                grants=d.grants, actor=dict(VER),
                atomic_actor=dict(DIR))
        rec = d.store.revisions[(Q, 1)]
        assert rec["phase"] == "COMPLETE" and rec["disposition"]["kind"] == \
            "question_answered", form
        for eid in ("gx-v%d" % n, "gx-d%d" % n):
            body = json.loads(d.store.conn.execute(
                "SELECT body FROM events WHERE event_id=?",
                (eid,)).fetchone()[0])
            assert body["_trusted"] is True and \
                body["receipt"]["recorded_at"] is not None, (form, eid)
        db, wpath = d.store.path, os.path.join(d.tmp, "world.json")
        d.close()
        d2 = Driver(db, FakeClock(), FakeExternalWorld(wpath))
        assert d2.store.revisions[(Q, 1)]["disposition"]["kind"] == \
            "question_answered", form  # reopen preserves history
        d2.close()
