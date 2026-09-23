"""P6-r14 host-timing T1-T4 (new core bytes, exact CLI, injected only).

T1 timer authority: full identity on every callback; omitted/mismatched
fails closed. T2 verifier window from verifier dispatch, persisted once.
T3 NONTERMINAL continuation while the grant is open. T4 honest latency
rows/counts. Records module paths + hashes. Injected effects only.
"""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
R3H = os.path.join(SRC, "r3harness", "harness.py")
NEWC = os.path.join(SRC, "r3harness")
sys.path.insert(0, NEWC)
import lifecycle as LC  # noqa: E402  (origin check below proves new bytes)

PARENT_R13 = ("/home/bmosher/memory-bake-off/campaign4/packages/"
              "P6-r13-core-record-integrity/candidate/src/r3harness")
P5_FIXTURE = ("/home/bmosher/memory-bake-off/campaign4/packages/"
              "P6-r5-launch-binding/src/fixture_worker.py")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _origin_ok(mod, name):
    actual = os.path.realpath(mod.__file__)
    if actual.endswith(".pyc"):
        stem = os.path.basename(actual).split(".")[0] + ".py"
        actual = os.path.realpath(os.path.join(
            os.path.dirname(os.path.dirname(actual)), stem))
    return actual == os.path.realpath(os.path.join(NEWC, name))


def test_module_bytes_are_new_core():
    assert _origin_ok(LC, "lifecycle.py"), LC.__file__
    assert os.path.realpath(os.path.join(NEWC, "harness.py")) != \
        os.path.realpath(os.path.join(PARENT_R13, "harness.py"))
    print("harness=%s" % sha(os.path.join(NEWC, "harness.py"))[:12])


def mktree():
    tmp = tempfile.mkdtemp(prefix="p6r14-")
    for d in ("stream", "claims", "art", "onsets"):
        os.makedirs(os.path.join(tmp, d))
    return tmp


def write_plan(tmp, wait_s=2, duration_s=900, verify_window_s=600,
               escalation_window_s=120, live_stop_utc=None):
    plan = {"fixture_id": "p6-r14", "package_id": "P6R",
            "worker_action": "p6r-w1", "verify_action": "p6r-v1",
            "seats": {"fixture_seats": ["s-w", "s-v"]},
            "allowlist": {"seats": ["s-w", "s-v"],
                          "timer_units": {"p6r-w1": "u-r14.timer"},
                          "wake_path": "/bin/true",
                          "systemd_run": "/bin/true",
                          "systemctl": "/bin/true"},
            "bounds": {"duration_s": duration_s,
                       "verify_window_s": verify_window_s,
                       "wait_s": wait_s,
                       "escalation_window_s": escalation_window_s,
                       "stream_dir": os.path.join(tmp, "stream"),
                       "onset_dir": os.path.join(tmp, "onsets"),
                       "artifact_base_dir": os.path.join(tmp, "art"),
                       "latency_path": os.path.join(tmp, "latency.jsonl")},
            "task_texts": {
                "worker": "action: {action}\nexecution: {execution}\n"
                          "attempt: {attempt}\nstep: {step}\n"
                          "claim: {claims}/{execution}.json\n"
                          "artifacts: {artifacts}\nartifact: out.bin\n"
                          "pinned_input: {pinned_input}\n"
                          "package: P6R\nitem: iT1\n",
                "verifier": "action: {action}\nexecution: {execution}\n"
                            "attempt: {attempt}\nstep: {step}\n"
                            "claim: {claims}/{execution}.json\n"
                            "artifacts: {artifacts}\n"
                            "worker_claim: {claims}/{worker_claim_execution}"
                            ".json\ncheck: recompute-sha256\n"
                            "package: P6R\nitem: iV1\n"},
            "authorized_dispositions": [{"kind": "question_answered",
                                           "decision_ref": "d1",
                                           "reason": "verified"}],
            "routes": {"p6r-v1": "s-v", "p6r-w1": "s-w"}}
    if live_stop_utc is not None:
        plan["live_stop_utc"] = live_stop_utc
    path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(path, "w"), sort_keys=True)
    return path


def setup_cli(tmp, plan):
    manifest = os.path.join(tmp, "manifest.json")
    r = r3cli("--plan", plan, "--manifest", manifest, "--session", "s",
              "--stream-key", "sk", "--worker-stream-key", "wsk",
              "--verifier-stream-key", "vsk", "setup")
    assert r.returncode == 0, r.stdout + r.stderr
    return manifest


def r3cli(*args, timeout=120):
    return subprocess.run(
        [sys.executable, R3H] + list(args),
        capture_output=True, text=True, timeout=timeout, cwd=PKG)


def run_args(tmp, plan, manifest, cmd):
    return ["--live", "--plan", plan, "--plan-hash", sha(plan),
            "--allowlist-seat", "s-w", "--allowlist-seat", "s-v",
            "--db", os.path.join(tmp, "fx.db"), "--manifest", manifest,
            "--claims", os.path.join(tmp, "claims"), "--qid", "P6R", cmd]


def kv(db):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try:
        return dict(con.execute("select key, value from driver_kv")
                    .fetchall())
    finally:
        con.close()


def produce(role, tmp, manifest, delay=0.0):
    if delay:
        time.sleep(delay)
    m = json.load(open(manifest))
    stream = os.path.join(tmp, "stream",
                          (m["worker_stream_key"]
                           if role == "worker"
                           else m["verifier_stream_key"]) + ".jsonl")
    text = os.path.join(tmp, "%s.txt" % role)
    with open(text, "w") as fh:
        fh.write("package: P6R\naction: %s\nexecution: %s\nattempt: a1\n"
                 "step: %s\nclaim: %s\nartifacts: %s\n"
                 % (m["action_id"] if role == "worker"
                    else m["verify_action_id"],
                    m["execution_id"] if role == "worker"
                    else m["verify_execution_id"],
                    "worker-run" if role == "worker" else "verify-run",
                    os.path.join(tmp, "claims",
                                 (m["execution_id"] if role == "worker"
                                  else m["verify_execution_id"]) + ".json"),
                    os.path.join(tmp, "art")))
        fh.write("artifact: out.bin\npinned_input: x\n"
                 if role == "worker" else
                 "worker_claim: %s\ncheck: recompute-sha256\n"
                 % os.path.join(tmp, "claims",
                                m["execution_id"] + ".json"))
        fh.write("item: %s\n" % ("iT1" if role == "worker" else "iV1"))
    r = subprocess.run(
        [sys.executable, P5_FIXTURE, "--role", role, "--text-file", text,
         "--stream-file", stream, "--onset-dir",
         os.path.join(tmp, "onsets")],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def cb_args(db, timer="u-r14", qid="P6R", action="p6r-w1",
            execution="ex-test"):
    return [R3H, "--db", db, "timer-callback", "--timer", timer,
            "--qid-cb", qid, "--action", action, "--execution", execution]


def run_cb(args):
    return subprocess.run([sys.executable] + args, capture_output=True,
                          text=True, timeout=30,
                          cwd=os.path.join(SRC, "r3harness"))


VOLATILE = ("ingress-epoch", "ingress-boot", "ingress-last")


def stable(db):
    return {k: v for k, v in kv(db).items() if k not in VOLATILE}


def ledger_via_cli(tmp, qids_actions):
    """Direct-Driver ledger setup: {qid: [(action, duration_s)]} then lapse."""
    from driver import Driver
    from ingress import HostClock
    db = os.path.join(tmp, "fx.db")
    d = Driver(db, HostClock())
    for qid, acts in qids_actions.items():
        d.admit_authorize(qid)
        for action, dur in acts:
            d.start_dispatch(qid, action, duration_s=dur)
    d.close()
    return db


# T1 ------------------------------------------------------------------
def test_T1_two_qids_one_db_isolation_and_early_noop():
    tmp = mktree()
    db = ledger_via_cli(tmp, {"QA": [("a-A", 1)], "QB": [("a-B", 900)]})
    from driver import Driver
    from ingress import HostClock
    from host_adapter import HostAdapter
    d = Driver(db, HostClock())
    HostAdapter(d).register_execution("a-A", "ex-A", "t",
                                      "2026-09-23T00:00:00Z")
    HostAdapter(d).register_execution("a-B", "ex-B", "t",
                                      "2026-09-23T00:00:00Z")
    d.close()
    time.sleep(2.0)  # QA genuinely overdue; QB still valid
    r = run_cb(cb_args(db, qid="QA", action="a-A", execution="ex-A"))
    out = json.loads(r.stdout)
    assert out["decision"] in ("interrupted", "recovered"), out
    assert out.get("dedup") is False
    k = kv(db)
    assert k.get("handled:deadline:QA:a-A") == "handled-acked", k
    assert "handled:deadline:QB:a-B" not in k  # QB untouched
    r = run_cb(cb_args(db, qid="QB", action="a-B", execution="ex-B"))
    assert json.loads(r.stdout)["decision"] == "no-op-early"


def test_T1_foreign_db_fails_closed_no_writes():
    tmp = mktree()
    db1 = ledger_via_cli(tmp, {"P6C": [("a-C", 1)]})
    other = os.path.join(tmp, "other.db")
    from driver import Driver
    from ingress import HostClock
    d = Driver(other, HostClock())
    d.admit_authorize("P6X")
    d.start_dispatch("P6X", "a-X", duration_s=900)
    d.close()
    before1, beforeX = stable(db1), stable(other)
    time.sleep(2.0)
    r = run_cb(cb_args(other, qid="P6C", action="a-C", execution="ex-C"))
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_UNKNOWN_PACKAGE"
    assert stable(db1) == before1 and stable(other) == beforeX


def test_T1_wrong_execution_and_omitted_identity_fail_closed():
    tmp = mktree()
    db = ledger_via_cli(tmp, {"P6R": [("a-W", 900)]})
    from driver import Driver
    from ingress import HostClock
    from host_adapter import HostAdapter
    d = Driver(db, HostClock())
    HostAdapter(d).register_execution("a-W", "ex-real", "t",
                                      "2026-09-23T00:00:00Z")
    d.close()
    before = stable(db)
    r = run_cb(cb_args(db, qid="P6R", action="a-W",
                       execution="ex-forged"))
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_EXECUTION_MISMATCH"
    r = run_cb([R3H, "--db", db, "timer-callback", "--timer", "u",
                "--qid-cb", "P6R", "--execution", "ex-real"])
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_NO_IDENTITY"
    r = run_cb([R3H, "--db", db, "timer-callback", "--timer", "u",
                "--action", "a-W", "--execution", "ex-real"])
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_NO_IDENTITY"
    assert stable(db) == before  # zero writes on all three


# T2 ------------------------------------------------------------------
def test_T2_window_starts_at_verifier_dispatch_and_persists():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=60, verify_window_s=30,
                      escalation_window_s=10)
    manifest = setup_cli(tmp, plan)
    db = os.path.join(tmp, "fx.db")
    m = json.load(open(manifest))
    t0 = time.time()
    # Slow worker: end lands 12s after dispatch, beyond any old-style
    # t0-based escalation bound, inside the worker grant.
    prod = threading.Thread(target=produce,
                            args=("worker", tmp, manifest, 12.0))
    prod.start()
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    assert out.get("decision") == "nonterminal-continuation", out
    prod.join()
    assert not [k for k in kv(db) if k.startswith("r3v:")] \
        # no verifier dispatched yet: no window facts
    results = []
    bg = threading.Thread(
        target=lambda: results.append(r3cli(
            *run_args(tmp, plan, manifest, "reattach"), timeout=120)))
    bg.start()  # worker observed at once; verifier dispatched ~now
    produce("verifier", tmp, manifest, delay=8.0)  # inside 30s window
    bg.join(timeout=110)
    assert results, "reattach thread did not return"
    out = json.loads(results[0].stdout)
    assert out.get("decision") in ("transition-committed", "terminal-rest",
                                   "duplicate-end-ignored"), out
    facts = {k: v for k, v in kv(db).items() if k.startswith("r3v:")}
    base = "r3v:%s:%s:" % (m["verify_action_id"],
                           m["verify_execution_id"])
    assert facts, "verifier window facts persisted once"
    wdispatch = [v for k, v in kv(db).items()
                 if k.startswith("r3:") and k.endswith("dispatch_at")
                 and not k.startswith("r3v:")][0]
    assert facts[base + "dispatch_at"] > wdispatch  # window starts later
    assert facts[base + "effective_deadline"] == \
        facts[base + "verify_deadline"]  # no outer stop: min is deadline
    r = r3cli(*run_args(tmp, plan, manifest, "reattach"))
    assert json.loads(r.stdout)["decision"] == "duplicate-end-ignored"
    assert {k: v for k, v in kv(db).items() if k.startswith("r3v:")} \
        == facts  # window never restarted/extended
    assert time.time() - t0 < 110


def test_T2_window_expiry_is_bounded_recovery_with_evidence():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=900, verify_window_s=12,
                      escalation_window_s=10)
    manifest = setup_cli(tmp, plan)
    db = os.path.join(tmp, "fx.db")
    produce("worker", tmp, manifest)
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    assert out.get("reason") == "verifier-no-end", out
    assert out.get("decision") == "owned-recovery", out
    w = out.get("verifier_window", {})
    assert w["dispatch_at"] and w["verify_deadline"] \
        and w["effective_deadline"], out
    assert w["effective_deadline"] <= w["verify_deadline"]
    rows = [json.loads(l) for l in
            open(os.path.join(tmp, "latency.jsonl")) if l.strip()]
    assert any(r.get("outcome", "").startswith("owned-recovery")
               for r in rows), rows


# T3 ------------------------------------------------------------------
def test_T3_beyond_slice_continues_then_recovers_no_resend():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=900, verify_window_s=25,
                      escalation_window_s=30)
    manifest = setup_cli(tmp, plan)
    db = os.path.join(tmp, "fx.db")
    latpath = os.path.join(tmp, "latency.jsonl")
    prod = threading.Thread(target=produce,
                            args=("worker", tmp, manifest, 10.0))
    prod.start()  # work completes beyond the 8s slice, inside the grant
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    assert out.get("decision") == "nonterminal-continuation", out
    assert out.get("reason") == "grant-open-continue", out
    assert out.get("latency_samples") == 0
    assert not os.path.exists(latpath) or \
        os.path.getsize(latpath) == 0  # unconcluded: zero rows
    prod.join()
    r = r3cli(*run_args(tmp, plan, manifest, "reattach"))
    out = json.loads(r.stdout)
    # worker end consumed; verifier dispatched; no verifier staged so the
    # window (60s) honestly expires into bounded recovery, never success.
    assert out.get("reason") == "verifier-no-end", out
    sent = [k for k in kv(db) if k.startswith("outbox-sent:")]
    assert len(sent) == 2, sent  # worker + verifier, each exactly once


def test_T3_genuine_expiry_is_terminal_no_end():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=1)
    manifest = setup_cli(tmp, plan)
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    # Slice (2s) ends past the 1s grant: genuine expiry, terminal no-end.
    assert out.get("decision") == "owned-failure", out
    assert out.get("reason") == "no-end", out


# T4 ------------------------------------------------------------------
def test_T4_rows_count_real_executions_and_gate_rejects_synthetic():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=900, verify_window_s=60,
                      escalation_window_s=30)
    manifest = setup_cli(tmp, plan)
    produce("worker", tmp, manifest)
    prod = threading.Thread(target=produce,
                            args=("verifier", tmp, manifest, 3.0))
    prod.start()
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    prod.join()
    assert out.get("decision") in ("transition-committed", "terminal-rest"), \
        out
    rows = [json.loads(l) for l in
            open(os.path.join(tmp, "latency.jsonl")) if l.strip()]
    assert len(rows) == 2, rows  # ONE execution: worker + verifier rows
    assert {r["action"] for r in rows} == {"p6r-w1", "p6r-v1"}, rows
    assert not [r for r in rows
                if r.get("outcome") == "no-end-failure"], rows
    for row in rows:
        assert row.get("detected_at") and row.get("committed_at"), row
    r = r3cli(*run_args(tmp, plan, manifest, "reattach"))
    assert json.loads(r.stdout)["decision"] == "duplicate-end-ignored"
    rows2 = [json.loads(l) for l in
             open(os.path.join(tmp, "latency.jsonl")) if l.strip()]
    assert len(rows2) == 2, rows2  # repeat writes no extra rows
    # Synthetic fabricated row fails the gate explicitly.
    bad = os.path.join(tmp, "bad.jsonl")
    with open(bad, "w") as fh:
        fh.write(json.dumps({"action": "p6r-w1", "dispatch_at": None,
                             "detected_at": None, "committed_at": None,
                             "outcome": "no-end-failure"}) + "\n")
    r = r3cli("--manifest", manifest, "check-latency")
    assert r.returncode == 0, r.stdout  # real file still gates-hold
    # direct gate on a synthetic fabricated file via a temp manifest
    m2 = json.load(open(manifest))
    m2["latency_path"] = bad
    man2 = os.path.join(tmp, "manifest2.json")
    json.dump(m2, open(man2, "w"), sort_keys=True)
    r = r3cli("--manifest", man2, "check-latency")
    assert r.returncode == 3, r.stdout
    assert "E_BAD_SAMPLE" in r.stdout, r.stdout


def test_T4_missing_onset_is_incomplete_not_zero():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=900, verify_window_s=60,
                      escalation_window_s=30)
    manifest = setup_cli(tmp, plan)
    produce("worker", tmp, manifest)
    # Remove producer onset sidecars: timing unmeasurable, never zero.
    for f in os.listdir(os.path.join(tmp, "onsets")):
        os.remove(os.path.join(tmp, "onsets", f))
    prod = threading.Thread(target=produce,
                            args=("verifier", tmp, manifest, 3.0))
    prod.start()
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out = json.loads(r.stdout)
    prod.join()
    assert out.get("decision") in ("transition-committed", "terminal-rest"), \
        out
    r = r3cli("--manifest", manifest, "check-latency")
    assert r.returncode == 3, r.stdout
    assert "unmeasurable-incomplete" in r.stdout, r.stdout


def test_T1R_absent_execution_authority_rejects_no_effects_reopen_agrees():
    # Repair repro: otherwise-valid due current action but ABSENT
    # exec-current (missing fact NOT pre-registered) fails closed.
    tmp = mktree()
    db = ledger_via_cli(tmp, {"P6R": [("a-W", 1)]})
    time.sleep(2.0)  # genuinely overdue
    before = stable(db)
    r = run_cb(cb_args(db, qid="P6R", action="a-W", execution="ex-claim"))
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_NO_EXECUTION_AUTHORITY"
    assert stable(db) == before  # no stop/wake, no ledger/KV mutation
    # Empty and malformed persisted identities also reject.
    from driver import Driver
    from ingress import HostClock
    for bad in ("", "   "):
        d = Driver(db, HostClock())
        d._kv_put("exec-current:a-W", bad)
        d.close()
        r = run_cb(cb_args(db, qid="P6R", action="a-W",
                           execution="ex-claim"))
        assert json.loads(r.stdout)["error"] == "E_NO_EXECUTION_AUTHORITY"
    d = Driver(db, HostClock())
    d._kv_put("exec-current:a-W", "SUPERSEDED->a-N")
    d.close()
    r = run_cb(cb_args(db, qid="P6R", action="a-W", execution="ex-claim"))
    assert json.loads(r.stdout)["error"] == "E_SUPERSEDED_ACTION"
    # Reopen agrees: still rejects, still no effects.
    r = run_cb(cb_args(db, qid="P6R", action="a-W", execution="ex-claim"))
    assert r.returncode == 3, r.stdout
    # Genuine registered due execution still interrupts exactly once.
    d = Driver(db, HostClock())
    from host_adapter import HostAdapter
    HostAdapter(d).register_execution("a-W", "ex-real", "t",
                                      "2026-09-23T00:00:00Z")
    d.close()
    r = run_cb(cb_args(db, qid="P6R", action="a-W", execution="ex-real"))
    out = json.loads(r.stdout)
    assert out["decision"] in ("interrupted", "recovered"), out
    assert out.get("dedup") is False
    r = run_cb(cb_args(db, qid="P6R", action="a-W", execution="ex-real"))
    out = json.loads(r.stdout)
    assert out["decision"] == "already-handled" \
        and out.get("dedup") is True
