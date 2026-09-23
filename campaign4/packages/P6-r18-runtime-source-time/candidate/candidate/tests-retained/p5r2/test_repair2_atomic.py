"""P5 repair-2: atomic close ordering. Legitimate CHECKING verify_pass +
disposition commits terminal+disposition together (both API forms, incl
replay and reopen); invalid/forged pairs leave no partial writes; wrong
actor/receipt/time/grant still fail; standalone decide still gated."""
import json
import os
import sys
import tempfile

sys.path.insert(0, "/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/candidate/src/r3harness")  # ADAPTED P6-r13: exercise NEW core

from driver import Driver, FakeClock, FakeExternalWorld
from ingress import IngressError, Quarantined

Q = "P5T"
DL_V = "2026-09-21T14:00:00Z"
DISP = {"kind": "question_answered", "decision_ref": "t-1",
        "reason": "atomic ok", "evidence_refs": ["h"]}


def mk():
    tmp = tempfile.mkdtemp(prefix="p5t-")
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


def rows(d, eid):
    return d.store.conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_id=?", (eid,)).fetchone()[0]


def reopen(d, now="2026-09-21T12:30:00Z"):
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    return Driver(db, FakeClock(now), FakeExternalWorld(wpath))


# --- archived failure reproduced-then-fixed ----------------------------------
def test_archived_failure_now_commits_terminal_close():
    d = mk()
    checking(d)
    # Pre-repair this raised E_PHASE_MISMATCH and wrote neither event.
    d.terminal_close(
        Q, "ev-vp", "ev-dec",
        {"type": "verify_pass", "who": "verifier",
         "body": {"elapsed_s": 60, "pass_budget_s": 1800,
                  "finding": "positive"}},
        dict(DISP))
    rec = d.store.revisions[(Q, 1)]
    assert rec["phase"] == "COMPLETE" and rec["disposition"]["kind"] == \
        "question_answered"
    assert rows(d, "ev-vp") == 1 and rows(d, "ev-dec") == 1
    d.close()


def test_atomic_append_decide_form_commits_and_survives_reopen():
    d = mk()
    checking(d)
    v = {"event_id": "ev-va", "question_id": Q, "revision": 1,
         "type": "verify_pass", "elapsed_s": 60, "pass_budget_s": 1800,
         "finding": "positive"}
    sub = {"event_id": "ev-da", "question_id": Q, "revision": 1,
           "type": "decide", "disposition": dict(DISP)}
    d.ingress.append(v, d.budget, atomic={"decide": sub}, grants=d.grants,
                     actor={"seat": "corvid", "role": "verifier"},
                     atomic_actor={"seat": "tern", "role": "director"})
    rec = d.store.revisions[(Q, 1)]
    assert rec["phase"] == "COMPLETE" and rec["disposition"] is not None
    # Both subevents trusted-stamped with the same receipt instant.
    r1 = json.loads(d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='ev-va'").fetchone()[0])
    r2 = json.loads(d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='ev-da'").fetchone()[0])
    assert r1["receipt"]["recorded_at"] == r2["receipt"]["recorded_at"]
    assert r1["_trusted"] is True and r2["_trusted"] is True
    d2 = reopen(d)
    rec2 = d2.store.revisions[(Q, 1)]
    assert rec2["phase"] == "COMPLETE" and rec2["disposition"]["kind"] == \
        "question_answered"
    d2.close()


def test_atomic_replay_idempotent_both_forms():
    d = mk()
    checking(d)
    v = {"event_id": "ev-vr", "question_id": Q, "revision": 1,
         "type": "verify_pass", "elapsed_s": 60, "pass_budget_s": 1800,
         "finding": "positive"}
    sub = {"event_id": "ev-dr", "question_id": Q, "revision": 1,
           "type": "decide", "disposition": dict(DISP)}
    d.ingress.append(v, d.budget, atomic={"decide": sub}, grants=d.grants,
                     actor={"seat": "corvid", "role": "verifier"},
                     atomic_actor={"seat": "tern", "role": "director"})
    out, dup = d.ingress.append(
        dict(v), d.budget, atomic={"decide": dict(sub)}, grants=d.grants,
        actor={"seat": "corvid", "role": "verifier"},
        atomic_actor={"seat": "tern", "role": "director"})
    assert dup is True  # replay: no second terminal, no re-stamp
    assert rows(d, "ev-vr") == 1 and rows(d, "ev-dr") == 1
    d.close()


# --- invalid/forged pairs: no partial writes ----------------------------------
def test_invalid_disposition_leaves_both_rows_absent():
    d = mk()
    checking(d)
    try:
        d.terminal_close(
            Q, "ev-bad1", "ev-bad2",
            {"type": "verify_pass", "who": "verifier",
             "body": {"elapsed_s": 60, "pass_budget_s": 1800}},
            {"kind": "not-a-kind", "decision_ref": "x", "reason": "y"})
        assert False, "expected rejection"
    except Exception as e:
        assert "E_MISSING_DISPOSITION" in str(e), e
    assert rows(d, "ev-bad1") == 0 and rows(d, "ev-bad2") == 0
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"  # unchanged
    d.close()


def test_nonterminal_pair_rejected_without_writes():
    d = mk()
    checking(d)
    # verify_fail with eligible repair lands REPAIR_ALLOWED: a disposition
    # cannot ride along.
    v = {"event_id": "ev-nt", "question_id": Q, "revision": 1,
         "type": "verify_fail", "elapsed_s": 60, "pass_budget_s": 1800,
         "finding": "defect", "eligible_repair": True}
    sub = {"event_id": "ev-ntd", "question_id": Q, "revision": 1,
           "type": "decide", "disposition": dict(DISP)}
    try:
        d.ingress.append(v, d.budget, atomic={"decide": sub},
                         grants=d.grants,
                         actor={"seat": "corvid", "role": "verifier"},
                         atomic_actor={"seat": "tern", "role": "director"})
        assert False, "expected E_PHASE_MISMATCH"
    except IngressError as e:
        assert e.code == "E_PHASE_MISMATCH", e
    assert rows(d, "ev-nt") == 0 and rows(d, "ev-ntd") == 0
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()


def test_pair_revision_mismatch_rejected_without_writes():
    d = mk()
    checking(d)
    v = {"event_id": "ev-mm", "question_id": Q, "revision": 1,
         "type": "verify_pass", "elapsed_s": 60, "pass_budget_s": 1800}
    sub = {"event_id": "ev-mmd", "question_id": Q, "revision": 2,
           "type": "decide", "disposition": dict(DISP)}
    try:
        d.ingress.append(v, d.budget, atomic={"decide": sub},
                         grants=d.grants,
                         actor={"seat": "corvid", "role": "verifier"},
                         atomic_actor={"seat": "tern", "role": "director"})
        assert False, "expected E_BAD_ATOMIC"
    except IngressError as e:
        assert e.code == "E_BAD_ATOMIC", e
    assert rows(d, "ev-mm") == 0 and rows(d, "ev-mmd") == 0
    d.close()


def test_standalone_decide_from_checking_still_fails():
    d = mk()
    checking(d)
    ev = {"event_id": "fx-solo", "question_id": Q, "revision": 1,
          "type": "decide", "disposition": dict(DISP)}
    try:
        d.ingress.append(ev, d.budget, grants=d.grants,
                         actor={"seat": "tern", "role": "director"})
        assert False, "expected E_PHASE_MISMATCH"
    except IngressError as e:
        assert e.code == "E_PHASE_MISMATCH", e
    assert rows(d, "fx-solo") == 0
    d.close()


def test_atomic_wrong_actor_forged_receipt_still_fail():
    d = mk()
    checking(d)
    v = {"event_id": "ev-wa", "question_id": Q, "revision": 1,
         "type": "verify_pass", "elapsed_s": 60, "pass_budget_s": 1800,
         "actor": {"seat": "tern", "role": "director"}}
    sub = {"event_id": "ev-wad", "question_id": Q, "revision": 1,
           "type": "decide", "disposition": dict(DISP)}
    try:
        d.ingress.append(v, d.budget, atomic={"decide": sub},
                         grants=d.grants,
                         actor={"seat": "corvid", "role": "verifier"},
                         atomic_actor={"seat": "tern", "role": "director"})
        assert False, "expected E_FORGED_ATTRIBUTION"
    except IngressError as e:
        assert e.code == "E_FORGED_ATTRIBUTION", e
    v2 = dict(v, event_id="ev-wb")
    del v2["actor"]
    v2["recorded_at"] = "2026-09-21T12:00:00Z"
    try:
        d.ingress.append(v2, d.budget, atomic={"decide": dict(
            sub, event_id="ev-wbd")}, grants=d.grants,
            actor={"seat": "corvid", "role": "verifier"},
            atomic_actor={"seat": "tern", "role": "director"})
        assert False, "expected E_FORGED_RECEIPT"
    except IngressError as e:
        assert e.code == "E_FORGED_RECEIPT", e
    assert rows(d, "ev-wa") == 0 and rows(d, "ev-wb") == 0
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()
