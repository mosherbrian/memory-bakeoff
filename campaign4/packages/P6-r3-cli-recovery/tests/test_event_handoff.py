"""P6-r2.1 event handoff: runtime turn-end primary trigger, route-free
FILE claims, transactional intent, durable outbox. Injected effects only.

Rationale for changed tests (repair D2/D3): the initial suite passed
caller-constructed claim dicts and fixed example artifacts/deadlines.
The repaired boundary loads atomically published claim files from the
launch-assigned path, recomputes artifact hashes from actual files, and
takes recovery bounds from the launch manifest — so these tests stage
real files and manifest bounds instead."""
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
ESC_DL = "2026-09-21T16:00:00Z"


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


def staged(d, ha, action="a-w1", execution="ex-1", stream="sess",
           item="i1", step="worker-run", outcome="completed",
           art_content=b"artifact-bytes"):
    """Stage a bound turn + registered execution + artifact files + an
    atomically published claim file. Returns (launch, claims_dir)."""
    base = os.path.join(d.tmp, "art")
    os.makedirs(os.path.join(base, "artifacts"), exist_ok=True)
    claims = os.path.join(d.tmp, "claims")
    import hashlib
    digest = hashlib.sha256(art_content).hexdigest()
    with open(os.path.join(base, "artifacts", "out.bin"), "wb") as fh:
        fh.write(art_content)
    ha.register_execution(action, execution, "auth-1", DL_V)
    ha.bind_turn(stream, item, execution, action, step)
    ha.bind_route("a-v1", "p6-fixture-verifier")
    launch = {"package": "P6F", "attempt": "a1", "action": action,
              "execution": execution, "contract_step": step,
              "escalation_deadline_utc": ESC_DL,
              "artifact_base_dir": base}
    write_claim(claims, execution, {
        "package": "P6F", "attempt": "a1", "action": action,
        "execution": execution, "contract_step": step, "outcome": outcome,
        "artifacts": {"out": {"path": "artifacts/out.bin",
                              "sha256": digest}}})
    return launch, claims


def turn(item="i1", kind="end", stream_key="sess"):
    return {"stream_key": stream_key, "item": item, "kind": kind,
            "extra": {}}


SPEC = {"action_id": "a-v1", "deadline_utc": DL_V}


# --- watcher: loss/truncation/dup/stale/restart ------------------------------------
def test_sidecar_poll_dedups_and_survives_truncation():
    tmp = tempfile.mkdtemp(prefix="p6s-")
    p = os.path.join(tmp, "sess.jsonl")
    with open(p, "w") as fh:
        fh.write('{"t":"start","item":"i1"}\n{"t":"d","item":"i1"}\n'
                 '{"t":"end","item":"i1"}\n')
    w = TurnWatcher(tmp)
    seen = set()
    evs, cursors, notes, labels = w.poll(
        ["sess"], {}, seen.add, lambda t: t in seen)
    assert [e["kind"] for e in evs] == ["start", "d", "end"]
    assert notes == {"sess": "ok"} and labels == {"sess":
                                                  "replay-fallback"}
    w.notify("sess")
    evs2, _, _, labels2 = w.poll(["sess"], cursors, seen.add,
                                 lambda t: t in seen)
    assert evs2 == [] and labels2 == {"sess": "notified"}  # no dup
    with open(p, "w") as fh:  # truncation (per-turn reset)
        fh.write('{"t":"start","item":"i2"}\n')
    evs3, _, _, _ = w.poll(["sess"], cursors, seen.add,
                           lambda t: t in seen)
    # Repair D4: whole-file rescan + durable seen set makes truncation
    # lossless with no special note (old rows skipped, new turn emitted).
    assert [e["item"] for e in evs3] == ["i2"]  # new turn, nothing lost
    assert w.poll(["nope"], {}, seen.add,
                  lambda t: t in seen)[2] == {"nope": "rotated-missing"}


def test_partial_tail_held_same_length_replacement_emits():
    tmp = tempfile.mkdtemp(prefix="p6p-")
    p = os.path.join(tmp, "sess.jsonl")
    with open(p, "w") as fh:
        fh.write('{"t":"end","item":')  # partial record
    w = TurnWatcher(tmp)
    seen = set()
    evs, cursors, notes, _ = w.poll(["sess"], {}, seen.add,
                                    lambda t: t in seen)
    assert evs == [] and notes == {"sess": "partial-tail-held"}
    with open(p, "w") as fh:  # replacement with still-partial content
        fh.write('{"t":"end","itemX"}')
    evs2, _, _, _ = w.poll(["sess"], cursors, seen.add,
                           lambda t: t in seen)
    assert evs2 == []  # still partial: nothing invented
    # Repair D4: the producer completes the torn record by rewrite; the
    # held bytes are NOT skipped past — the completed line emits exactly
    # once. (Bytes glued mid-line without a newline are unframed and
    # cannot be recovered; the producer invariant is newline framing.)
    with open(p, "w") as fh:
        fh.write('{"t":"end","item":"i9"}\n')
    evs3, _, _, _ = w.poll(["sess"], cursors, seen.add,
                           lambda t: t in seen)
    assert [e["item"] for e in evs3] == ["i9"]  # kept bytes, no loss


# --- claims --------------------------------------------------------------------------
def test_claim_writer_and_route_free_validation():
    d, ha = mk()
    launch, claims = staged(d, ha)
    loaded = json.load(open(os.path.join(claims, "ex-1.json")))
    assert validate_claim(loaded, dict(launch, execution="ex-1",
                                       action="a-w1",
                                       contract_step="worker-run",
                                       package="P6F",
                                       attempt="a1")) == loaded
    base = {"package": "P6F", "attempt": "a1", "action": "a-w1",
            "execution": "ex-1", "contract_step": "worker-run",
            "outcome": "completed",
            "artifacts": {"o": {"path": "x", "sha256": "y"}}}
    for bad in ("verifier", "destination", "next_task", "duration_s",
                "deadline", "disposition"):
        c = dict(base, **{bad: "x"})
        try:
            validate_claim(c, base)
            assert False, "expected E_FORGED_ROUTE"
        except ValueError as e:
            assert "E_FORGED_ROUTE" in str(e), e
    d.close()


# --- production path: end causes next dispatch through code ------------------------------
def test_injected_end_dispatches_next_in_ledger():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "transition-committed"
    fl = d.store.revisions[(Q, 1)]["flight"]
    assert fl["action_id"] == "a-v1"  # next dispatch committed in-ledger
    assert d.kv.get("outbox-pending:" + out["outbox"])  # outbox pending
    d.close()


def test_duplicate_end_never_repeats_handoff():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    run_handoff(ha, Q, turn(), claims, launch, SPEC)
    n_events = d.store.conn.execute(
        "SELECT COUNT(*) FROM events").fetchone()[0]
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "duplicate-end-ignored"
    assert d.store.conn.execute(
        "SELECT COUNT(*) FROM events").fetchone()[0] == n_events
    d.close()


def test_stale_unbound_nonend_rejected_pre_mutation():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    before = d.store.conn.execute(
        "SELECT COUNT(*) FROM events").fetchone()[0]
    for bad_turn, code in (
            (turn(kind="start"), "E_NOT_END"),
            (turn(item="i-other"), "E_UNBOUND_TURN"),
            (turn(stream_key="other"), "E_UNBOUND_TURN")):
        try:
            run_handoff(ha, Q, bad_turn, claims, launch, SPEC)
            assert False, "expected " + code
        except OwnedFault as e:
            assert e.code == code, (bad_turn, e.code)
    assert d.store.conn.execute(
        "SELECT COUNT(*) FROM events").fetchone()[0] == before
    assert d.kv.get("turn-seen:sess:i-other:ex-1") is None  # no writes
    d.close()


def test_failed_end_creates_owned_recovery_not_success():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha, outcome="failed")
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "owned-recovery"
    assert out["escalation"] == "escalated-owned"
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"  # no fake success
    d.close()


def test_missing_claim_malformed_claim_no_poke():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    os.remove(os.path.join(claims, "ex-1.json"))  # missing claim file
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "owned-recovery"  # bounded, never pokes
    with open(os.path.join(claims, "ex-1.json"), "w") as fh:
        fh.write("{malformed")  # malformed claim file
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "owned-recovery"
    n_pub = len([e for (qq, _), r in d.store.revisions.items()
                 for e in r["history"] if "pub" in e])
    assert n_pub == 0
    d.close()


def test_end_before_claim_anomaly_holds_for_claim():
    d, ha = mk()
    running(d)
    launch, _ = staged(d, ha)
    empty = os.path.join(d.tmp, "empty-claims")  # end first, no claim yet
    os.makedirs(empty)
    out = run_handoff(ha, Q, turn(), empty, launch, SPEC)
    assert out["decision"] == "owned-recovery"  # holds, invents nothing
    d.close()


def test_pre_end_claim_waits_for_end():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    assert os.path.exists(os.path.join(claims, "ex-1.json"))
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"  # no end, no run
    d.close()


def test_worker_cannot_supply_terminal_disposition():
    d, ha = mk()
    running(d)
    d.publish_completion(Q, "a-w1", {"out": "sha256:fake-a-w1"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})
    launch, claims = staged(d, ha)
    out = run_handoff(ha, Q, turn(), claims, launch, None)
    # Worker completion without a bound verifier step: recovery, and the
    # ledger is NOT closed by any worker-supplied disposition.
    assert out["decision"] == "owned-recovery"
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    d.close()


def test_verify_close_needs_director_authorized_disposition():
    d, ha = mk()
    running(d)
    d.publish_completion(Q, "a-w1", {"out": "sha256:fake-a-w1"},
                         verify={"action_id": "a-v1", "owner": "corvid",
                                 "deadline": DL_V})
    ha.register_execution("a-v1", "ex-v1", "auth-v", DL_V)
    ha.bind_turn("sess", "i-v", "ex-v1", "a-v1", "verify-run")
    base = os.path.join(d.tmp, "art")
    os.makedirs(os.path.join(base, "artifacts"), exist_ok=True)
    import hashlib
    digest = hashlib.sha256(b"artifact-bytes").hexdigest()
    with open(os.path.join(base, "artifacts", "out.bin"), "wb") as fh:
        fh.write(b"artifact-bytes")
    claims = os.path.join(d.tmp, "claims")
    vlaunch = {"package": "P6F", "attempt": "a1", "action": "a-v1",
               "execution": "ex-v1", "contract_step": "verify-run",
               "escalation_deadline_utc": ESC_DL,
               "artifact_base_dir": base}
    write_claim(claims, "ex-v1", {
        "package": "P6F", "attempt": "a1", "action": "a-v1",
        "execution": "ex-v1", "contract_step": "verify-run",
        "outcome": "completed",
        "artifacts": {"out": {"path": "artifacts/out.bin",
                              "sha256": digest}}})
    # No director-authorized disposition bound: rejected, never closed.
    try:
        run_handoff(ha, Q, turn(item="i-v"), claims, vlaunch)
        assert False, "expected E_FORGED_DISPOSITION"
    except OwnedFault as e:
        assert e.code == "E_FORGED_DISPOSITION", e
    assert d.store.revisions[(Q, 1)]["phase"] == "CHECKING"
    # With the director-authorized disposition: terminal rest, quiet.
    vlaunch["authorized_dispositions"] = [
        {"kind": "question_answered", "decision_ref": "t",
         "reason": "verified done",
         "evidence_refs": ["sha256:fake-a-w1"]}]
    out = run_handoff(ha, Q, turn(item="i-v"), claims, vlaunch)
    assert out["decision"] == "terminal-rest"
    rec = d.store.revisions[(Q, 1)]
    assert rec["phase"] == "COMPLETE" and rec["disposition"] is not None
    d.close()


def test_artifact_mutation_detected():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha, art_content=b"original-bytes")
    with open(os.path.join(d.tmp, "art", "artifacts", "out.bin"),
              "wb") as fh:
        fh.write(b"mutated-bytes")  # actual on-disk mutation
    # Actual on-disk mutation routes to bounded recovery, never success.
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "owned-recovery"
    assert d.store.revisions[(Q, 1)]["phase"] == "RUNNING"
    d.close()


def test_outbox_ack_after_delivery_restart_reconciles():
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    oid = out["outbox"]
    assert ha.outbox_ack(oid) == ("pending", True)  # queued, not delivered
    ha.transport.mark(ha.driver.kv.get("outbox-sent:" + oid), "delivered")
    assert ha.outbox_ack(oid) == ("acked", False)  # ack AFTER delivery
    assert ha.reconcile_outbox() == {}  # acked: nothing resent
    d.close()


def test_roll_forward_after_crash_before_commit():
    # Repair D3: simulate death after intent/seen writes, before the ledger
    # commit. A retry must roll forward under the same identities - the
    # old code reported duplicate-end-ignored with the ledger stuck.
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    import json as _json
    d._kv_put("turn-seen:sess:i1:ex-1",
              _json.dumps({"outcome": "completed"}))
    d._kv_put("handoff-intent:a-w1:ex-1", _json.dumps(
        {"next": "verifier-dispatch", "action": "a-w1",
         "execution": "ex-1", "verify_action": "a-v1",
         "hashes": {"out": "sha256:fake-a-w1"}}))
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out.get("recovered") is True
    assert out["decision"] == "transition-committed"
    assert d.store.revisions[(Q, 1)]["flight"]["action_id"] == "a-v1"
    assert d.kv.get("handoff-done:a-w1:ex-1")  # completion now marked
    d.close()


def test_restart_at_every_boundary_no_blind_replay():
    import shutil
    d, ha = mk()
    running(d)
    launch, claims = staged(d, ha)
    out = run_handoff(ha, Q, turn(), claims, launch, SPEC)
    assert out["decision"] == "transition-committed"
    db, wpath = d.store.path, os.path.join(d.tmp, "world.json")
    d.close()
    d2 = Driver(db, FakeClock("2026-09-21T12:30:00Z"),
                FakeExternalWorld(wpath))
    ha2 = HostAdapter(d2)
    out2 = ha2.reconcile_outbox()  # pending outbox, same identity
    assert out2[out["outbox"]] in ("resent-same-identity",
                                   "held-awaiting-receipt",
                                   "held-ambiguous")
    assert ha2.driver.kv.get("handoff-done:a-w1:ex-1")  # done persisted
    d2.close()
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
