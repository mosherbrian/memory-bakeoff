"""Amendment-2 reconcile: run_fixture/reopen vs faithful host facts.

Exact CLI --live run-fixture/reattach with file-backed systemd stubs:
duplicate create rejects, show reports actual units, stop removes.
Injected only: private tmp dirs/DBs, stub scripts, no real services.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
R9 = os.path.join(HERE, "..")
SRC = os.path.join(R9, "src")
R3CLI = os.path.join(SRC, "r3harness", "harness.py")
sys.path.insert(0, os.path.join(SRC, "r3harness"))


def sha(p):
    import hashlib
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write_stubs(tmp):
    binp = os.path.join(tmp, "bin")
    os.makedirs(binp, exist_ok=True)
    units = os.path.join(tmp, "units.json")
    log = os.path.join(tmp, "systemd.log")
    json.dump([], open(units, "w"))
    open(log, "w").write("")
    run = os.path.join(binp, "systemd-run")
    with open(run, "w") as fh:
        fh.write(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "units = os.environ['P6R9_UNITS']\n"
            "log = os.environ['P6R9_SYSLOG']\n"
            "cur = json.load(open(units))\n"
            "unit = [a.split('=', 1)[1] for a in sys.argv\n"
            "        if a.startswith('--unit=')][0]\n"
            "open(log, 'a').write('create ' + unit + '\\n')\n"
            "if unit in cur:\n"
            "    sys.stderr.write('unit already exists')\n"
            "    sys.exit(1)\n"
            "cur.append(unit)\n"
            "json.dump(cur, open(units, 'w'))\n")
    ctl = os.path.join(binp, "systemctl")
    with open(ctl, "w") as fh:
        fh.write(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "units = os.environ['P6R9_UNITS']\n"
            "log = os.environ['P6R9_SYSLOG']\n"
            "if os.environ.get('P6R9_FAIL_QUERY') and 'show' in sys.argv:\n"
            "    sys.stderr.write('bus unavailable')\n"
            "    sys.exit(1)\n"
            "if 'show' in sys.argv:\n"
            "    unit = sys.argv[sys.argv.index('show') + 1]\n"
            "    cur = json.load(open(units))\n"
            "    st = 'active' if unit in cur else 'inactive'\n"
            "    sys.stdout.write('ActiveState=%s\\nSubState=%s\\n'\n"
            "                     % (st, 'running' if st == 'active'\n"
            "                        else 'dead'))\n"
            "    sys.exit(0)\n"
            "open(log, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
            "cur = json.load(open(units))\n"
            "for a in sys.argv:\n"
            "    if a.endswith('.timer') and a in cur:\n"
            "        cur.remove(a)\n"
            "json.dump(cur, open(units, 'w'))\n")
    os.chmod(run, 0o755)
    os.chmod(ctl, 0o755)
    return run, ctl


def write_plan(tmp, run, ctl, wait_s=2, duration_s=900):
    plan = {"fixture_id": "p6-r9-reconcile", "package_id": "P6R",
            "worker_action": "p6r-w1", "verify_action": "p6r-v1",
            "seats": {"fixture_seats": ["s-w", "s-v"]},
            "allowlist": {"seats": ["s-w", "s-v"],
                          "timer_units": {"p6r-w1": "u-r3-test.timer"},
                          "wake_path": "/bin/true",
                          "systemd_run": run,
                          "systemctl": ctl},
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
    tmp = tempfile.mkdtemp(prefix="p6r9rec-")
    for d in ("stream", "claims", "art", "onsets"):
        os.makedirs(os.path.join(tmp, d))
    run, ctl = write_stubs(tmp)
    return tmp, run, ctl


def r3cli(env, *args):
    e = dict(os.environ)
    e.update(env)
    return subprocess.run([sys.executable, R3CLI] + list(args),
                          capture_output=True, text=True, timeout=120,
                          cwd=os.path.join(SRC, "r3harness"), env=e)


def setup_cli(env, tmp, plan):
    manifest = os.path.join(tmp, "manifest.json")
    r = r3cli(env, "--plan", plan, "--manifest", manifest, "--session",
              "s", "--stream-key", "sk", "--worker-stream-key", "wsk",
              "--verifier-stream-key", "vsk", "setup")
    assert r.returncode == 0, r.stdout + r.stderr
    return manifest


def run_args(tmp, plan, manifest, cmd):
    return ["--live", "--plan", plan, "--plan-hash", sha(plan),
            "--allowlist-seat", "s-w", "--allowlist-seat", "s-v",
            "--db", os.path.join(tmp, "fx.db"), "--manifest", manifest,
            "--claims", os.path.join(tmp, "claims"), "--qid", "P6R", cmd]


def produce(tmp, manifest):
    m = json.load(open(manifest))
    stream = os.path.join(tmp, "stream", m["worker_stream_key"] + ".jsonl")
    text = os.path.join(tmp, "worker.txt")
    with open(text, "w") as fh:
        fh.write("package: P6R\naction: %s\nexecution: %s\nattempt: a1\n"
                 "step: worker-run\nclaim: %s\nartifacts: %s\n"
                 "artifact: out.bin\npinned_input: x\nitem: iT1\n"
                 % (m["action_id"], m["execution_id"],
                    os.path.join(tmp, "claims", m["execution_id"] + ".json"),
                    os.path.join(tmp, "art")))
    r = subprocess.run(
        [sys.executable,
         "/home/bmosher/memory-bake-off/campaign4/packages/"
         "P6-r5-launch-binding/src/fixture_worker.py", "--role", "worker",
         "--text-file", text, "--stream-file", stream, "--onset-dir",
         os.path.join(tmp, "onsets")],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def creates(tmp):
    return [l for l in open(os.path.join(tmp, "systemd.log")).read()
            .splitlines() if l.startswith("create ")]


def kv(db):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try:
        return dict(con.execute("select key, value from driver_kv")
                    .fetchall())
    finally:
        con.close()


def env_for(tmp):
    return {"P6R9_UNITS": os.path.join(tmp, "units.json"),
            "P6R9_SYSLOG": os.path.join(tmp, "systemd.log")}


def test_reattach_reuses_matching_host_timer_no_recreate():
    tmp, run, ctl = mktree()
    env = env_for(tmp)
    plan = write_plan(tmp, run, ctl)
    manifest = setup_cli(env, tmp, plan)
    db = os.path.join(tmp, "fx.db")
    r = r3cli(env, *run_args(tmp, plan, manifest, "run-fixture"))
    assert json.loads(r.stdout).get("reason") == "no-end", r.stdout
    assert creates(tmp) == ["create u-r3-test.timer"]
    produce(tmp, manifest)
    r = r3cli(env, *run_args(tmp, plan, manifest, "reattach"))
    out = json.loads(r.stdout)
    assert out.get("reason") == "verifier-no-end", out
    # existing matching host timer reused: still exactly one create,
    # worker + verifier each sent exactly once.
    assert creates(tmp) == ["create u-r3-test.timer"]
    msgs = [k for k in kv(db) if k.startswith("msg:")]
    assert len(msgs) == 2


def test_reattach_reconstructs_missing_host_timer_bounded():
    tmp, run, ctl = mktree()
    env = env_for(tmp)
    plan = write_plan(tmp, run, ctl)
    manifest = setup_cli(env, tmp, plan)
    r = r3cli(env, *run_args(tmp, plan, manifest, "run-fixture"))
    assert json.loads(r.stdout).get("reason") == "no-end", r.stdout
    # host loses the timer out from under the kv record
    json.dump([], open(os.path.join(tmp, "units.json"), "w"))
    produce(tmp, manifest)
    r = r3cli(env, *run_args(tmp, plan, manifest, "reattach"))
    out = json.loads(r.stdout)
    assert out.get("reason") == "verifier-no-end", out
    # reconstructed for the remaining grant: exactly one more create,
    # no duplicate sends beyond worker+verifier.
    assert creates(tmp) == ["create u-r3-test.timer"] * 2
    db = os.path.join(tmp, "fx.db")
    assert len([k for k in kv(db) if k.startswith("msg:")]) == 2


def test_reattach_conflicting_deadline_owned_failure():
    tmp, run, ctl = mktree()
    env = env_for(tmp)
    plan = write_plan(tmp, run, ctl)
    manifest = setup_cli(env, tmp, plan)
    db = os.path.join(tmp, "fx.db")
    r = r3cli(env, *run_args(tmp, plan, manifest, "run-fixture"))
    assert json.loads(r.stdout).get("reason") == "no-end", r.stdout
    con = sqlite3.connect(db)
    try:
        (raw,) = con.execute(
            "select value from driver_kv where key='timer-arm:u-r3-test'"
            ).fetchone()
        rec = json.loads(raw)
        rec["deadline"] = "2030-01-01T00:00:00Z"
        con.execute("update driver_kv set value=? where key=?",
                    (json.dumps(rec, sort_keys=True),
                     "timer-arm:u-r3-test"))
        con.commit()
    finally:
        con.close()
    produce(tmp, manifest)
    r = r3cli(env, *run_args(tmp, plan, manifest, "reattach"))
    out = json.loads(r.stdout)
    assert out.get("decision") == "owned-failure", out
    assert "E_TIMER_CONFLICT" in out.get("reason", ""), out
    # conflicting unit never hijacked: no second create.
    assert creates(tmp) == ["create u-r3-test.timer"]


def test_reattach_query_failure_owned_failure():
    tmp, run, ctl = mktree()
    env = env_for(tmp)
    plan = write_plan(tmp, run, ctl)
    manifest = setup_cli(env, tmp, plan)
    r = r3cli(env, *run_args(tmp, plan, manifest, "run-fixture"))
    assert json.loads(r.stdout).get("reason") == "no-end", r.stdout
    produce(tmp, manifest)
    env2 = dict(env, P6R9_FAIL_QUERY="1")
    r = r3cli(env2, *run_args(tmp, plan, manifest, "reattach"))
    out = json.loads(r.stdout)
    assert out.get("decision") == "owned-failure", out
    assert "E_TIMER_QUERY" in out.get("reason", ""), out
