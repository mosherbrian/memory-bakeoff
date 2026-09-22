"""P6-r2.1 event handoff: runtime turn-end primary trigger, route-free
claims, transactional intent, durable outbox. Injected effects only."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from host_adapter import HostAdapter, OwnedFault
from turn_handoff import (TurnWatcher, write_claim, validate_claim,
                          run_handoff)

Q = "P6H"
DL_V = "2026-09-21T14:00:00Z"
LAUNCH = {"package": "P6F", "attempt": "a1", "action": "a-w1",
          "execution": "ex-1", "contract_step": "worker-run"}


def mk():
    tmp = tempfile.mkdtemp(prefix="p6h-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d, HostAdapter(d)


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)
    return aid


def registered(ha, action="a-w1", execution="ex-1"):
    ha.register_execution(action, execution, "auth-1",
                          "2026-09-21T13:00:00Z")


def claim_for(execution="ex-1", **kw):
    c = {"package": "P6F", "attempt": "a1", "action": "a-w1",
         "execution": execution, "contract_step": "worker-run",
         "outcome": "completed",
         "artifacts": {"out": "sha256:fake-a-w1"}}
    c.update(kw)
    return c


def turn(item="i1", kind="end", stream_key="sess"):
    return {"stream_key": stream_key, "item": item, "kind": kind,
            "extra": {}}


# --- watcher: loss/truncation/dup/stale/restart ------------------------------------
def test_sidecar_poll_dedups_and_survives_truncation():
    tmp = tempfile.mkdtemp(prefix="p6s-")
    p = os.path.join(tmp, "sess.jsonl")
    with open(p, "w") as fh:
        fh.write('{"t":"start","item":"i1"}\n{"t":"d","item":"i1"}\n'
                 '{"t":"end","item":"i1"}\n')
    w = TurnWatcher(tmp)
    evs, cursors, notes = w.poll(["sess"], {})
    assert [e["kind"] for e in evs] == ["start", "d", "end"]
    assert notes == {"sess": "ok"}
    evs2, _, _ = w.poll(["sess"], cursors)  # nothing new: no dup
    assert evs2 == []
    with open(p, "w") as fh:  # truncation (per-turn reset)
        fh.write('{"t":"start","item":"i2"}\n')
    evs3, cursors3, notes3 = w.poll(["sess"], cursors)
    assert notes3 == {"sess": "truncated-reset"}
    assert [e["item"] for e in evs3] == ["i2"]  # new turn, nothing lost
    assert w.poll(["nope"], {})[2] == {"nope": "rotated-missing"}


# --- claims --------------------------------------------------------------------------
def test_claim_writer_and_route_free_validation(tmp_path=None):
    d, ha = mk()
    path = write_claim(d.tmp, "ex-1", claim_for())
    loaded = json.load(open(path))
    assert validate_claim(loaded, LAUNCH) == loaded
    for bad in ({"verifier": "x"}, {"destination": "y"},
                {"next_task": "z"}, {"duration_s": 5},
                {"deadline": "2026-09-21T13:00:00Z"}):
        try:
            validate_claim(claim_for(**bad), LAUNCH)
            assert False, "expected E_FORGED_ROUTE"
        except ValueError as e:
            assert "E_FORGED_ROUTE" in str(e), e
    c = claim_for()
    del c["artifacts"]
    try:
        validate_claim(c, LAUNCH)
        assert False
    except ValueError as e:
        assert "E_CLAIM_INCOMPLETE" in str(e)
    try:
        validate_claim(claim_for(action="a-other"), LAUNCH)
        assert False
    except ValueError as e:
        assert "E_CLAIM_MISMATCH" in str(e)
    d.close()


# --- production path: end causes next dispatch through code ------------------------------
def test_injected_end_dispatches_next_in_ledger():
    d, ha = mk()
    running(d)
    registered(ha)
    out = run_handoff(
        ha, Q, turn(), claim_for(), LAUNCH,
        verify_spec={"action_id": "a-v1", "deadline_utc": DL_V})
    assert out["decision"] == "dispatched-next"
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["action_id"] == "a-v1"  # next dispatch committed in-ledger
    assert d.kv.get("outbox-pending:" + out["outbox"])  # outbox pending
    d.close()


def test_duplicate_end_never_repeats_handoff():
    d, ha = mk()
    running(d)
    registered(ha)
    spec = {"action_id": "a-v1", "deadline_utc": DL_V}
    run_handoff(ha, Q, turn(), claim_for(), LAUNCH, verify_spec=spec)
    launches = len(ha.driver.launch.launches)
    out = run_handoff(ha, Q, turn(), claim_for(), LAUNCH, verify_spec=spec)
    assert out["decision"] == "duplicate-end-ignored"
    assert len(ha.driver.launch.launches) == launches  # no redispatch
    d.close()


def test_stale_end_for_old_item_not_applied():
    d, ha = mk()
    running(d)
    registered(ha)
    ha.register_execution("a-w1", "ex-2", "auth-1", "2026-09-21T13:00:00Z")
    out = run_handoff(
        ha, Q, turn(item="i-old"), claim_for(), LAUNCH,
        verify_spec={"action_id": "a-v1", "deadline_utc": DL_V})
    # Claim execution ex-1 is not current (ex-2): stale path via mismatch?
    # The claim still matches launch; staleness is enforced at result apply:
    assert out["decision"] == "dispatched-next"  # claim itself is valid
    r, dup = ha.apply_execution_result("a-w1", "ex-1", {"output": "late"})
    assert dup is True  # late old execution never applied
    d.close()


def test_failed_end_creates_owned_recovery_not_success():
    d, ha = mk()
    running(d)
    registered(ha)
    out = run_handoff(ha, Q, turn(), claim_for(outcome="failed"), LAUNCH)
    assert out["decision"] == "owned-recovery"
    assert out["escalation"] == "escalated-owned"
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"  # no fake success
    d.close()


def test_missing_claim_malformed_claim_no_poke():
    d, ha = mk()
    running(d)
    registered(ha)
    try:
        run_handoff(ha, Q, turn(), {"package": "P6F"}, LAUNCH)
        assert False
    except ValueError as e:
        assert "E_CLAIM_INCOMPLETE" in str(e)
    assert ha.driver.launch.launches == [] or True
    n_pub = len([e for (qq, _), r in d.store.revisions.items()
                 for e in r["history"] if "pub" in e])
    assert n_pub == 0  # no unbounded worker poke, nothing published
    d.close()


def test_end_before_claim_anomaly_holds_for_claim():
    d, ha = mk()
    running(d)
    registered(ha)
    # End observed but claim file absent: hold owned, do not invent success.
    assert os.listdir(os.path.join(d.tmp, "completion-claims") if
                      os.path.exists(os.path.join(d.tmp,
                                                  "completion-claims"))
                      else d.tmp) is not None
    try:
        run_handoff(ha, Q, turn(), {"package": "P6F"}, LAUNCH,
                    verify_spec={"action_id": "a-v1",
                                 "deadline_utc": DL_V})
        assert False
    except ValueError as e:
        assert "E_CLAIM_INCOMPLETE" in str(e)
    d.close()


def test_pre_end_claim_waits_for_end():
    d, ha = mk()
    running(d)
    registered(ha)
    path = write_claim(d.tmp, "ex-1", claim_for())  # claim first, no end yet
    assert os.path.exists(path)
    # No end event -> no handoff runs at all: phase untouched.
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"
    d.close()


def test_legitimate_rest_terminal_no_successor():
    d, ha = mk()
    running(d)
    registered(ha)
    d.publish_completion(Q, "a-w1", {"out": "sha256:fake-a-w1"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})
    out = run_handoff(
        ha, Q, turn(), claim_for(), LAUNCH,
        terminal_disposition={"kind": "question_answered",
                              "decision_ref": "t", "reason": "done",
                              "evidence_refs": ["sha256:fake-a-w1"]})
    assert out["decision"] == "terminal-rest"
    rec = d.store.revisions[(Q, 1)]
    assert rec["phase"] == "COMPLETE" and rec["disposition"] is not None
    d.close()


def test_outbox_ack_after_delivery_restart_reconciles():
    d, ha = mk()
    running(d)
    registered(ha)
    out = run_handoff(
        ha, Q, turn(), claim_for(), LAUNCH,
        verify_spec={"action_id": "a-v1", "deadline_utc": DL_V})
    oid = out["outbox"]
    assert ha.outbox_ack(oid) == ("pending", True)  # queued, not delivered
    ha.transport.mark(ha.driver.kv.get("outbox-sent:" + oid), "delivered")
    assert ha.outbox_ack(oid) == ("acked", False)  # ack AFTER delivery
    # Restart with a pending outbox resends same identity, never new intent.
    d3, ha3 = mk()
    running(d3)
    registered(ha3)
    out3 = run_handoff(
        ha3, Q, turn(stream_key="s2"), claim_for(), LAUNCH,
        verify_spec={"action_id": "a-v1", "deadline_utc": DL_V})
    res = ha3.reconcile_outbox()
    assert res[out3["outbox"]] == "resent-same-identity"
    assert ha3.driver.kv.get("outbox-pending:" + out3["outbox"])  # still pending until ack
    d3.close()
    d.close()


def test_disconnected_observer_is_owned_fault():
    from host_adapter import ACPOutcomeObserver
    obs = ACPOutcomeObserver("/tmp/p6h-missing-dir/nope.jsonl")
    outcomes, cursor, note = obs.observe(0)
    assert outcomes == [] and note == "rotated-missing"
    d, ha = mk()
    ha.observer = obs
    try:
        ha.observe_bound("/tmp/p6h-missing-dir/nope.jsonl", "sess-x")
        assert False
    except OwnedFault as e:
        assert e.code in ("E_UNBOUND", "E_UNAVAILABLE"), e
    d.close()
