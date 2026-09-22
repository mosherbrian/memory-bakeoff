"""P6-r7 host-branch tests: the SAME no-overlay entrypoint branch with
injected boundaries only (test-signed plan/binding/registry, tmp sockets,
test executables, test producer-boundary harness). No real seats/messages/
restarts/timers; live registry/socket roots untouched. Real-seat execution
stays pending Stage C."""
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time

import pytest

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
SCRIPT = os.path.join(SRC, "stagec_host.py")
CANDIDATE_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
                 "P6-r5-launch-binding/src")
P6R6_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
            "P6-r6-live-preparation/src")
REAL_PLAN = os.path.join(PKG, "stagec-plan.json")
WLANE = "/home/bmosher/.config/agent-deck/acp-go"
VLANE = "/home/bmosher/.config/agent-deck/acp-go-deepseek"

sys.path.insert(0, SRC)
import stagec_host as sh
from stagec_host import StageCFault


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cli(*args):
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True, timeout=180,
                          cwd=PKG)


@pytest.fixture()
def env():
    e = _make_env()
    yield e
    for s in e["socks"]:
        s.close()


def _make_env():
    tmp = tempfile.mkdtemp(prefix="p6r7-")
    for d in ("stream", "sock", "msgs", "claims", "art", "onsets", "bin",
              "workdirs"):
        os.makedirs(os.path.join(tmp, d))
    wsid, vsid = "t7-worker-001", "t7-verifier-001"
    wt, vt = "p6-fixture-worker-t7", "p6-fixture-verifier-t7"
    socks = []
    for sid in (wsid, vsid):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(os.path.join(tmp, "sock", sid + ".sock"))
        socks.append(s)
    ino = {sid: os.stat(os.path.join(tmp, "sock", sid + ".sock")).st_ino
           for sid in (wsid, vsid)}
    # test executables: wake records + delivers; systemd shims inert
    wake = os.path.join(tmp, "bin", "wake")
    with open(wake, "w") as fh:
        fh.write("#!/bin/bash\n"
                 "echo \"CALL wake $1\" >> \"%s/trace.log\"\n"
                 "n=$(ls \"%s/msgs\" 2>/dev/null | wc -l)\n"
                 "printf '%%s' \"$2\" > \"%s/msgs/to-$1-$n.txt\"\n"
                 "if [ \"$2\" = \"probe-ambiguous\" ]; then\n"
                 "  echo \"garbage-no-receipt\"; exit 0\n"
                 "fi\n"
                 "mode=$(cat \"%s/mode\" 2>/dev/null || echo started)\n"
                 "if [ \"$mode\" = \"queued-first\" ] && [ \"$1\" = \"%s\" ]"
                 " && [ ! -f \"%s/seen-$1\" ]; then\n"
                 "  touch \"%s/seen-$1\"\n"
                 "  echo \"wake: $1 -> queued\"; exit 3\n"
                 "fi\n"
                 "echo \"wake: $1 -> started\"; exit 0\n"
                 % (tmp, tmp, tmp, tmp, wt, tmp, tmp))
    srun = os.path.join(tmp, "bin", "systemd-run")
    sctl = os.path.join(tmp, "bin", "systemctl")
    open(srun, "w").write("#!/bin/bash\nexit 0\n")
    open(sctl, "w").write("#!/bin/bash\necho \"ActiveState=inactive\"\n"
                          "echo \"SubState=dead\"\nexit 0\n")
    for f in (wake, srun, sctl):
        os.chmod(f, 0o755)
    open(os.path.join(tmp, "mode"), "w").write("started")
    open(os.path.join(tmp, "trace.log"), "w").close()
    plan = dict(json.load(open(REAL_PLAN)))
    plan["host_commands"] = {"wake": wake, "systemd_run": srun,
                             "systemctl": sctl}
    plan["live_run_dirs"] = {"root": tmp, "claims": tmp + "/claims",
                             "art": tmp + "/art", "onsets": tmp + "/onsets",
                             "msgs": tmp + "/msgs", "db": tmp + "/fixture.db",
                             "latency": tmp + "/latency.jsonl",
                             "witness": tmp + "/witness-rows.jsonl"}
    planp = os.path.join(tmp, "plan.json")
    json.dump(plan, open(planp, "w"), sort_keys=True)
    binding = {"launcher_source": "live-agent-deck", "profile": "campaign4",
               "worker": {"session_id": wsid, "title": wt, "role_lane": WLANE,
                          "launch_command": WLANE,
                          "workdir": tmp + "/workdirs/" + wt,
                          "producer_root": tmp + "/stream",
                          "stream_path": tmp + "/stream/" + wsid + ".jsonl",
                          "socket": tmp + "/sock/" + wsid + ".sock",
                          "incarnation": {"ino": ino[wsid], "mtime": 1.0}},
               "verifier": {"session_id": vsid, "title": vt,
                            "role_lane": VLANE, "launch_command": VLANE,
                            "workdir": tmp + "/workdirs/" + vt,
                            "producer_root": tmp + "/stream",
                            "stream_path": tmp + "/stream/" + vsid + ".jsonl",
                            "socket": tmp + "/sock/" + vsid + ".sock",
                            "incarnation": {"ino": ino[vsid],
                                            "mtime": 1.0}}}
    for sid in (wsid, vsid):
        os.makedirs(os.path.dirname(
            binding["worker" if sid == wsid else "verifier"]
            ["workdir"]), exist_ok=True)
    bindp = os.path.join(tmp, "binding.json")
    json.dump(binding, open(bindp, "w"), sort_keys=True)
    reg = [{"id": wsid, "title": wt, "profile": "campaign4",
            "command": WLANE, "path": tmp + "/workdirs/" + wt,
            "status": "idle"},
           {"id": vsid, "title": vt, "profile": "campaign4",
            "command": VLANE, "path": tmp + "/workdirs/" + vt,
            "status": "idle"}]
    regp = os.path.join(tmp, "registry.json")
    json.dump(reg, open(regp, "w"))
    cfg = os.path.join(tmp, "execution-config.json")
    sig = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern", "purpose": "stagec-task",
               "plan_sha256": sha(planp),
               "binding_sha256": sha(bindp)}, open(sig, "w"))
    r = cli("derive-config", "--plan", planp, "--binding", bindp,
            "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    json.dump({"signer": "tern", "purpose": "stagec-task",
               "plan_sha256": sha(planp), "binding_sha256": sha(bindp),
               "config_sha256": sha(cfg),
               "stagec_entry_sha256": sha(SCRIPT),
               "candidate_harness_sha256":
               "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142"},
              open(sig, "w"))
    return {"tmp": tmp, "plan": planp, "binding": bindp, "cfg": cfg,
            "sig": sig, "reg": regp, "wsid": wsid, "vsid": vsid, "wt": wt,
            "vt": vt, "socks": socks}


def producers(env, hold=(), tamper=False, stop=None):
    """Test producer-boundary harness (plays the seat role OUTSIDE the
    tool): fresh producers seeing only dispatched texts + named files."""
    tmp = env["tmp"]
    done = set()

    def _loop():
        while (stop or (lambda: True))() and not \
                ({env["wt"], env["vt"]} - set(hold) <= done):
            for seat, role, sid in ((env["wt"], "worker", env["wsid"]),
                                    (env["vt"], "verifier", env["vsid"])):
                if seat in done or seat in hold:
                    continue
                files = sorted(f for f in os.listdir(tmp + "/msgs")
                               if f.startswith("to-" + seat + "-"))
                if not files:
                    time.sleep(0.2)
                    continue
                cmd = [sys.executable, CANDIDATE_SRC + "/fixture_worker.py",
                       "--role", role, "--text-file",
                       tmp + "/msgs/" + files[-1], "--stream-file",
                       tmp + "/stream/" + sid + ".jsonl", "--onset-dir",
                       tmp + "/onsets"]
                p = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=60)
                assert p.returncode == 0, p.stdout + p.stderr
                done.add(seat)
                if tamper and role == "worker":
                    import glob as _g
                    for a in _g.glob(tmp + "/art/*"):
                        open(a, "wb").write(b"tampered-by-fixture-fault")
            time.sleep(0.2)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


def test_h1_parent_keyerror_reproducer():
    sys.path.insert(0, P6R6_SRC)
    import stagec_entry as parent
    plan = {"actions": {"worker": "p6c-w1", "verifier": "p6c-v1"},
            "timer_unit": "p6-stagec-handoff-1.timer", "live_run_dirs": {}}
    config = {"worker": {"title": "w"}, "verifier": {"title": "v"}}
    with pytest.raises(KeyError) as e:
        parent._candidate_plan(config, plan,
                               parent._live_dirs(plan))
    assert "wake_shim" in str(e.value)  # pinned H1.5 reproducer, read-only


def test_h1_missing_host_path_owned(env):
    plan = json.load(open(env["plan"]))
    plan["host_commands"] = {"wake": "/nonexistent/wake"}
    badp = os.path.join(env["tmp"], "badplan.json")
    json.dump(plan, open(badp, "w"))
    with pytest.raises(StageCFault) as e:
        sh._live_dirs(plan)
    assert e.value.code == "E_HOST_PATH"  # owned, never KeyError


def test_h2_gate_negatives(env):
    base = json.load(open(env["sig"]))

    def gate_with(sigedit=None, regedit=None, cfgedit=None):
        sig = dict(base)
        sig.update(sigedit or {})
        sp = os.path.join(env["tmp"], "s-neg.json")
        json.dump(sig, open(sp, "w"))
        if regedit is not None:
            json.dump(regedit, open(env["reg"], "w"))
        cfgp = env["cfg"]
        if cfgedit:
            man = json.load(open(cfgp))
            cfgedit(man)
            cfgp = os.path.join(env["tmp"], "c-neg.json")
            json.dump(man, open(cfgp, "w"))
            s2 = dict(sig)
            s2["config_sha256"] = sha(cfgp)
            json.dump(s2, open(sp, "w"))
        return cli("gate", "--config", cfgp, "--plan", env["plan"],
                   "--signatures", sp, "--registry-file", env["reg"])
    r = gate_with(sigedit={"purpose": "preparation"})
    assert r.returncode == 3 and "E_NO_SIGNATURE" in r.stdout
    r = gate_with(sigedit={"stagec_entry_sha256": "changed"})
    assert r.returncode == 3 and "E_TOOL_CHANGED" in r.stdout
    reg = json.load(open(env["reg"]))
    reg[0]["status"] = "stopped"
    r = gate_with(regedit=reg)
    assert r.returncode == 3 and "E_EXPIRED" in r.stdout, r.stdout
    reg = json.load(open(env["reg"]))
    for s in reg:
        s["status"] = "idle"
    json.dump(reg, open(env["reg"], "w"))
    reg[1]["command"] = "/wrong/lane"
    r = gate_with(regedit=reg)
    assert r.returncode == 3 and "E_MISMATCH" in r.stdout, r.stdout
    reg[1]["command"] = VLANE
    json.dump(reg, open(env["reg"], "w"))
    man = json.load(open(env["binding"]))
    man["worker"]["socket"] = env["tmp"] + "/sock/nonexistent.sock"
    badb = os.path.join(env["tmp"], "bad-binding.json")
    json.dump(man, open(badb, "w"))
    cfgp = os.path.join(env["tmp"], "c-rebound.json")
    sig = dict(base, binding_sha256=sha(badb))
    sp = os.path.join(env["tmp"], "s-rebound.json")
    json.dump(sig, open(sp, "w"))
    r = cli("derive-config", "--plan", env["plan"], "--binding", badb,
            "--signatures", sp, "--out", cfgp)
    assert r.returncode == 0, r.stdout
    sig["config_sha256"] = sha(cfgp)
    json.dump(sig, open(sp, "w"))
    r = cli("gate", "--config", cfgp, "--plan", env["plan"], "--signatures",
            sp, "--registry-file", env["reg"])
    assert r.returncode == 3 and "E_EXPIRED" in r.stdout, r.stdout


def _run(env, case, hold=(), tamper=False, mode="started"):
    open(os.path.join(env["tmp"], "mode"), "w").write(mode)
    t = producers(env, hold=hold, tamper=tamper)
    try:
        r = cli("run-case", "--config", env["cfg"], "--plan", env["plan"],
                "--signatures", env["sig"], "--case", case,
                "--registry-file", env["reg"],
                "--out", os.path.join(env["tmp"], "r-%s.json" % case))
    finally:
        t.join(timeout=5)
    return r


def test_h4_positive_no_overlay_trace(env):
    r = _run(env, "positive-handoff")
    assert r.returncode == 0, r.stdout
    body = json.loads(r.stdout)
    assert body["sends"] == {"worker": 1, "verifier": 1}, body
    assert body["timecheck"] == "accept", body
    assert body["overlay"] is False
    receipt = json.load(open(os.path.join(env["tmp"],
                                          "r-positive-handoff.json")))
    assert receipt["settled_actions"] == ["p6c-v1", "p6c-w1"], receipt
    assert receipt["gate"]["registry_source"].startswith("injected")


def test_h4_lost_completion_and_failed_verification():
    env = _make_env()
    try:
        r = _run(env, "lost-completion", hold={env["vt"]})
        assert r.returncode == 0, r.stdout
        assert json.loads(r.stdout)["timecheck"] == "accept-open", r.stdout
    finally:
        for s in env["socks"]:
            s.close()
    env = _make_env()
    try:
        r = _run(env, "failed-verification", tamper=True)
        assert r.returncode == 0, r.stdout
        assert json.loads(r.stdout)["timecheck"] == "accept-open", r.stdout
        assert "COMPLETE" not in r.stdout
    finally:
        for s in env["socks"]:
            s.close()


def test_h4_queued_restart_and_quiet():
    env = _make_env()
    try:
        r = _run(env, "queued-ambiguous-restart", mode="queued-first")
        assert r.returncode == 0, r.stdout
        body = json.loads(r.stdout)
        assert body["sends"] == {"worker": 1, "verifier": 1}, body
        assert body["timecheck"] == "accept", body
    finally:
        for s in env["socks"]:
            s.close()
    env = _make_env()
    try:
        r = _run(env, "quiet-rest")
        assert r.returncode == 0, r.stdout
        assert json.loads(r.stdout)["timecheck"] == "accept", r.stdout
    finally:
        for s in env["socks"]:
            s.close()


def test_h3_wrong_execution_and_omitted_ack():
    env = _make_env()
    try:
        _run(env, "positive-handoff")
        tmp = env["tmp"]
        lat = tmp + "/latency.jsonl"
        wit = tmp + "/witness-rows.jsonl"
        rec = tmp + "/r-positive-handoff.json"
        rows = [json.loads(l) for l in open(wit) if l.strip()]
        for r in rows:
            r["execution"] = "ex-old-stale"
        open(wit, "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
        r = cli("timecheck", "--config", env["cfg"], "--latency", lat,
                "--witness", wit, "--receipt", rec)
        assert r.returncode == 3 and "wrong-execution" in r.stdout, r.stdout
    finally:
        for s in env["socks"]:
            s.close()
    env = _make_env()
    try:
        _run(env, "positive-handoff")
        tmp = env["tmp"]
        lat = tmp + "/latency.jsonl"
        wit = tmp + "/witness-rows.jsonl"
        rec = tmp + "/r-positive-handoff.json"
        rows = [json.loads(l) for l in open(wit) if l.strip()]
        for r in rows:
            r["ack"] = False
        open(wit, "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
        r = cli("timecheck", "--config", env["cfg"], "--latency", lat,
                "--witness", wit, "--receipt", rec)
        assert r.returncode == 3 and "missing ack" in r.stdout, r.stdout
    finally:
        for s in env["socks"]:
            s.close()


def test_h4_rollback_archives_then_disables(env):
    _run(env, "positive-handoff")
    arc = os.path.join(env["tmp"], "archive")
    r = cli("rollback", "--config", env["cfg"], "--root-dir", env["tmp"],
            "--archive-dir", arc)
    assert r.returncode == 0 and "witness_archived" in r.stdout, r.stdout
    assert os.path.exists(os.path.join(arc, "rollback-report.json"))
