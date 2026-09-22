"""P6-r13 amendment-1 (#11) producer/verifier independence (new core bytes).

Public trusted-ingress path only: real publish via Driver (producer kiln),
then same-principal verify as kiln/verifier. Records module __file__+hashes.
No Driver.verify-only proof (hardcodes corvid); no hand-seeded worker_seat.
"""
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NEWC = "/home/bmosher/memory-bake-off/campaign4/packages/" \
    "P6-r13-core-record-integrity/candidate/src/r3harness"
if NEWC not in sys.path:
    sys.path.insert(0, NEWC)

import lifecycle as LC
import store as STOREMOD
from driver import Driver, FakeClock, FakeExternalWorld

Q = "R13I"
KILN_W = {"seat": "kiln", "role": "worker"}
KILN_V = {"seat": "kiln", "role": "verifier"}
CORVID_V = {"seat": "corvid", "role": "verifier"}
DIR = {"seat": "tern", "role": "director"}
DISP = {"kind": "question_answered", "decision_ref": "t-1", "reason": "ok",
        "evidence_refs": ["h"]}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_module_bytes_are_new_core():
    import driver as DRV
    import ingress as ING
    for mod in (DRV, LC, STOREMOD, ING):
        assert mod.__file__.startswith(NEWC), mod.__file__
    print("lifecycle=%s ingress=%s store=%s"
          % (sha(LC.__file__)[:12], sha(ING.__file__)[:12],
             sha(STOREMOD.__file__)[:12]))


def mk():
    tmp = tempfile.mkdtemp(prefix="r13i-")
    db = os.path.join(tmp, "ledger.db")
    world = os.path.join(tmp, "world.json")
    d = Driver(db, FakeClock(), FakeExternalWorld(world))
    d.tmp, d.db, d.worldpath = tmp, db, world
    return d


def published(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)
    d.publish_completion(Q, aid, {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": "2026-09-21T14:00:00Z"})


def vclaim(eid, typ="verify_pass", body=None):
    e = {"event_id": eid, "question_id": Q, "revision": 1, "type": typ}
    e.update(body or {"elapsed_s": 60, "pass_budget_s": 1800,
                      "finding": "positive"})
    return e


def counts(d):
    return (d.store.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            set(d.store.seen_events),
            d.store.revisions[(Q, 1)]["phase"])


def submit_verify(d, eid, actor, typ="verify_pass", atomic=None):
    aa = None if atomic is None or "hold" in atomic else dict(DIR)
    return d.ingress.append(vclaim(eid, typ), d.budget, atomic,
                           getattr(d, "grants", None), actor=dict(actor),
                           atomic_actor=aa)


def test_same_principal_verify_pass_and_fail_reject_before_mutation():
    # Atomic decide closes the verdict: on unfixed bytes the pair commits
    # to COMPLETE+disposition (old-fail); fixed bytes reject E_SELF_VERIFY
    # before any row/cache/state mutation.
    for typ in ("verify_pass", "verify_fail"):
        d = mk()
        try:
            published(d)
            before = counts(d)
            dec = {"event_id": "ev-self-d-%s" % typ, "question_id": Q,
                   "revision": 1, "type": "decide",
                   "at": "2026-09-21T12:10:00Z",
                   "disposition": dict(DISP)}
            try:
                submit_verify(d, "ev-self-%s" % typ, KILN_V, typ,
                              atomic={"decide": dec})
                raise AssertionError("same-principal %s accepted" % typ)
            except Exception as e:
                assert getattr(e, "code", "") == "E_SELF_VERIFY", \
                    getattr(e, "code", e)
            assert counts(d) == before  # zero row/cache/state change
            assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
        finally:
            try:
                d.close()
            except Exception:
                pass


def test_rejected_verdict_with_atomic_hold_decide_leaves_zero_writes():
    import datetime as _dt
    d = mk()
    try:
        published(d)
        before = counts(d)
        hold = (_dt.datetime(2026, 9, 21, 16, 0, 0)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        try:
            submit_verify(d, "ev-self-hold", KILN_V, "verify_pass",
                          atomic={"hold": hold})
            raise AssertionError("atomic hold on self-verify accepted")
        except Exception as e:
            assert getattr(e, "code", "") == "E_SELF_VERIFY", \
                getattr(e, "code", e)
        assert counts(d) == before
        dec = {"event_id": "ev-self-d", "question_id": Q, "revision": 1,
               "type": "decide", "at": "2026-09-21T12:10:00Z",
               "disposition": dict(DISP)}
        try:
            submit_verify(d, "ev-self-dec", KILN_V, "verify_pass",
                          atomic={"decide": dec})
            raise AssertionError("atomic decide on self-verify accepted")
        except Exception as e:
            assert getattr(e, "code", "") == "E_SELF_VERIFY", \
                getattr(e, "code", e)
        assert counts(d) == before
    finally:
        try:
            d.close()
        except Exception:
            pass


def test_role_relabel_and_spoofed_worker_seat_do_not_defeat_rule():
    d = mk()
    try:
        published(d)
        # Same seat with a swapped/relabeled role still rejects.
        for actor in (dict(KILN_V), {"seat": "kiln", "role": "worker"},
                      {"seat": "kiln", "role": "director"}):
            submit = dict(vclaim("ev-swap-%s" % actor["role"]))
            try:
                if actor["role"] == "worker":
                    # worker role cannot emit verify at all: still rejected
                    d.ingress.append(submit, d.budget, None,
                                    getattr(d, "grants", None),
                                    actor=dict(actor),
                                    atomic_actor=dict(DIR))
                else:
                    submit_verify(d, "ev-swap-%s" % actor["role"], actor)
                raise AssertionError("relabeled %r accepted" % (actor,))
            except Exception as e:
                assert getattr(e, "code", "") in (
                    "E_SELF_VERIFY", "E_UNAUTHORIZED"), \
                    getattr(e, "code", e)
        # Adversarial publish-time worker_seat claim is ignored: a later
        # self-verify still fires on the true producer.
        d2 = mk()
        try:
            d2.admit_authorize(Q)
            d2.start_dispatch(Q, "a-w9", duration_s=3600)
            d2.acknowledge("a-w9")
            d2.publish_completion(Q, "a-w9", {"h": "x"},
                                 verify={"action_id": "a-v9",
                                         "owner": "corvid",
                                         "deadline":
                                         "2026-09-21T14:00:00Z"})
            assert d2.store.revisions[(Q, 1)]["producer_seat"] == "kiln"
            try:
                d2.ingress.append(
                    vclaim("ev-spoof"), d2.budget, None,
                    getattr(d2, "grants", None), actor=dict(KILN_V),
                    atomic_actor=dict(DIR))
                raise AssertionError("spoofed self-verify accepted")
            except Exception as e:
                assert getattr(e, "code", "") == "E_SELF_VERIFY", \
                    getattr(e, "code", e)
        finally:
            try:
                d2.close()
            except Exception:
                pass
    finally:
        try:
            d.close()
        except Exception:
            pass


def test_distinct_verifier_still_completes_with_disposition():
    d = mk()
    try:
        published(d)
        dec = {"event_id": "ev-legit-d", "question_id": Q, "revision": 1,
               "type": "decide", "at": "2026-09-21T12:10:00Z",
               "disposition": dict(DISP)}
        d.ingress.append(vclaim("ev-legit-v"), d.budget,
                         {"decide": dec}, getattr(d, "grants", None),
                         actor=dict(CORVID_V), atomic_actor=dict(DIR))
        rev = d.store.revisions[(Q, 1)]
        assert rev["phase"] == "COMPLETE", rev["phase"]
        assert rev["disposition"]["reason"] == "ok"
    finally:
        try:
            d.close()
        except Exception:
            pass


def test_reopen_preserves_producer_and_rejection():
    from store import Store
    d = mk()
    try:
        published(d)
        d.store.close()
        s2 = Store(d.db)
        try:
            assert s2.revisions[(Q, 1)]["producer_seat"] == "kiln"
            base = s2.revisions[(Q, 1)]
            try:
                LC.apply(dict(base),
                         {"event_id": "ev-re", "question_id": Q,
                          "revision": 1, "type": "verify_pass",
                          "actor": dict(KILN_V), "at": "2026-09-21T12:10:00Z",
                          "elapsed_s": 60, "pass_budget_s": 1800,
                          "finding": "positive"},
                         "2026-09-21T12:10:00Z",
                         {"attempts": 1, "repairs": 1, "verifier_s": 1800})
                raise AssertionError("replayed self-verify accepted")
            except LC.TransitionError as e:
                assert e.code == "E_SELF_VERIFY", e.code
        finally:
            s2.close()
    finally:
        try:
            d.close()
        except Exception:
            pass


def test_missing_producer_provenance_fails_closed_internal():
    # INTERNAL supplement: a CHECKING state with no bound producer (e.g.
    # pre-fix ledger shape that replay cannot recover) refuses verdict
    # with an owned explicit error instead of silently allowing it.
    st = LC.new_revision(Q)
    assert st["producer_seat"] is None
    st["phase"] = "CHECKING"
    budget = {"attempts": 1, "repairs": 1, "verifier_s": 1800}
    for actor in (dict(KILN_V), dict(CORVID_V)):
        try:
            LC.apply(dict(st),
                     {"event_id": "ev-mp", "question_id": Q, "revision": 1,
                      "type": "verify_pass", "actor": actor,
                      "at": "2026-09-21T12:10:00Z", "elapsed_s": 60,
                      "pass_budget_s": 1800, "finding": "positive"},
                     "2026-09-21T12:10:00Z", budget)
            raise AssertionError("verdict without producer accepted")
        except LC.TransitionError as e:
            assert e.code == "E_UNKNOWN_PRODUCER", e.code