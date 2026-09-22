"""P5 sole-repair tests: D1 attribution binding, D2 deadline authority,
D3 epoch uniqueness + ambiguous restart. Fresh tmp state; injected clocks."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld, ACTOR
import ingress as ingress_mod
from ingress import IngressError, Quarantined

Q = "P5R"
FAR = "2099-01-01T00:00:00Z"


def mk(clock=None):
    tmp = tempfile.mkdtemp(prefix="p5r-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), clock or FakeClock(), w)
    d.tmp = tmp
    return d


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


def reopen(d, now):
    db = d.store.path
    wpath = os.path.join(d.tmp, "world.json")
    d.close()
    return Driver(db, FakeClock(now), FakeExternalWorld(wpath))


# --- D1: caller attribution never chooses authority --------------------------
def test_d1_raw_admit_caller_actor_rejected():
    d = mk()
    raw = {"event_id": "fx-admit", "question_id": Q, "revision": 1,
           "type": "admit", "actor": {"seat": "kiln", "role": "reader"}}
    try:
        d.ingress.append(raw, d.budget, grants=d.grants,
                         actor={"seat": "corvid", "role": "reader"})
        assert False, "expected E_FORGED_ATTRIBUTION"
    except IngressError as e:
        assert e.code == "E_FORGED_ATTRIBUTION" and e.owner == "tern", e
    assert (Q, 1) not in d.store.revisions  # nothing persisted
    d.close()


def test_d1_forged_director_claim_rejected_trusted_context_wins():
    d = mk()
    running(d)
    forged = {"event_id": "fx-dec", "question_id": Q, "revision": 1,
              "type": "decide", "actor": {"seat": "tern", "role": "director"},
              "disposition": {"kind": "budget_spent", "decision_ref": "x",
                              "reason": "forged", "allocation_ref": "a"}}
    try:
        d.ingress.append(forged, d.budget, grants=d.grants,
                         actor={"seat": "corvid", "role": "reader"})
        assert False, "expected E_FORGED_ATTRIBUTION"
    except IngressError as e:
        assert e.code == "E_FORGED_ATTRIBUTION", e
    # Same claim through the supported route binds the trusted context.
    d.publish_completion(Q, "a-w1", {"h": "x"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": "2026-09-21T14:00:00Z"})
    d.verify(Q, "ev-f", True)
    ok = {"event_id": "fx-dec2", "question_id": Q, "revision": 1,
          "type": "decide",
          "disposition": {"kind": "question_answered", "decision_ref": "t",
                          "reason": "ok", "evidence_refs": ["h"]}}
    d.ingress.append(ok, d.budget, grants=d.grants,
                     actor={"seat": "tern", "role": "director"})
    import json
    body = json.loads(d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='fx-dec2'").fetchone()[0])
    assert body["receipt"]["epoch"] == d.ingress.epoch
    d.close()


def test_d1_terminal_subevent_actor_rejected():
    d = mk()
    running(d)
    v = {"event_id": "fx-v", "question_id": Q, "revision": 1,
         "type": "verify_fail", "actor": {"seat": "corvid",
                                          "role": "verifier"},
         "elapsed_s": 60, "pass_budget_s": 1800, "finding": "bad"}
    dd = {"event_id": "fx-d", "question_id": Q, "revision": 1, "type": "decide",
          "disposition": {"kind": "budget_spent", "decision_ref": "t",
                          "reason": "r", "allocation_ref": "a"}}
    try:
        d.ingress.record_terminal(
            v, dd, d.budget, grants=d.grants,
            actor_v={"seat": "corvid", "role": "verifier"},
            actor_d={"seat": "tern", "role": "director"})
        assert False, "expected E_FORGED_ATTRIBUTION"
    except IngressError as e:
        assert e.code == "E_FORGED_ATTRIBUTION", e
    d.close()


def test_d1_atomic_decide_needs_trusted_actor():
    d = mk()
    running(d)
    base = {"event_id": "fx-a", "question_id": Q, "revision": 1,
            "type": "verify_fail", "elapsed_s": 60, "pass_budget_s": 1800,
            "finding": "bad"}
    sub = {"event_id": "fx-a-dec", "type": "decide",
           "actor": {"seat": "tern", "role": "director"},
           "disposition": {"kind": "budget_spent", "decision_ref": "t",
                           "reason": "r", "allocation_ref": "a"}}
    try:
        d.ingress.append(dict(base), d.budget,
                         atomic={"decide": sub}, grants=d.grants,
                         actor={"seat": "corvid", "role": "verifier"})
        assert False, "expected E_FORGED_ATTRIBUTION"
    except IngressError as e:
        assert e.code == "E_FORGED_ATTRIBUTION", e
    d.close()


def test_d1_untrusted_actor_context_rejected():
    d = mk()
    d.admit_authorize(Q)
    ev = {"event_id": "fx-u", "question_id": Q, "revision": 1, "type": "start",
          "action_id": "a-u", "duration_s": 60}
    try:
        d.ingress.append(ev, d.budget, grants=d.grants,
                         actor={"seat": "mallory", "role": "director"})
        assert False, "expected E_UNTRUSTED_ACTOR"
    except IngressError as e:
        assert e.code == "E_UNTRUSTED_ACTOR", e
    d.close()


def test_d1_every_public_path_persists_bound_actor():
    import json
    d = mk()
    d.admit_authorize(Q)
    d.start_dispatch(Q, "a-w1", duration_s=3600)
    for eid, seat, role in (("P5R-admit", "corvid", "reader"),
                            ("a-w1-start", "cairn", "duty")):
        body = json.loads(d.store.conn.execute(
            "SELECT body FROM events WHERE event_id=?", (eid,)).fetchone()[0])
        assert body["receipt"]["recorded_at"] is not None
        row = d.store.conn.execute(
            "SELECT actor_seat, actor_role FROM events WHERE event_id=?",
            (eid,)).fetchone()
        assert row == (seat, role), (eid, row)
    d.close()


# --- D2: every new deadline derived/checked -----------------------------------
def test_d2_grantless_2099_verifier_deadline_rejected():
    d = mk()
    running(d)
    try:
        d.publish_completion(
            Q, "a-w1", {"h": "x"},
            verify={"action_id": "a-v1", "owner": "corvid", "deadline": FAR},
            eid="pub-far")
        assert False, "expected E_DEADLINE_UNAUTHORIZED"
    except IngressError as e:
        assert e.code == "E_DEADLINE_UNAUTHORIZED", e
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"
    d.close()


def test_d2_checking_grant_cannot_authorize_running_start():
    d = mk()
    d.admit_authorize(Q)
    d.pin_grant("g-chk", "2026-09-21T18:00:00Z", phase="verify")
    try:
        d.start_dispatch(Q, "a-w1", grant_ref="g-chk")
        assert False, "expected E_GRANT_MISMATCH"
    except IngressError as e:
        assert e.code == "E_GRANT_MISMATCH", e
    d.close()


def test_d2_nested_handoff_grant_routes():
    d = mk()
    running(d)
    try:
        d.publish_completion(
            Q, "a-w1", {"h": "x"}, eid="pub-hfar",
            handoff={"handoff_deadline": FAR, "handoff_owner": "duty"})
        assert False, "expected E_DEADLINE_UNAUTHORIZED"
    except IngressError as e:
        assert e.code == "E_DEADLINE_UNAUTHORIZED", e
    d.pin_grant("g-ho", FAR, phase="handoff")
    d.publish_completion(
        Q, "a-w1", {"h": "x"}, eid="pub-hok",
        handoff={"handoff_deadline": FAR, "handoff_owner": "duty"},
        handoff_grant_ref="g-ho")  # covered distant handoff: valid
    d.close()


def test_d2_nested_grant_cover_accepted():
    import json
    d = mk()
    running(d)
    d.pin_grant("g-v", FAR, phase="verify")
    ev = d._ev("pub-vok", Q, "publish", "worker",
               {"artifact_hashes": {"h": "x"},
                "verify": {"action_id": "a-v1", "owner": "corvid",
                           "deadline": FAR},
                "verify_grant_ref": "g-v"})
    d._submit(ev, "worker")  # distant deadline covered by a real grant: valid
    body = json.loads(d.store.conn.execute(
        "SELECT body FROM events WHERE event_id='pub-vok'").fetchone()[0])
    assert body["verify"]["deadline"] == FAR
    d.close()


def test_d2_start_needs_explicit_authorization():
    d = mk()
    d.admit_authorize(Q)
    try:
        d.start_dispatch(Q, "a-w1")  # no duration, no grant: no fallback
        assert False, "expected E_NO_AUTHORIZATION"
    except IngressError as e:
        assert e.code == "E_NO_AUTHORIZATION", e
    d.close()


def test_d2_actual_phase_not_hints():
    d = mk()
    d.admit_authorize(Q)  # REGISTERED, never started
    try:
        d.publish_completion(Q, "a-w1", {"h": "x"},
                             verify={"action_id": "a-v1", "owner": "corvid",
                                     "deadline": "2026-09-21T14:00:00Z"})
        assert False, "expected E_PHASE_MISMATCH"
    except IngressError as e:
        assert e.code == "E_PHASE_MISMATCH", e
    d.close()


# --- D3: unique epochs, ambiguous restart --------------------------------------
def test_d3_new_epoch_per_lifetime():
    d = mk()
    e1 = d.ingress.epoch
    d2 = reopen(d, "2026-09-21T12:00:00Z")  # identical clock values
    assert d2.ingress.epoch != e1  # genuinely new, never reproduced
    d2.close()


def test_d3_backward_utc_needs_bounded_reconcile():
    d = mk()
    running(d)
    d2 = reopen(d, "2026-09-21T11:00:00Z")  # wall went backward
    try:
        d2.on_deadline("a-w1", Q)
        # on_deadline authority: now < deadline -> early no-op BEFORE write?
        # The interrupt write itself must quarantine; force a direct write:
        d2._submit(d2._ev("fx-bw", Q, "interrupt", "duty", {"reason": "x"}),
                   "duty")
        assert False, "expected E_AMBIGUOUS_RESTART"
    except Quarantined as e:
        assert e.code == "E_AMBIGUOUS_RESTART", e
        assert e.evidence["owner"] == "cairn"
    dl_before = d2.store.revisions[(Q, 1)]["flight"]["deadline"]
    d2.ingress.reconcile_clock("operator confirms clock restore",
                               owner="cairn")
    d2._submit(d2._ev("fx-bw2", Q, "interrupt", "duty", {"reason": "x"}),
               "duty")  # writes resume after owned reconcile
    dl_after = d2.store.revisions[(Q, 1)]["flight"]["deadline"]
    assert dl_before == dl_after == "2026-09-21T13:00:00Z"  # never extended
    d2.close()


def test_d3_cross_process_mono_never_compared():
    d = mk()
    running(d)
    d2 = reopen(d, "2026-09-21T12:30:00Z")
    d2.clock._mono = 999999.0  # wild cross-process value: must not matter
    d2._submit(d2._ev("fx-m", Q, "interrupt", "duty", {"reason": "x"}),
               "duty")  # proceeds; no spurious discontinuity
    d2.close()
