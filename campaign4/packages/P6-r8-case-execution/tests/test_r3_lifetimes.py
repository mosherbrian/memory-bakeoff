"""P6-r8 R3 tests: production deadline calculation + actual CLI
reattach/notification path with controlled clock/boundaries. Late
completion after the old 8s-style cutoff is handled once with no second
send; real grant expiry escalates boundedly without extension. First runs
are behavior-identical to the pinned parent. Injected effects only."""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

import pytest

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
R3H = os.path.join(SRC, "r3harness", "harness.py")
PARENT_H = ("/home/bmosher/memory-bake-off/campaign4/packages/"
            "P6-r5-launch-binding/src/harness.py")
CANDIDATE_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
                 "P6-r5-launch-binding/src")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def r3cli(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, R3H] + list(args),
                          capture_output=True, text=True, timeout=120,
                          cwd=PKG, env=env)


def write_plan(tmp, wait_s=2, duration_s=900):
    plan = {"fixture_id": "p6-r3-late", "package_id": "P6R",
            "worker_action": "p6r-w1", "verify_action": "p6r-v1",
            "seats": {"fixture_seats": ["s-w", "s-v"]},
            "allowlist": {"seats": ["s-w", "s-v"],
                          "timer_units": {"p6r-w1": "u-r3-test.timer"},
                          "wake_path": "/bin/true",
                          "systemd_run": "/bin/true",
                          "systemctl": "/bin/true"},
            "bounds": {"duration_s": duration_s, "verify_window_s": 600,
                       "wait_s": wait_s, "escalation_window_s": 120,
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
            "authorized_dispositions": [],
            "routes": {"p6r-v1": "s-v", "p6r-w1": "s-w"}}
    path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(path, "w"), sort_keys=True)
    return path


def mktree():
    tmp = tempfile.mkdtemp(prefix="p6r3-")
    for d in ("stream", "claims", "art", "onsets"):
        os.makedirs(os.path.join(tmp, d))
    return tmp


def setup_cli(tmp, plan):
    manifest = os.path.join(tmp, "manifest.json")
    r = r3cli("--plan", plan, "--manifest", manifest, "--session", "s",
              "--stream-key", "sk", "--worker-stream-key", "wsk",
              "--verifier-stream-key", "vsk", "setup")
    assert r.returncode == 0, r.stdout + r.stderr
    return manifest


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
        [sys.executable, CANDIDATE_SRC + "/fixture_worker.py", "--role",
         role, "--text-file", text, "--stream-file", stream, "--onset-dir",
         os.path.join(tmp, "onsets")],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def run_args(tmp, plan, manifest, cmd):
    return ["--live", "--plan", plan, "--plan-hash", sha(plan),
            "--allowlist-seat", "s-w", "--allowlist-seat", "s-v",
            "--db", os.path.join(tmp, "fx.db"), "--manifest", manifest,
            "--claims", os.path.join(tmp, "claims"), "--qid", "P6R", cmd]


def test_r3_late_completion_once_no_resend():
    tmp = mktree()
    plan = write_plan(tmp)
    manifest = setup_cli(tmp, plan)
    db = os.path.join(tmp, "fx.db")
    r = r3cli(*run_args(tmp, plan, manifest, "run-fixture"))
    out1 = json.loads(r.stdout)
    assert out1.get("reason") == "no-end", out1  # past 2s cutoff, grant open
    kv1 = kv(db)
    assert sum(1 for k in kv1 if k.startswith("msg:")) == 1  # worker sent
    produce("worker", tmp, manifest)  # late completion, before reattach
    r = r3cli(*run_args(tmp, plan, manifest, "reattach"))
    out2 = json.loads(r.stdout)
    # worker end consumed exactly once; verifier wait honestly expires
    # (no verifier end staged) into owned recovery — never false success.
    assert out2.get("reason") == "verifier-no-end", out2
    kv2 = kv(db)
    msgs = [k for k in kv2 if k.startswith("msg:")]
    assert len(msgs) == 2  # worker + verifier oids, each sent exactly once
    sent_before = {k: v for k, v in kv1.items()
                   if k.startswith("outbox-sent:")}
    sent_after = {k: v for k, v in kv2.items()
                  if k.startswith("outbox-sent:")}
    assert len(sent_before) == 1 and len(sent_after) == 2
    for k, v in sent_before.items():
        assert sent_after[k] == v  # same worker identity, never resent
    m = json.load(open(manifest))
    claim = json.load(open(os.path.join(tmp, "claims",
                                        m["execution_id"] + ".json")))
    assert claim["execution"] == m["execution_id"]
    assert claim["outcome"] == "completed"


def test_r3_expiry_escalates_bounded_no_extension():
    tmp = mktree()
    plan = write_plan(tmp, wait_s=2, duration_s=30)
    manifest = setup_cli(tmp, plan)
    db = os.path.join(tmp, "fx.db")
    script = os.path.join(tmp, "expiry_probe.py")
    with open(script, "w") as fh:
        fh.write(
            "import json, sys\n"
            "sys.path.insert(0, %r)\n"
            "from driver import Driver, FakeClock, FakeExternalWorld\n"
            "from host_adapter import (HostAdapter, FakeWakeTransport,\n"
            "                          HostTimerService)\n"
            "from types import SimpleNamespace as _NS\n"
            "import harness as h\n"
            "tmp = %r\n"
            "man = json.load(open(%r))\n"
            "w = FakeExternalWorld(tmp + '/world.json')\n"
            "clk = FakeClock('2026-09-22T04:00:00Z')\n"
            "d = Driver(tmp + '/fx.db', clk, w)\n"
            "t = FakeWakeTransport()\n"
            "ok = lambda cmd, **kw: _NS(returncode=0, stdout='', stderr='')\n"
            "ts = HostTimerService(d.kv.get, d._kv_put, enabled=True,\n"
            "                      allowlist=('u-r3-test.timer',),\n"
            "                      runner=ok)\n"
            "a = HostAdapter(d, clock=clk, transport=t, timers=ts)\n"
            "out1 = h.run_fixture(a, man, tmp + '/claims', 'P6R')\n"
            "calls1 = len(t.calls)\n"
            "facts_before = {k: d.kv.get(k) for k in d.kv.keys()\n"
            "                if k.startswith('r3:')}\n"
            "clk.now = '2026-09-22T04:40:00Z'\n"
            "out2 = h.run_fixture(a, man, tmp + '/claims', 'P6R',\n"
            "                     resume=True)\n"
            "facts_after = {k: d.kv.get(k) for k in d.kv.keys()\n"
            "               if k.startswith('r3:')}\n"
            "print(json.dumps({'first': out1.get('reason'),\n"
            "                'second': out2, 'calls_delta': len(t.calls) -\n"
            "                calls1, 'new_kinds': [k for _, _, k in t.calls\n"
            "                [calls1:]], 'facts_same': facts_before ==\n"
            "                facts_after, 'facts': facts_after},\n"
            "               sort_keys=True))\n"
            % (os.path.join(SRC, "r3harness"), tmp, manifest))
    r = subprocess.run([sys.executable, script], capture_output=True,
                       text=True, timeout=120, cwd=tmp)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.loads(r.stdout)
    assert res["first"] == "no-end", res
    assert res["second"]["reason"] == "grant-expired", res
    assert res["second"]["decision"] == "owned-recovery", res
    assert res["calls_delta"] == 1 and res["new_kinds"] == ["escalation"], \
        res  # only the bounded escalation send; zero fixture resends
    assert res["facts_same"] is True  # deadlines never extended


def test_r3_first_run_identical_to_parent():
    for harness_path, tag in ((CANDIDATE_SRC + "/harness.py", "parent"),
                              (R3H, "r3")):
        tmp = mktree()
        plan = write_plan(tmp)
        man = os.path.join(tmp, "manifest.json")
        r = subprocess.run(
            [sys.executable, harness_path, "--plan", plan, "--manifest",
             man, "--session", "s", "--stream-key", "sk",
             "--worker-stream-key", "wsk", "--verifier-stream-key", "vsk",
             "setup"],
            capture_output=True, text=True, timeout=60, cwd=tmp)
        assert r.returncode == 0, (tag, r.stdout + r.stderr)
        produce("worker", tmp, man)
        r = subprocess.run(
            [sys.executable, harness_path, "--live", "--plan", plan,
             "--plan-hash", sha(plan), "--allowlist-seat", "s-w",
             "--allowlist-seat", "s-v", "--db", os.path.join(tmp, "fx.db"),
             "--manifest", man, "--claims", os.path.join(tmp, "claims"),
             "--qid", "P6R", "run-fixture"],
            capture_output=True, text=True, timeout=120, cwd=tmp)
        out = json.loads(r.stdout)
        # verifier end never staged: owned verifier-no-end recovery, same
        # shape in both implementations
        assert out.get("reason") == "verifier-no-end", (tag, out)
        assert out.get("latency_samples", 0) >= 1, (tag, out)
