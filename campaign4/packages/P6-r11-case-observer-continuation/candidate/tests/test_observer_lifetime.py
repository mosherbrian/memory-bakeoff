"""P6-r9 observer lifetime: normal worker->verifier observed under real
latency. Parent defect: positive-handoff waited a hardcoded 8s slice while
the real first turn completes at ~18-20s, with no reattach -> terminal
no-end while the signed grant (duration 900s) remained valid. Fix: the
observer reattaches the SAME action/execution (zero new sends, original
absolute grant preserved) and observes the remainder; waits derive from
signed grants, never a larger magic constant. Exact CLI, NO --simulated,
only external runtime/model/service effects intercepted. Injected only."""
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

import pytest

R9 = os.path.join(os.path.dirname(__file__), "..")
R9SRC = os.path.join(R9, "src")
R9SCRIPT = os.path.join(R9SRC, "case_entry.py")
R9SEAT = os.path.join(R9SRC, "seat_emulator.py")
R9DEPOSIT = os.path.join(R9SRC, "fixture-wake-deposit")
R9PLAN = os.path.join(R9, "stagec-plan.json")
R8 = "/home/bmosher/memory-bake-off/campaign4/packages/P6-r8-case-execution"
R8SRC = os.path.join(R8, "src")
R8SCRIPT = os.path.join(R8SRC, "case_entry.py")
R8SEAT = os.path.join(R8SRC, "seat_emulator.py")
WLANE = "/home/bmosher/.config/agent-deck/acp-go"
VLANE = "/home/bmosher/.config/agent-deck/acp-go-deepseek"


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cli(script, cwd, *args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, script] + list(args),
                          capture_output=True, text=True, timeout=300,
                          cwd=cwd, env=env)


def write_bin(tmp):
    binp = os.path.join(tmp, "bin")
    os.makedirs(binp, exist_ok=True)
    wake = os.path.join(binp, "wake")
    with open(wake, "w") as fh:
        fh.write("#!/bin/bash\n"
                 "echo \"ARGV:$1\" >> \"%s/wake-calls.log\"\n"
                 "echo \"PROFILE:${AGENTDECK_PROFILE:-unset}\" >> \"%s/wake-calls.log\"\n"
                 "printf '%%s' \"$2\" > \"$DELIVER_INBOX/to-$1-$(date +%%s%%N).txt\"\n"
                 "echo \"wake: $1 -> started\"; exit 0\n" % (tmp, tmp))
    open(os.path.join(binp, "systemd-run"), "w").write("#!/bin/bash\nexit 0\n")
    open(os.path.join(binp, "systemctl"), "w").write(
        "#!/bin/bash\necho \"ActiveState=inactive\"\n"
        "echo \"SubState=dead\"\nexit 0\n")
    for fn in ("wake", "systemd-run", "systemctl"):
        os.chmod(os.path.join(binp, fn), 0o755)


def make_suite(script, seat, deposit, plan_src, cwd, bounds=None,
               live_stop_in=None):
    tmp = tempfile.mkdtemp(prefix="p6r9-")
    write_bin(tmp)
    wsid, vsid = "o9-worker-001", "o9-verifier-001"
    wt, vt = "alpha-12", "omega-07"
    socks = []
    for sid in (wsid, vsid):
        os.makedirs(os.path.join(tmp, "sock"), exist_ok=True)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(os.path.join(tmp, "sock", sid + ".sock"))
        socks.append(s)
    ino = {sid: os.stat(os.path.join(tmp, "sock", sid + ".sock")).st_ino
           for sid in (wsid, vsid)}
    plan = dict(json.load(open(plan_src)))
    plan["host_commands"] = {"deposit_wake": deposit,
                             "wake": tmp + "/bin/wake",
                             "systemd_run": tmp + "/bin/systemd-run",
                             "systemctl": tmp + "/bin/systemctl"}
    if bounds:
        plan.setdefault("bounds", {}).update(bounds)
    if live_stop_in is not None:
        plan["live_stop_utc"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + live_stop_in))
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
    for name in (wt, vt):
        os.makedirs(tmp + "/workdirs/" + name, exist_ok=True)
    os.makedirs(tmp + "/stream", exist_ok=True)
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
    r = cli(script, cwd, "derive-config", "--plan", planp, "--binding",
            bindp, "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    srcdir = os.path.dirname(script)
    json.dump({"signer": "tern", "purpose": "stagec-task",
               "plan_sha256": sha(planp), "binding_sha256": sha(bindp),
               "config_sha256": sha(cfg),
               "stagec_entry_sha256": sha(script),
               "candidate_harness_sha256":
               "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142",
               "r3_harness_sha256": sha(os.path.join(
                   srcdir, "r3harness", "harness.py")),
               "fixture_control_sha256": sha(os.path.join(
                   srcdir, "fixture_control.py")),
               "deposit_sha256": sha(deposit),
               "seat_emulator_sha256": sha(seat),
               "fault_onset_sha256": sha(os.path.join(
                   srcdir, "fault_onset.py"))}, open(sig, "w"))
    return {"tmp": tmp, "plan": planp, "binding": bindp, "cfg": cfg,
            "sig": sig, "reg": regp, "wsid": wsid, "vsid": vsid, "wt": wt,
            "vt": vt, "socks": socks, "script": script, "seat": seat,
            "cwd": cwd}


def emulators(env, case, delays=None):
    delays = delays or {}
    procs = []
    for seat, role, sid in ((env["wt"], "worker", env["wsid"]),
                            (env["vt"], "verifier", env["vsid"])):
        cmd = [sys.executable, env["seat"], "--seat", seat, "--role", role,
               "--text-dir", os.path.join(env["tmp"], case, "inbox"),
               "--stream-file",
               os.path.join(env["tmp"], "stream", sid + ".jsonl"),
               "--onset-dir", os.path.join(env["tmp"], case, "onsets"),
               "--art-dir", os.path.join(env["tmp"], case, "art"),
               "--intervention",
               os.path.join(env["tmp"], "faults", case + ".json"),
               "--timeout-s", "120"]
        if delays.get(seat):
            cmd += ["--delay-s", str(delays[seat])]
        procs.append(subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    return procs


def run_case(env, case, delays=None):
    procs = emulators(env, case, delays=delays or {})
    try:
        return cli(env["script"], env["cwd"], "run-case", "--config",
                   env["cfg"], "--plan", env["plan"], "--signatures",
                   env["sig"], "--case", case, "--suite-root", env["tmp"],
                   "--registry-file", env["reg"], "--out",
                   os.path.join(env["tmp"], case, "receipt.json"))
    finally:
        for p in procs:
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                p.kill()


def close(env):
    for s in env["socks"]:
        s.close()


def arm(env, case, control="none-declared"):
    r = cli(env["script"], env["cwd"], "fault", "arm", "--case", case,
            "--run-root", env["tmp"], "--control", control,
            "--actor", "cairn")
    assert r.returncode == 0, r.stdout


def test_old_fails_parent_delayed_worker():
    # Parent bytes, exact production path: 18s worker vs 8s slice,
    # no reattach on positive -> terminal no-end.
    env = make_suite(R8SCRIPT, R8SEAT, os.path.join(R8SRC,
                     "fixture-wake-deposit"), os.path.join(
                         R8, "stagec-plan.json"), R8)
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["wt"]: 18.0})
        assert r.returncode == 3 and "no-end" in r.stdout, r.stdout
    finally:
        close(env)


def test_delayed_worker_commits_new():
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9)
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["wt"]: 18.0})
        assert r.returncode == 0, r.stdout
        assert json.loads(r.stdout)["timecheck"] == "accept", r.stdout
        rec = json.load(open(os.path.join(env["tmp"], "positive-handoff",
                                          "receipt.json")))
        assert rec["sends"] == {"worker": 1, "verifier": 1}, rec["sends"]
        assert len(rec["settled_actions"]) == 2
        assert "PROFILE:campaign4" in open(os.path.join(
            env["tmp"], "wake-calls.log")).read()
    finally:
        close(env)


def test_delayed_verifier_observed_once():
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9)
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["vt"]: 15.0})
        assert r.returncode == 0, r.stdout
        rec = json.load(open(os.path.join(env["tmp"], "positive-handoff",
                                          "receipt.json")))
        assert rec["sends"] == {"worker": 1, "verifier": 1}, rec["sends"]
    finally:
        close(env)


def test_near_boundary_small_grant():
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9,
                     bounds={"duration_s": 40, "escalation_window_s": 60})
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["wt"]: 25.0})
        assert r.returncode == 0, r.stdout
        rec = json.load(open(os.path.join(env["tmp"], "positive-handoff",
                                          "receipt.json")))
        assert rec["sends"] == {"worker": 1, "verifier": 1}, rec["sends"]
    finally:
        close(env)


def test_expiry_owned_failure_not_success():
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9,
                     bounds={"duration_s": 15, "escalation_window_s": 30})
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["wt"]: 40.0})
        assert r.returncode == 3, r.stdout
        assert '"verdict": "accept"' not in r.stdout, r.stdout
    finally:
        close(env)


def test_outer_stop_incomplete():
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9,
                     live_stop_in=12)
    try:
        arm(env, "positive-handoff")
        r = run_case(env, "positive-handoff",
                     delays={env["wt"]: 25.0})
        assert r.returncode == 3, r.stdout
        assert '"verdict": "accept"' not in r.stdout, r.stdout
    finally:
        close(env)


def test_reopen_worker_phase_same_execution():
    # Reopen DURING the worker wait: a second reattach CLI while the
    # late end is still in flight. Same execution, zero resends: the
    # first observer to bind the end commits, the other dedups.
    import threading
    env = make_suite(R9SCRIPT, R9SEAT, R9DEPOSIT, R9PLAN, R9)
    try:
        arm(env, "positive-handoff")
        procs = emulators(env, "positive-handoff",
                          delays={env["wt"]: 18.0})
        out = {}
        t = threading.Thread(
            target=lambda: out.update(
                {"r": cli(R9SCRIPT, R9, "run-case", "--config", env["cfg"],
                          "--plan", env["plan"], "--signatures", env["sig"],
                          "--case", "positive-handoff", "--suite-root",
                          env["tmp"], "--registry-file", env["reg"],
                          "--out", os.path.join(env["tmp"],
                                                "positive-handoff",
                                                "receipt.json"))}))
        t.start()
        croot = os.path.join(env["tmp"], "positive-handoff")
        cplan = os.path.join(croot, "candidate-plan.json")
        for _ in range(40):
            if os.path.exists(cplan):
                break
            time.sleep(0.5)
        assert os.path.exists(cplan), "first run never dispatched"
        time.sleep(10)  # first 8s slice missed, late end still in flight
        r3 = os.path.join(R9SRC, "r3harness", "harness.py")
        rr = cli(r3, R9, "reattach", "--live", "--plan", cplan,
                 "--plan-hash", sha(cplan), "--allowlist-seat", env["wt"],
                 "--allowlist-seat", env["vt"], "--db",
                 os.path.join(croot, "fixture.db"), "--manifest",
                 os.path.join(croot, "manifest.json"), "--claims",
                 os.path.join(croot, "claims"), "--qid", "P6C")
        t.join(timeout=240)
        for p in procs:
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                p.kill()
        assert out["r"].returncode == 0, out["r"].stdout
        rec = json.load(open(os.path.join(croot, "receipt.json")))
        assert rec["sends"] == {"worker": 1, "verifier": 1}, rec["sends"]
        assert len(rec["settled_actions"]) == 2, rec["settled_actions"]
    finally:
        close(env)
