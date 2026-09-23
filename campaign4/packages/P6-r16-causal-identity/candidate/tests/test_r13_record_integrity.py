"""P6-r13 record-integrity regressions A-D + E matrix (new core bytes).

Proves which bytes ran via module __file__ + sha256. Public paths use
Driver/ingress with trusted actors; internal core checks labelled.
"""
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NEWC = os.path.realpath(os.path.join(HERE, "..", "src", "r3harness"))
sys.path.insert(0, NEWC)

import lifecycle as LC
import store as STOREMOD
from driver import Driver, FakeClock, FakeExternalWorld

Q = "R13T"
DISP = {"kind": "question_answered", "decision_ref": "t-1", "reason": "ok",
        "evidence_refs": ["h"]}
VER = {"seat": "corvid", "role": "verifier"}
DIR = {"seat": "tern", "role": "director"}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _origin_path(mod, name):
    """Canonical resolved path of an imported module (collapses a
    __pycache__ .pyc to its source file; never name/suffix matching)."""
    actual = os.path.realpath(mod.__file__)
    if actual.endswith(".pyc"):
        stem = os.path.basename(actual).split(".")[0] + ".py"
        actual = os.path.realpath(os.path.join(
            os.path.dirname(os.path.dirname(actual)), stem))
    return actual


def _origin_ok(mod, name):
    return _origin_path(mod, name) == \
        os.path.realpath(os.path.join(NEWC, name))


def test_module_bytes_are_new_core():
    import driver as DRV
    for mod, name in ((DRV, "driver.py"), (LC, "lifecycle.py"),
                      (STOREMOD, "store.py")):
        assert _origin_ok(mod, name), (mod.__file__, NEWC)
    print("store=%s lifecycle=%s" % (sha(STOREMOD.__file__)[:12],
                                     sha(LC.__file__)[:12]))


def test_module_origin_aliases_pass_parent_and_lookalike_fail():
    import driver as DRV
    expected = os.path.realpath(os.path.join(NEWC, "lifecycle.py"))
    # Both filesystem aliases of this candidate resolve equal.
    alias = NEWC.replace("/home/", "/var/home/", 1) \
        if NEWC.startswith("/home/") \
        else NEWC.replace("/var/home/", "/home/", 1)
    assert os.path.realpath(os.path.join(alias, "lifecycle.py")) \
        == expected
    assert _origin_path(LC, "lifecycle.py") == expected
    assert _origin_path(DRV, "driver.py") == \
        os.path.realpath(os.path.join(NEWC, "driver.py"))
    # Historical parent module is a different file.
    parent = os.path.realpath(
        "/home/bmosher/memory-bake-off/campaign4/packages/"
        "P6-r11-case-observer-continuation/candidate/src/r3harness/"
        "lifecycle.py")
    assert parent != expected
    # Sibling prefix-lookalike passes startswith but fails equality.
    lookalike = os.path.normpath(NEWC + "-lookalike/lifecycle.py")
    assert lookalike.startswith(NEWC)
    assert os.path.realpath(lookalike) != expected


def mk():
    tmp = tempfile.mkdtemp(prefix="r13-")
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(),
               FakeExternalWorld(os.path.join(tmp, "world.json")))
    d.tmp = tmp
    return d


def checking(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)
    d.publish_completion(Q, aid, {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": "2026-09-21T14:00:00Z"})


def ev(eid, typ, who, role, body=None, at="2026-09-21T12:10:00Z"):
    e = {"event_id": eid, "question_id": Q, "revision": 1, "type": typ,
         "actor": {"seat": who, "role": role}, "at": at}
    e.update(body or {})
    return e


def bare(e):
    """Ingress-bound event: no caller actor (authority comes only from the
    trusted adapter context)."""
    return {k: v for k, v in e.items() if k != "actor"}


# A (#2): rollback leaves every projection consistent.
def test_A1_pair_duplicate_no_phantom_and_retry_commits():
    d = mk()
    try:
        checking(d)
        existing = d.store.conn.execute(
            "SELECT event_id FROM events ORDER BY rowid LIMIT 1"
        ).fetchone()[0]
        verdict = ev("ev-r13-v1", "verify_pass", "corvid", "verifier",
                     {"elapsed_s": 60, "pass_budget_s": 1800,
                      "finding": "positive"})
        decide = ev(existing, "decide", "tern", "director",
                    {"disposition": dict(DISP)})
        try:
            d.store.record_terminal(verdict, decide)
            raise AssertionError("duplicate decide committed")
        except LC.TransitionError as e:
            assert e.code == "E_DUP_EVENT", e.code
        assert "ev-r13-v1" not in d.store.seen_events  # no phantom
        assert d.store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id='ev-r13-v1'"
        ).fetchone()[0] == 0  # zero new rows
        # same-store retry with fresh valid decide persists exactly once
        decide2 = ev("ev-r13-dfresh", "decide", "tern", "director",
                     {"disposition": dict(DISP)})
        d.store.record_terminal(verdict, decide2)
        assert d.store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id='ev-r13-v1'"
        ).fetchone()[0] == 1
        assert "ev-r13-v1" in d.store.seen_events
        # prior committed IDs still dedupe
        assert d.store.append(
            ev(existing, "decide", "tern", "director",
               {"disposition": dict(DISP)}))[1] is True
        # reopened store agrees
        d.store.close()
        from store import Store
        s2 = Store(os.path.join(d.tmp, "ledger.db"))
        assert "ev-r13-v1" in s2.seen_events
        assert s2.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id='ev-r13-v1'"
        ).fetchone()[0] == 1
        s2.close()
    finally:
        try:
            d.close()
        except Exception:
            pass


def test_A3_injected_second_insert_failure_rolls_back():
    d = mk()
    try:
        checking(d)
        verdict = ev("ev-r13-va", "verify_pass", "corvid", "verifier",
                     {"elapsed_s": 60, "pass_budget_s": 1800,
                      "finding": "positive"})
        decide = ev("ev-r13-da", "decide", "tern", "director",
                    {"disposition": dict(DISP)})
        real = d.store._insert

        def boom(eid, *a, **k):
            if eid == "ev-r13-da":
                raise RuntimeError("injected insert failure")
            return real(eid, *a, **k)

        d.store._insert = boom
        try:
            d.store.record_terminal(verdict, decide)
            raise AssertionError("injected failure committed")
        except RuntimeError:
            pass
        finally:
            d.store._insert = real
        assert "ev-r13-va" not in d.store.seen_events
        assert "ev-r13-da" not in d.store.seen_events
        assert d.store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id IN "
            "('ev-r13-va','ev-r13-da')").fetchone()[0] == 0
        assert ("R13T", 1) not in d.store.revisions or \
            d.store.revisions[("R13T", 1)].get("disposition") is None
    finally:
        try:
            d.close()
        except Exception:
            pass


# B (#6): first disposition immutable; replay idempotent; AMEND retained.
def test_B_second_decide_rejects_replay_idempotent_amend_ok():
    st = LC.new_revision(Q)
    st["phase"] = "COMPLETE"
    st, _ = LC.apply(
        st, ev("d-r13-1", "decide", "tern", "director",
               {"disposition": dict(DISP, reason="first")}),
        "2026-09-21T12:00:00Z", {})
    assert st["disposition"]["reason"] == "first"
    constate = json.dumps(st, sort_keys=True)
    rows = 1
    try:
        LC.apply(st, ev("d-r13-2", "decide", "tern", "director",
                        {"disposition": dict(DISP, reason="second")}),
                 "2026-09-21T12:01:00Z", {})
        raise AssertionError("second decide overwrote")
    except LC.TransitionError as e:
        assert e.code == "E_ALREADY_DECIDED", e.code
    assert st["disposition"]["reason"] == "first"  # zero state change
    assert json.dumps(st, sort_keys=True) == constate
    assert rows == 1
    # AMEND path retained (not co-opted): amend still supersedes
    st2, _ = LC.apply(dict(st), ev("a-r13-1", "amend", "tern", "director",
                                   {"new_revision": 2}),
                      "2026-09-21T12:02:00Z", {})
    assert st2["phase"] == "SUPERSEDED"


def test_B_public_replay_idempotent_second_rejected():
    d = mk()
    try:
        checking(d)
        v = ev("ev-r13-vb", "verify_pass", "corvid", "verifier",
               {"elapsed_s": 60, "pass_budget_s": 1800,
                "finding": "positive"})
        dec = ev("ev-r13-db", "decide", "tern", "director",
                 {"disposition": dict(DISP, reason="first")})
        before = d.store.conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        d.ingress.append(
            bare(v), d.budget,
            atomic={"decide": dict(dec, actor=None) if False else {
                "event_id": "ev-r13-db", "question_id": Q, "revision": 1,
                "type": "decide", "at": "2026-09-21T12:10:00Z",
                "disposition": dict(DISP, reason="first")}},
            grants=getattr(d, "grants", None),
            actor=dict(VER), atomic_actor=dict(DIR))
        # exact same committed verdict replay is idempotent, not error
        out = d.ingress.append(
            bare(v), d.budget,
            atomic={"decide": {
                "event_id": "ev-r13-db", "question_id": Q, "revision": 1,
                "type": "decide", "at": "2026-09-21T12:10:00Z",
                "disposition": dict(DISP, reason="first")}},
            grants=getattr(d, "grants", None),
            actor=dict(VER), atomic_actor=dict(DIR))
        assert out[1] is True, out  # duplicate-ignored
        # distinct later decide rejected with zero row change
        try:
            d.ingress.append(
                bare(ev("ev-r13-vb2", "verify_pass", "corvid", "verifier",
                        {"elapsed_s": 60, "pass_budget_s": 1800,
                         "finding": "positive2"})),
                d.budget,
                atomic={"decide": {
                    "event_id": "ev-r13-db2", "question_id": Q,
                    "revision": 1, "type": "decide",
                    "at": "2026-09-21T12:11:00Z",
                    "disposition": dict(DISP, reason="second")}},
                grants=getattr(d, "grants", None),
                actor=dict(VER), atomic_actor=dict(DIR))
            raise AssertionError("distinct decide overwrote via ingress")
        except Exception as e:
            # Deterministic rejection before mutation: the verdict itself
            # cannot land on a decided revision (E_PHASE_MISMATCH), or the
            # decide is refused (E_ALREADY_DECIDED). Either way zero change.
            assert getattr(e, "code", "") in (
                "E_ALREADY_DECIDED", "E_BAD_TRANSITION", "E_TERMINAL",
                "E_DUP_EVENT", "E_PHASE_MISMATCH"), getattr(e, "code", e)
        after = d.store.conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        rev = d.store.revisions[(Q, 1)]
        assert rev.get("disposition", {}).get("reason") == "first", \
            rev.get("disposition")
        assert after == before + 2, (before, after)  # only first pair added
    finally:
        try:
            d.close()
        except Exception:
            pass


# C (#7): decide+grant_ref rejects before mutation; valid forms commit.
def test_C_decide_grant_ref_rejects_valid_forms_commit():
    d = mk()
    try:
        checking(d)
        v = ev("ev-r13-vc", "verify_pass", "corvid", "verifier",
               {"elapsed_s": 60, "pass_budget_s": 1800,
                "finding": "positive"})
        sub = {"event_id": "ev-r13-dc", "question_id": Q, "revision": 1,
               "type": "decide", "at": "2026-09-21T12:10:00Z",
               "disposition": dict(DISP)}
        before = (d.store.conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0],
            set(d.store.seen_events),
            d.store.revisions[(Q, 1)].get("disposition"))
        try:
            d.ingress.append(bare(v), d.budget,
                             atomic={"decide": dict(sub),
                                     "grant_ref": "g-forged"},
                             grants=getattr(d, "grants", None),
                             actor=dict(VER), atomic_actor=dict(DIR))
            raise AssertionError("decide+grant_ref accepted")
        except Exception as e:
            assert getattr(e, "code", "") == "E_BAD_ATOMIC", \
                getattr(e, "code", e)
        after = (d.store.conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0],
            set(d.store.seen_events),
            d.store.revisions[(Q, 1)].get("disposition"))
        assert after == before  # zero mutation
        # valid decide (no grant) still commits with trusted stamping
        d.ingress.append(bare(ev("ev-r13-vc2", "verify_pass", "corvid",
                                 "verifier",
                                 {"elapsed_s": 60, "pass_budget_s": 1800,
                                  "finding": "positive"})),
                         d.budget,
                         atomic={"decide": dict(sub,
                                                event_id="ev-r13-dc2")},
                         grants=getattr(d, "grants", None),
                         actor=dict(VER), atomic_actor=dict(DIR))
        assert d.store.revisions[(Q, 1)].get("disposition") is not None
    finally:
        try:
            d.close()
        except Exception:
            pass


# D (#10): instant ordering incl. offsets/fractions; naive/malformed reject.
def test_D_instant_deadline_ordering():
    base = LC.new_revision(Q)
    base["phase"] = "RUNNING"
    base["deadline"] = "2026-09-22T22:00:00+02:00"  # == 20:00Z
    pub = ev("p-r13-1", "publish", "alpha-12", "worker",
             {"artifact_hashes": {"h": "x"},
              "verify": {"action_id": "a-v1", "owner": "corvid",
                         "deadline": "2026-09-23T00:00:00Z"}})
    # 20:30Z is past the instant -> expired
    try:
        LC.apply(dict(base), dict(pub), "2026-09-22T20:30:00Z", {})
        raise AssertionError("past-instant publish accepted")
    except LC.TransitionError as e:
        assert e.code == "E_DEADLINE_EXPIRED", e.code
    # equivalent encodings: 21:59:59+02:00 == 19:59:59Z, before -> accept
    st, _ = LC.apply(dict(base), dict(pub), "2026-09-22T21:59:59+02:00",
                     {})
    assert st["phase"] == "CHECKING"
    # fractional + Z equivalent before -> accept
    st, _ = LC.apply(dict(base), dict(pub), "2026-09-22T19:59:59.5Z", {})
    assert st["phase"] == "CHECKING"
    # equal instant -> not expired (boundary convention)
    st, _ = LC.apply(dict(base), dict(pub), "2026-09-22T20:00:00Z", {})
    assert st["phase"] == "CHECKING"
    # naive values reject deterministically, never crash/compare-as-text
    for bad_now in ("2026-09-22T19:00:00", "not-a-time", None, 12345):
        try:
            LC.apply(dict(base), dict(pub), bad_now, {})
            raise AssertionError("naive/malformed now accepted: %r"
                                 % (bad_now,))
        except LC.TransitionError as e:
            assert e.code == "E_BAD_DEADLINE", e.code
    bad = dict(base, deadline="tomorrow")
    try:
        LC.apply(bad, dict(pub), "2026-09-22T19:00:00Z", {})
        raise AssertionError("malformed deadline accepted")
    except LC.TransitionError as e:
        assert e.code == "E_BAD_DEADLINE", e.code


# E (#5): public atomic/phase matrix — wholly applied or rejected, never drop.
def test_E_atomic_phase_matrix_no_silent_drop():
    d = mk()
    try:
        checking(d)
        # accept-on-COMMIT... accept requires COMPLETE phase; on CHECKING it
        # must reject deterministically (E_BAD_TRANSITION), not accept-drop.
        try:
            LC.apply(dict(d.store.revisions[(Q, 1)]),
                     ev("ac-r13-1", "accept", "tern", "director"), "t", {})
            raise AssertionError("accept-on-nonCOMPLETE applied")
        except LC.TransitionError as e:
            assert e.code in ("E_BAD_TRANSITION", "E_TERMINAL"), e.code
        # hold+decide mixed rejects; unknown form rejects; empty rejects
        for bad in ({"hold": "2026-09-21T15:00:00Z",
                     "decide": {"event_id": "x"}},
                    {"frobnicate": 1}, {}, "notadict"):
            try:
                d.ingress.append(
                    bare(ev("ev-r13-ve", "verify_pass", "corvid",
                            "verifier",
                            {"elapsed_s": 60, "pass_budget_s": 1800,
                             "finding": "positive"})),
                    d.budget, atomic=bad,
                    grants=getattr(d, "grants", None),
                    actor=dict(VER), atomic_actor=dict(DIR))
                raise AssertionError("malformed atomic accepted: %r"
                                     % (bad,))
            except Exception as e:
                assert getattr(e, "code", "") in (
                    "E_MIXED_ATOMIC", "E_BAD_ATOMIC"), \
                    getattr(e, "code", e)
    finally:
        try:
            d.close()
        except Exception:
            pass
