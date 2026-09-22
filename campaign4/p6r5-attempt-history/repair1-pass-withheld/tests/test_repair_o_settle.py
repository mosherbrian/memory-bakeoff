"""P6-r4 O-settlement repair: valid production receipt plus authoritative
verifier start/outcome evidence, matched package/action/execution/message/
destination; atomic settlement; same identity across crash/reopen."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from driver import Driver, FakeClock, FakeExternalWorld
from host_adapter import HostAdapter, OwnedFault

Q = "P6O"
DL_V = "2026-09-22T01:00:00Z"


def mk():
    tmp = tempfile.mkdtemp(prefix="p6o-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    return d, HostAdapter(d)


class _OkRunner:
    """Injected runner with the real subprocess signature (rc 0 sent)."""

    def __init__(self):
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))

        class _Out:
            returncode = 0
            stdout = "wake: seat -> started\n"
            stderr = ""
        return _Out()


def mk_live(tmp=None):
    """Adapter on the production transport branch (injected runner)."""
    from host_adapter import HostWakeTransport
    tmp = tmp or tempfile.mkdtemp(prefix="p6ol-")
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    d.tmp = tmp
    run = _OkRunner()
    t = HostWakeTransport("/bin/wake", ("p6-fixture-verifier",),
                          enabled=True, kv_get=d.kv.get, kv_put=d._kv_put,
                          runner=run)
    ha = HostAdapter(d, transport=t)
    return d, ha, run


def running(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)


def prove_run(d, ha, action="a-v1", execution="ex-v",
              stream="sess", item="i-v"):
    """Stage the authoritative evidence: bound turn-seen + ledger flight
    for the target action in the same package (verifier started)."""
    ha.register_execution(action, execution, "auth-1", DL_V)
    ha.bind_turn(stream, item, execution, action, "verify-run")
    ha.bind_route(action, "p6-fixture-verifier")
    d._kv_put("turn-seen:%s:%s:%s" % (stream, item, execution),
              json.dumps({"outcome": "completed"}))
    if action == "a-v1":
        d.publish_completion("P6O", "a-w1", {"h": "x"},
                             verify={"action_id": "a-v1", "owner": "corvid",
                                     "deadline": DL_V})


def test_o_queued_plus_evidence_settles():
    d, ha, run = mk_live()
    running(d)
    prove_run(d, ha)
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    mid = ha.driver.kv.get("outbox-sent:" + oid)
    assert ha.transport.state(mid) == "sent"  # production receipt, not proof
    assert ha.drain_outbox_settled(Q) == [oid]  # runtime evidence completes
    assert ha.driver.kv.get("outbox-acked:" + oid) == mid
    assert ha.driver.kv.get("outbox-pending:" + oid) == ""
    d.close()


def test_o_queued_alone_never_settles():
    d, ha = mk()
    running(d)
    ha.bind_route("a-v1", "p6-fixture-verifier")
    ha.register_execution("a-v1", "ex-v", "auth-1", DL_V)
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    assert ha.drain_outbox_settled(Q) == []  # no runtime evidence
    assert ha.driver.kv.get("outbox-pending:" + oid)
    d.close()


def test_o_wrong_seat_stale_execution_collision_missing():
    import json as _json
    d, ha, run = mk_live()
    running(d)
    prove_run(d, ha)
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    mid = ha.driver.kv.get("outbox-sent:" + oid)
    # Wrong seat: tamper the receipt copy.
    raw = _json.loads(ha.driver.kv.get("msg:" + mid))
    raw["seat"] = "mallory-seat"
    ha.driver._kv_put("msg:" + mid, _json.dumps(raw))
    assert ha.drain_outbox_settled(Q) == []
    raw["seat"] = "p6-fixture-verifier"
    ha.driver._kv_put("msg:" + mid, _json.dumps(raw))
    # Stale execution: advance current past the receipt execution.
    ha.register_execution("a-v1", "ex-new", "auth-2", DL_V)
    assert ha.drain_outbox_settled(Q) == []
    d.close()


def test_o_msg_counter_never_rewinds_or_overwrites():
    d, ha, run = mk_live()
    running(d)
    ha.bind_route("a-v1", "p6-fixture-verifier")
    m1 = ha.transport.send("p6-fixture-verifier", "one", action="a-v1",
                           execution="ex-1")
    d2 = ha.driver
    d2._kv_put("msg-counter", "0")  # simulate a rewound counter
    try:
        ha.transport.send("p6-fixture-verifier", "two", action="a-v1",
                          execution="ex-1")
        assert False, "expected E_MSG_COLLISION"
    except OwnedFault as e:
        assert e.code == "E_MSG_COLLISION", e
    assert ha.transport.state(m1) == "sent"  # original receipt intact
    d.close()


def test_o_unrelated_terminal_proves_nothing():
    d, ha, run = mk_live()
    running(d)
    prove_run(d, ha)
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    # Terminal disposition in ANOTHER package must not settle this intent.
    d2q = "OTHER"
    d.admit_authorize(d2q)
    d.start_dispatch(d2q, "a-o", duration_s=60)
    d.publish_completion(d2q, "a-o", {"h": "x"},
                         verify={"action_id": "a-ov", "owner": "corvid",
                                 "deadline": DL_V})
    d.verify(d2q, "ev-o", True)
    d.store.append(d._ev("ev-od", d2q, "decide", "director",
                         {"disposition": {"kind": "question_answered",
                                          "decision_ref": "t", "reason": "r",
                                          "evidence_refs": ["h"]}}),
                   d.budget)
    assert ha.drain_outbox_settled("OTHER-Q-NOT-Q") == []
    assert ha.driver.kv.get("outbox-pending:" + oid)
    d.close()


def test_o_crash_before_after_delivery_and_ack():
    d, ha, run = mk_live()
    running(d)
    prove_run(d, ha)
    oid = ha.outbox_send("a-v1", {"kind": "x", "action": "a-v1"},
                         execution="ex-v")
    mid = ha.driver.kv.get("outbox-sent:" + oid)
    n_calls = len(ha.transport.calls)
    # Crash after delivery evidence, before ack-put: drain settles same mid.
    assert ha.drain_outbox_settled(Q) == [oid]
    assert ha.driver.kv.get("outbox-acked:" + oid) == mid
    # Crash after ack: reconcile + drain replay nothing, resend nothing.
    assert ha.drain_outbox_settled(Q) == []
    assert ha.reconcile_outbox() == {}
    assert len(ha.transport.calls) == n_calls
    # Ambiguous transport, evidence present: holds, never clears.
    ha.bind_route("a-v9", "p6-fixture-verifier")
    oid2 = ha.outbox_send("a-v9", {"kind": "y", "action": "a-v9"},
                          execution="ex-v")
    mid2 = ha.driver.kv.get("outbox-sent:" + oid2)
    raw2 = json.loads(ha.driver.kv.get("msg:" + mid2))
    raw2["state"] = "ambiguous"
    ha.driver._kv_put("msg:" + mid2, json.dumps(raw2))
    assert ha.drain_outbox_settled(Q) == []
    assert ha.driver.kv.get("outbox-pending:" + oid2)
    d.close()


def test_o_full_cli_terminal_restart_rollback_clean():
    import shutil
    import subprocess
    import harness as harness_mod
    tmp = tempfile.mkdtemp(prefix="p6oc-")
    bindir = os.path.join(tmp, "bin")
    os.makedirs(bindir)
    for name, body in (
            ("wake", "#!/bin/bash\necho \"wake: $1 -> started\"\nexit 0\n"),
            ("systemd-run", "#!/bin/bash\nexit 0\n"),
            ("systemctl", "#!/bin/bash\n"
             "echo \"ActiveState=inactive\"\necho \"SubState=dead\"\n"
             "exit 0\n")):
        with open(os.path.join(bindir, name), "w") as fh:
            fh.write(body)
        os.chmod(os.path.join(bindir, name), 0o755)
    stream = os.path.join(tmp, "stream")
    claims = os.path.join(tmp, "claims")
    art = os.path.join(tmp, "art")
    os.makedirs(stream)
    os.makedirs(claims)
    os.makedirs(art)
    plan = {"fixture_id": "p6-fixture-handoff-1", "package_id": "P6H",
            "worker_action": "p6h-w1", "verify_action": "p6h-v1",
            "seats": {"fixture_seats": ["p6-fixture-worker",
                                        "p6-fixture-verifier"]},
            "allowlist": {"seats": ["p6-fixture-worker",
                                    "p6-fixture-verifier"],
                          "timer_units": {"p6h-w1": "p6-fixture-u1.timer"},
                          "wake_path": os.path.join(bindir, "wake"),
                          "systemd_run": os.path.join(bindir,
                                                      "systemd-run"),
                          "systemctl": os.path.join(bindir, "systemctl")},
            "bounds": {"duration_s": 900, "verify_window_s": 600,
                       "wait_s": 5, "escalation_window_s": 120,
                       "stream_dir": stream, "artifact_base_dir": art,
                       "latency_path": os.path.join(tmp, "lat.jsonl")},
            "task_texts": {"worker": "TASK-W {action}",
                           "verifier": "TASK-V {action}"},
            "authorized_dispositions": [
                {"kind": "question_answered", "decision_ref": "t-dir",
                 "reason": "fixture verified",
                 "evidence_refs": ["sha256:fx"]}],
            "routes": {"p6h-v1": "p6-fixture-verifier"}}
    plan_path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(plan_path, "w"), sort_keys=True)
    import hashlib
    phash = hashlib.sha256(open(plan_path, "rb").read()).hexdigest()
    man_path = os.path.join(tmp, "manifest.json")
    manifest = harness_mod.setup_manifest(
        plan_path, man_path, "sess-ev", "sk-ev", "wsk-ev", "vsk-ev")
    assert manifest["worker_stream_key"] == "wsk-ev"
    assert manifest["verifier_stream_key"] == "vsk-ev"
    with open(os.path.join(stream, manifest["worker_stream_key"] +
                           ".jsonl"), "w") as fh:
        fh.write('{"t":"end","item":"iT1"}\n')
    with open(os.path.join(stream, manifest["verifier_stream_key"] +
                           ".jsonl"), "w") as fh:
        fh.write('{"t":"end","item":"iT2"}\n')
    digest = hashlib.sha256(b"fx-artifact").hexdigest()
    open(os.path.join(art, "out.bin"), "wb").write(b"fx-artifact")
    for execution, action, step in (
            (manifest["execution_id"], manifest["action_id"],
             "worker-run"),
            (manifest["verify_execution_id"],
             manifest["verify_action_id"], "verify-run")):
        json.dump(
            {"package": "P6H", "attempt": "a1", "action": action,
             "execution": execution, "contract_step": step,
             "outcome": "completed",
             "artifacts": {"out": {"path": "out.bin",
                                   "sha256": digest}}},
            open(os.path.join(claims, execution + ".json"), "w"),
            sort_keys=True)
    db = os.path.join(tmp, "fx.db")
    adapter = harness_mod.build_adapter(
        db, live=True, plan_hash=phash,
        allowlist_seats=("p6-fixture-worker", "p6-fixture-verifier"),
        plan_path=plan_path)
    out = harness_mod.run_fixture(adapter, manifest, claims, "P6H")
    assert out["decision"] == "terminal-rest", out
    adapter.driver.close()
    # Restart in a new process boundary: rollback succeeds, zero pending,
    # no second send, consistent archive.
    adapter2 = harness_mod.build_adapter(
        db, live=True, plan_hash=phash,
        allowlist_seats=("p6-fixture-worker", "p6-fixture-verifier"),
        plan_path=plan_path)
    # New process, same identities: nothing left to settle, no resends.
    assert adapter2.drain_outbox_settled("P6H") == []
    pending = [k for k, v in adapter2.driver.kv.items()
               if k.startswith("outbox-pending:") and v]
    assert pending == []  # zero unresolved delivered intents
    n_sends = len(adapter2.transport.calls)
    report = harness_mod.rollback_verify(
        db, man_path, os.path.join(tmp, "arc"))
    assert report["timers"] == "none-armed-verified"
    assert report["intents"] == "none-outstanding-verified"
    assert len(adapter2.transport.calls) == n_sends  # no second send
    arcdb = __import__("sqlite3").connect(
        os.path.join(tmp, "arc", "fixture.db"))
    assert arcdb.execute("select count(*) from events").fetchone()[0] == \
        adapter2.driver.store.conn.execute(
            "select count(*) from events").fetchone()[0]
    adapter2.driver.close()
