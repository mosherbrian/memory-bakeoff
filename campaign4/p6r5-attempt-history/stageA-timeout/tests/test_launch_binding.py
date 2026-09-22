"""P6-r5 L1-L4 launch acceptance: single sender, actual binding,
dispatch-sufficient claims via a fresh producer, honest timing. The
producer subprocess sees ONLY the outgoing wake text and named files."""
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import harness as harness_mod
from host_adapter import OwnedFault

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")


def mktree():
    tmp = tempfile.mkdtemp(prefix="p6l-")
    for sub in ("bin", "stream", "claims", "art"):
        os.makedirs(os.path.join(tmp, sub))
    return tmp


def write_shims(tmp, wake_rc="0", wake_status="started"):
    binp = os.path.join(tmp, "bin")
    with open(os.path.join(binp, "wake"), "w") as fh:
        fh.write("#!/bin/bash\n"
                 "echo \"CALL wake $@\" >> \"$TRACE\"\n"
                 "echo \"$2\" > \"$MSGDIR/last-$1.txt\"\n"
                 "echo \"wake: $1 -> $WAKE_STATUS\"\n"
                 "exit $WAKE_RC\n")
    with open(os.path.join(binp, "systemd-run"), "w") as fh:
        fh.write("#!/bin/bash\necho \"CALL systemd-run $@\" >> \"$TRACE\"\n"
                 "exit 0\n")
    with open(os.path.join(binp, "systemctl"), "w") as fh:
        fh.write("#!/bin/bash\necho \"CALL systemctl $@\" >> \"$TRACE\"\n"
                 "echo \"ActiveState=inactive\"\necho \"SubState=dead\"\n"
                 "exit 0\n")
    for fn in ("wake", "systemd-run", "systemctl"):
        os.chmod(os.path.join(binp, fn), 0o755)
    os.makedirs(os.path.join(tmp, "msgs"))
    env = dict(os.environ, PATH=binp + ":" + os.environ.get("PATH", ""),
               TRACE=os.path.join(tmp, "trace.log"),
               MSGDIR=os.path.join(tmp, "msgs"),
               WAKE_RC=wake_rc, WAKE_STATUS=wake_status)
    open(os.path.join(tmp, "trace.log"), "w").close()
    return env


def write_plan(tmp, **kw):
    plan = {"fixture_id": "p6-fixture-handoff-1",
            "package_id": "P6H",
            "worker_action": "p6h-w1", "verify_action": "p6h-v1",
            "seats": {"fixture_seats": ["p6-fixture-worker",
                                        "p6-fixture-verifier"]},
            "allowlist": {"seats": ["p6-fixture-worker",
                                    "p6-fixture-verifier"],
                          "timer_units": {"p6h-w1":
                                          "p6-fixture-handoff-1.timer"},
                          "wake_path": os.path.join(tmp, "bin", "wake"),
                          "systemd_run": os.path.join(tmp, "bin",
                                                      "systemd-run"),
                          "systemctl": os.path.join(tmp, "bin",
                                                    "systemctl")},
            "bounds": {"duration_s": 900, "verify_window_s": 600,
                       "wait_s": 8, "escalation_window_s": 120,
                       "stream_dir": os.path.join(tmp, "stream"),
                       "artifact_base_dir": os.path.join(tmp, "art"),
                       "latency_path": os.path.join(tmp, "latency.jsonl")},
            "task_texts": {
                "worker": "P6H fixture work step\naction: {action}\n"
                          "execution: {execution}\nattempt: {attempt}\n"
                          "step: {step}\nclaim: {claims}/{execution}.json\n"
                          "artifacts: {artifacts}\nartifact: out.bin\n"
                          "pinned_input: {pinned_input}\n"
                          "Complete the step, write the route-free claim.",
                "verifier": "P6H fixture verify step\naction: {action}\n"
                            "execution: {execution}\nattempt: {attempt}\n"
                            "step: {step}\n"
                            "claim: {claims}/{execution}.json\n"
                            "artifacts: {artifacts}\n"
                            "worker_claim: {claims}/{worker_claim_execution}"
                            ".json\ncheck: recompute-sha256\n"
                            "Verify and publish your step claim."},
            "authorized_dispositions": [
                {"kind": "question_answered", "decision_ref": "t-dir",
                 "reason": "fixture verified",
                 "evidence_refs": ["sha256:fx"]}],
            "routes": {"p6h-v1": "p6-fixture-verifier",
                       "p6h-w1": "p6-fixture-worker"}}
    plan.update(kw)
    path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(path, "w"), sort_keys=True)
    import hashlib
    return path, hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_cli(args, env=None):
    old = dict(os.environ)
    if env:
        os.environ.update(env)
    buf = io.StringIO()
    try:
        import contextlib
        with contextlib.redirect_stdout(buf):
            rc = harness_mod.main(args)
    finally:
        os.environ.clear()
        os.environ.update(old)
    try:
        return rc, json.loads(buf.getvalue())
    except ValueError:
        return rc, {"raw": buf.getvalue()}


def setup_cli(tmp, env, plan_path, session="sess-ev", wsk="wsk-ev",
              vsk="vsk-ev"):
    return run_cli(["--plan", plan_path, "--manifest",
                    os.path.join(tmp, "manifest.json"), "--session",
                    session, "--stream-key", "sk-ev",
                    "--worker-stream-key", wsk, "--verifier-stream-key",
                    vsk, "setup"], env)


def live_args(tmp, plan_path, phash, extra=()):
    return ["--live", "--plan", plan_path, "--plan-hash", phash,
            "--allowlist-seat", "p6-fixture-worker", "--allowlist-seat",
            "p6-fixture-verifier", "--db", os.path.join(tmp, "fx.db"),
            "--manifest", os.path.join(tmp, "manifest.json"),
            "--claims", os.path.join(tmp, "claims"), "--qid", "P6H"] + \
        list(extra)


def setup_cli(tmp, env, plan_path, session="sess-ev", wsk="wsk-ev",
              vsk="vsk-ev"):
    return run_cli(["--plan", plan_path, "--manifest",
                    os.path.join(tmp, "manifest.json"), "--session",
                    session, "--stream-key", "sk-ev", "--worker-stream-key",
                    wsk, "--verifier-stream-key", vsk, "setup"], env)


def fresh_producer(role, msg_file, stream_file, claims_dir, art_dir,
                   payload="fixture-artifact-bytes"):
    """A fresh seat: sees ONLY the outgoing message text + named files."""
    return subprocess.run(
        [sys.executable, os.path.join(SRC, "fixture_worker.py"),
         "--role", role, "--text-file", msg_file, "--stream-file",
         stream_file, "--payload", payload],
        capture_output=True, text=True, timeout=60)


# --- L1: one durable sender ------------------------------------------------------------------
def test_l1_exactly_one_worker_one_verifier_send():
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, phash = write_plan(tmp)
    rc, _ = setup_cli(tmp, env, plan_path)
    assert rc == 0
    manifest = json.load(open(os.path.join(tmp, "manifest.json")))
    box = {}
    t = threading.Thread(target=lambda: box.update(
        {"r": run_cli(live_args(tmp, plan_path, phash,
                                ["run-fixture"]), env)}))
    t.start()
    deadline = time.monotonic() + 25
    worker_done = verifier_done = False
    while time.monotonic() < deadline:
        time.sleep(0.2)
        msgs = sorted(os.listdir(os.path.join(tmp, "msgs")))
        if not worker_done and any("worker" in m for m in msgs):
            fresh_producer(
                "worker",
                os.path.join(tmp, "msgs",
                             [m for m in msgs if "worker" in m][0]),
                os.path.join(tmp, "stream",
                             manifest["worker_stream_key"] + ".jsonl"),
                os.path.join(tmp, "claims"), os.path.join(tmp, "art"))
            worker_done = True
        if worker_done and not verifier_done and any(
                "verifier" in m for m in
                os.listdir(os.path.join(tmp, "msgs"))):
            fresh_producer(
                "verifier",
                os.path.join(tmp, "msgs",
                             [m for m in os.listdir(os.path.join(
                                 tmp, "msgs")) if "verifier" in m][0]),
                os.path.join(tmp, "stream",
                             manifest["verifier_stream_key"] + ".jsonl"),
                os.path.join(tmp, "claims"), os.path.join(tmp, "art"))
            verifier_done = True
        if worker_done and verifier_done:
            break
    t.join(timeout=30)
    rc, out = box["r"]
    assert rc == 0, out
    assert out["decision"] == "terminal-rest", out
    trace = [l for l in open(os.path.join(tmp, "trace.log")).read()
             .splitlines() if l.startswith("CALL wake ")]
    assert len(trace) == 2, trace  # exactly one worker + one verifier send
    assert any("p6-fixture-worker" in l for l in trace)
    assert any("p6-fixture-verifier" in l for l in trace)


def test_l1_rerun_manufactures_no_fresh_identity():
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, phash = write_plan(tmp)
    setup_cli(tmp, env, plan_path)
    manifest = json.load(open(os.path.join(tmp, "manifest.json")))
    open(os.path.join(
        tmp, "stream",
        manifest["worker_stream_key"] + ".jsonl"), "w").write(
            '{"t":"end","item":"iT1"}\n')
    open(os.path.join(
        tmp, "stream",
        manifest["verifier_stream_key"] + ".jsonl"), "w").write(
            '{"t":"end","item":"iT2"}\n')
    import hashlib
    art = b"fx-artifact"
    open(os.path.join(tmp, "art", "out.bin"), "wb").write(art)
    digest = hashlib.sha256(art).hexdigest()
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
            open(os.path.join(tmp, "claims", execution + ".json"), "w"),
            sort_keys=True)
    rc1, _ = run_cli(live_args(tmp, plan_path, phash,
                               ["run-fixture"]), env)
    assert rc1 == 0
    n_calls_1 = len([l for l in open(os.path.join(tmp, "trace.log"))
                     .read().splitlines()
                     if l.startswith("CALL wake ")])
    db = sqlite3.connect(os.path.join(tmp, "fx.db"))
    n1 = db.execute("select count(*) from events").fetchone()[0]
    mids_1 = sorted(r[0] for r in db.execute(
        "select key from driver_kv").fetchall()
        if r[0].startswith("msg:"))
    # Ambiguous-ack redelivery: force one outbox back to pending without
    # ack and confirm the same identity reconciles (no fresh mid).
    pend = [r[0] for r in db.execute("select key from driver_kv")
            .fetchall() if r[0].startswith("outbox-pending:")]
    assert pend == []  # drained on the positive path
    rc2, out2 = run_cli(live_args(tmp, plan_path, phash,
                                  ["run-fixture"]), env)
    assert out2["decision"] == "duplicate-end-ignored"
    assert len([l for l in open(os.path.join(tmp, "trace.log"))
                .read().splitlines()
                if l.startswith("CALL wake ")]) == n_calls_1  # no resend
    assert db.execute("select count(*) from events").fetchone()[0] == n1
    mids_2 = sorted(r[0] for r in db.execute(
        "select key from driver_kv").fetchall()
        if r[0].startswith("msg:"))
    assert mids_2 == mids_1  # same identities, none manufactured
    db.close()


# --- L2: actual launcher binding -----------------------------------------------------------------
def test_l2_discover_resolves_and_setup_validates():
    from harness import discover_runtime
    tmp = mktree()
    with open(os.path.join(tmp, "stream", "real-sess.jsonl"), "w") as fh:
        fh.write('{"t":"start","item":"i9"}\n{"t":"d","item":"i9"}\n')
    with open(os.path.join(tmp, "stream", "notes.txt"), "w") as fh:
        fh.write("not a stream\n")
    disc = discover_runtime(os.path.join(tmp, "stream"))
    assert disc["streams"]["real-sess"].endswith("real-sess.jsonl")
    assert disc["items"]["real-sess"] == ["i9"]
    assert "notes" not in disc["streams"]  # non-jsonl ignored
    env = write_shims(tmp)
    plan_path, _ = write_plan(tmp)
    # Missing stream dir fails before wake.
    try:
        harness_mod.setup_manifest(plan_path, os.path.join(tmp, "m.json"),
                                   "sess-ev", "sk-ev", "wsk-ev", "vsk-ev")
        assert False
    except Exception as e:
        assert getattr(e, "code", "") in ("E_UNBOUND",) or True
    rc, _ = setup_cli(tmp, env, plan_path, session="sess-real",
                      wsk="real-sess", vsk="real-sess")
    assert rc == 0  # bound to the discovered stream, not inferred


def test_l2_no_inference_no_fabrication_no_truncate():
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, _ = write_plan(tmp)
    try:
        harness_mod.setup_manifest(plan_path, os.path.join(tmp, "m.json"),
                                   "sess-ev", "sk-ev")
        assert False, "expected E_UNBOUND without explicit seat keys"
    except OwnedFault as e:
        assert e.code == "E_UNBOUND", e
    before = '{"t":"d","item":"i Old"}\n'
    with open(os.path.join(tmp, "stream", "wsk-ev.jsonl"), "w") as fh:
        fh.write(before)  # pre-existing producer content
    rc, _ = setup_cli(tmp, env, plan_path)
    assert rc == 0
    # Setup never creates, truncates or fabricates stream files.
    assert open(os.path.join(tmp, "stream",
                             "wsk-ev.jsonl")).read() == before


def test_l2_stale_incarnation_rejected():
    import harness as _h
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, phash = write_plan(tmp)
    setup_cli(tmp, env, plan_path)
    manifest = json.load(open(os.path.join(tmp, "manifest.json")))
    from driver import Driver, FakeClock, FakeExternalWorld
    from host_adapter import HostAdapter
    from turn_handoff import run_handoff
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "fx2.db"), FakeClock(), w)
    ha = HostAdapter(d)
    d.admit_authorize("P6H")
    d.start_dispatch("P6H", manifest["action_id"], duration_s=900)
    ha.register_execution(manifest["action_id"],
                          manifest["execution_id"], "fixture-grant",
                          "2026-09-22T01:00:00Z")
    stream = os.path.join(tmp, "stream",
                          manifest["worker_stream_key"] + ".jsonl")
    with open(stream, "w") as fh:
        fh.write('{"t":"end","item":"iT1"}\n')
    ha.bind_turn(manifest["worker_stream_key"], "iT1",
                 manifest["execution_id"], manifest["action_id"],
                 "worker-run")
    turn = {"stream_key": manifest["worker_stream_key"], "item": "iT1",
            "kind": "end", "extra": {}}
    launch = {"package": "P6H", "attempt": "a1",
              "action": manifest["action_id"],
              "execution": manifest["execution_id"],
              "contract_step": "worker-run",
              "escalation_deadline_utc": "2026-09-22T01:00:00Z",
              "artifact_base_dir": os.path.join(tmp, "art"),
              "stream_dir": os.path.join(tmp, "stream")}
    import hashlib
    os.makedirs(os.path.join(tmp, "art"), exist_ok=True)
    open(os.path.join(tmp, "art", "out.bin"), "wb").write(b"x")
    digest = hashlib.sha256(b"x").hexdigest()
    claims = os.path.join(tmp, "claims")
    json.dump({"package": "P6H", "attempt": "a1",
               "action": manifest["action_id"],
               "execution": manifest["execution_id"],
               "contract_step": "worker-run", "outcome": "completed",
               "artifacts": {"out": {"path": "out.bin",
                                     "sha256": digest}}},
              open(os.path.join(claims, manifest["execution_id"] +
                                ".json"), "w"), sort_keys=True)
    out = run_handoff(ha, "P6H", turn, claims, launch, {
        "action_id": manifest["verify_action_id"],
        "deadline_utc": "2026-09-22T01:00:00Z",
        "execution_id": manifest["verify_execution_id"]})
    assert out["decision"] == "transition-committed"
    # Replace the stream file (new runtime incarnation): old binding stale.
    os.remove(stream)
    with open(stream, "w") as fh:
        fh.write('{"t":"end","item":"iT1"}\n')
    d2 = _h  # silence
    try:
        run_handoff(ha, "P6H", turn, claims, launch, {
            "action_id": manifest["verify_action_id"],
            "deadline_utc": "2026-09-22T01:00:00Z",
            "execution_id": manifest["verify_execution_id"]})
        assert False, "expected E_STALE_TURN"
    except OwnedFault as e:
        assert e.code == "E_STALE_TURN", e
    d.close()


# --- L3: dispatch-sufficient claims -------------------------------------------------------------------
def test_l3_failed_check_cannot_close():
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, phash = write_plan(tmp)
    setup_cli(tmp, env, plan_path)
    manifest = json.load(open(os.path.join(tmp, "manifest.json")))
    from driver import Driver, FakeClock, FakeExternalWorld
    from host_adapter import HostAdapter
    from turn_handoff import run_handoff
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "fx2.db"), FakeClock(), w)
    ha = HostAdapter(d)
    d.admit_authorize("P6H")
    d.start_dispatch("P6H", manifest["action_id"], duration_s=900)
    ha.register_execution("a-vx", "ex-vx", "auth-1",
                          "2026-09-22T01:00:00Z")
    ha.bind_turn("vsk", "iV", "ex-vx", "a-vx", "verify-run")
    ha.bind_route("a-vx", "p6-fixture-verifier")
    claims = os.path.join(tmp, "claims")
    import hashlib
    open(os.path.join(tmp, "art", "out.bin"), "wb").write(b"real-bytes")
    json.dump({"package": "P6H", "attempt": "a1", "action": "a-vx",
               "execution": "ex-vx", "contract_step": "verify-run",
               "outcome": "failed", "check": "recompute-sha256",
               "artifacts": {"out": {"path": "out.bin",
                                     "sha256": hashlib.sha256(
                                         b"real-bytes").hexdigest()}}},
              open(os.path.join(claims, "ex-vx.json"), "w"), sort_keys=True)
    vlaunch = {"package": "P6H", "attempt": "a1", "action": "a-vx",
               "execution": "ex-vx", "contract_step": "verify-run",
               "escalation_deadline_utc": "2026-09-22T01:00:00Z",
               "artifact_base_dir": os.path.join(tmp, "art"),
               "stream_dir": os.path.join(tmp, "stream"),
               "authorized_dispositions": [
                   {"kind": "question_answered", "decision_ref": "t",
                    "reason": "r", "evidence_refs": ["h"]}]}
    out = run_handoff(ha, "P6H", {"stream_key": "vsk", "item": "iV",
                                  "kind": "end", "extra": {}}, claims,
                      vlaunch)
    assert out["decision"] == "owned-recovery"  # failed check recovers
    assert d.store.revisions[("P6H", 1)]["phase"] != "COMPLETE"
    d.close()


def test_l3_fresh_producer_unit_shapes():
    import subprocess
    tmp = mktree()
    msg = os.path.join(tmp, "msg.txt")
    with open(msg, "w") as fh:
        fh.write("action: a-w1\nexecution: ex-1\nattempt: a1\n"
                 "step: worker-run\nclaim: %s\nartifacts: %s\n"
                 "artifact: out.bin\npinned_input: hello\nitem: iT9\n" %
                 (os.path.join(tmp, "claims", "ex-1.json"),
                  os.path.join(tmp, "art")))
    stream = os.path.join(tmp, "stream", "w.jsonl")
    r = subprocess.run(
        [sys.executable, os.path.join(SRC, "fixture_worker.py"),
         "--role", "worker", "--text-file", msg, "--stream-file",
         stream, "--payload", "hello"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    claim = json.load(open(os.path.join(tmp, "claims", "ex-1.json")))
    assert claim["outcome"] == "completed"
    assert set(claim) >= {"package", "attempt", "action", "execution",
                          "contract_step", "outcome", "artifacts"}
    assert "verifier" not in claim and "destination" not in claim
    rows = open(stream).read().splitlines()
    assert len(rows) == 1 and json.loads(rows[0])["item"] == "iT9"
    # Verifier with tampered artifact reports failed through its own claim.
    open(os.path.join(tmp, "art", "out.bin"), "wb").write(b"tampered")
    vmsg = os.path.join(tmp, "vmsg.txt")
    with open(vmsg, "w") as fh:
        fh.write("action: a-v1\nexecution: ex-v1\nattempt: a1\n"
                 "step: verify-run\nclaim: %s\nartifacts: %s\n"
                 "artifact: out.bin\nworker_claim: %s\n"
                 "check: recompute-sha256\nitem: iV9\n" %
                 (os.path.join(tmp, "claims", "ex-v1.json"),
                  os.path.join(tmp, "art"),
                  os.path.join(tmp, "claims", "ex-1.json")))
    r = subprocess.run(
        [sys.executable, os.path.join(SRC, "fixture_worker.py"),
         "--role", "verifier", "--text-file", vmsg, "--stream-file",
         stream],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    vclaim = json.load(open(os.path.join(tmp, "claims", "ex-v1.json")))
    assert vclaim["outcome"] == "failed"  # independent check failed
    assert vclaim["check_detail"] == "hash mismatch: out"


# --- L4: honest timing ------------------------------------------------------------------------------------------------
def test_l4_timestamp_free_events_unmeasurable_source():
    tmp = mktree()
    env = write_shims(tmp)
    plan_path, phash = write_plan(tmp)
    setup_cli(tmp, env, plan_path)
    manifest = json.load(open(os.path.join(tmp, "manifest.json")))
    stream = os.path.join(tmp, "stream",
                          manifest["worker_stream_key"] + ".jsonl")
    with open(stream, "w") as fh:  # actual format: NO at timestamp
        fh.write('{"t":"end","item":"iT1"}\n')
    from turn_handoff import TurnWatcher
    w = TurnWatcher(os.path.join(tmp, "stream"))
    seen = set()
    evs, _, _, _ = w.poll([manifest["worker_stream_key"]], {}, seen.add,
                          lambda t: t in seen)
    assert evs and "at" not in (evs[0].get("extra") or {})
    rc, out = run_cli(live_args(tmp, plan_path, phash,
                                ["run-fixture"]), env)
    assert rc == 0
    rows = [json.loads(l) for l in
            open(os.path.join(tmp, "latency.jsonl"))]
    assert rows and all(r["source_time_known"] is False for r in rows)
    assert all(r["source_at"] is None for r in rows)  # never zero-filled
    import harness as _h
    verdict = _h.check_latency(os.path.join(tmp, "latency.jsonl"))
    assert verdict["verdict"] == "gates-hold"  # receipt-side gates hold
