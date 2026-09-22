"""P6-r11 pinned concrete acceptance cases — failed-verification and quiet-rest.

Independent corvid design (P6r11-concrete-cases-1). Works from the P6-r11
contract and the IMMUTABLE P6-r9 baseline at f1d7c86 (case_entry.py 9a1bb23c,
harness d7b4e517, host_adapter 231f45f0). Cases are branch-neutral: they define
the exact CLI, the observed baseline (old-fails) outcome, and the repaired
(new-passes) outcome; they are NOT tailored to any candidate byte.

Real production path: the r9 `case_entry.py` CLI is invoked with NO `--simulated`.
Only external collaborators are intercepted (seat emulator processes, a fake
wake, fake systemd-run/systemctl) — the accepted r9 test pattern.

Run:
  PYTHONPATH= python3 -m pytest -q \
    P6-r11-case-observer-continuation/concrete-cases/test_r11_failed_quiet.py

Baseline expectations (immutable r9, no shared reattach in these branches):
  * worker > 8s  -> failed-verification exits 3 (E_NO_ONSET), no verifier send,
    no tamper; quiet-rest exits 3 ("setup run did not commit").
  * verifier > 8s -> setup handoff commits but the single slice truncates the
    verifier phase; branch cannot reach its acceptance.
  * expiry / outer stop -> bounded failure/INCOMPLETE, never a success verdict.
"""
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile

import pytest

R9 = "/home/bmosher/memory-bake-off/campaign4/packages/P6-r9-observer-lifetime"
R9SRC = os.path.join(R9, "src")
R9SCRIPT = os.path.join(R9SRC, "case_entry.py")
R9SEAT = os.path.join(R9SRC, "seat_emulator.py")
R9DEPOSIT = os.path.join(R9SRC, "fixture-wake-deposit")
R9PLAN = os.path.join(R9, "stagec-plan.json")
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


def make_suite(cwd, bounds=None, live_stop_in=None):
    tmp = tempfile.mkdtemp(prefix="p6r11-case-")
    write_bin(tmp)
    wsid, vsid = "r11-worker-001", "r11-verifier-001"
    wt, vt = "alpha-12", "omega-07"
    socks = []
    for sid in (wsid, vsid):
        os.makedirs(os.path.join(tmp, "sock"), exist_ok=True)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(os.path.join(tmp, "sock", sid + ".sock"))
        socks.append(s)
    ino = {sid: os.stat(os.path.join(tmp, "sock", sid + ".sock")).st_ino
           for sid in (wsid, vsid)}
    plan = dict(json.load(open(R9PLAN)))
    plan["host_commands"] = {"deposit_wake": R9DEPOSIT,
                             "wake": tmp + "/bin/wake",
                             "systemd_run": tmp + "/bin/systemd-run",
                             "systemctl": tmp + "/bin/systemctl"}
    if bounds:
        plan.setdefault("bounds", {}).update(bounds)
    if live_stop_in is not None:
        import time as _t
        plan["live_stop_utc"] = _t.strftime(
            "%Y-%m-%dT%H:%M:%SZ", _t.gmtime(_t.time() + live_stop_in))
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
                            "incarnation": {"ino": ino[vsid], "mtime": 1.0}}}
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
    r = cli(R9SCRIPT, cwd, "derive-config", "--plan", planp, "--binding",
            bindp, "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    json.dump({"signer": "tern", "purpose": "stagec-task",
               "plan_sha256": sha(planp), "binding_sha256": sha(bindp),
               "config_sha256": sha(cfg),
               "stagec_entry_sha256": sha(R9SCRIPT),
               "candidate_harness_sha256":
               "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142",
               "r3_harness_sha256": sha(os.path.join(
                   R9SRC, "r3harness", "harness.py")),
               "fixture_control_sha256": sha(os.path.join(
                   R9SRC, "fixture_control.py")),
               "deposit_sha256": sha(R9DEPOSIT),
               "seat_emulator_sha256": sha(R9SEAT),
               "fault_onset_sha256": sha(os.path.join(
                   R9SRC, "fault_onset.py"))}, open(sig, "w"))
    return {"tmp": tmp, "plan": planp, "binding": bindp, "cfg": cfg,
            "sig": sig, "reg": regp, "wsid": wsid, "vsid": vsid, "wt": wt,
            "vt": vt, "socks": socks}


def emulators(env, case, delays=None):
    delays = delays or {}
    procs = []
    for seat, role, sid in ((env["wt"], "worker", env["wsid"]),
                            (env["vt"], "verifier", env["vsid"])):
        cmd = [sys.executable, R9SEAT, "--seat", seat, "--role", role,
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
        return cli(R9SCRIPT, R9, "run-case", "--config", env["cfg"], "--plan",
                   env["plan"], "--signatures", env["sig"], "--case", case,
                   "--suite-root", env["tmp"], "--registry-file", env["reg"],
                   "--out", os.path.join(env["tmp"], case, "receipt.json"))
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()


def close(env):
    for s in env["socks"]:
        s.close()


def arm(env, case, control):
    r = cli(R9SCRIPT, R9, "fault", "arm", "--case", case, "--run-root",
            env["tmp"], "--control", control, "--actor", "cairn")
    assert r.returncode == 0, r.stdout


def receipt(env, case):
    p = os.path.join(env["tmp"], case, "receipt.json")
    return json.load(open(p)) if os.path.exists(p) else {}


# --- pinned cases ---------------------------------------------------------

def test_FV_W_worker_gt_8s_baseline_truncates():
    env = make_suite(R9)
    try:
        arm(env, "failed-verification", "corrupt-after-worker")
        r = run_case(env, "failed-verification", {env["wt"]: 18.0})
        assert r.returncode == 3, r.stdout
        rec = receipt(env, "failed-verification")
        assert rec.get("sends") == {"worker": 1, "verifier": 0}, rec.get("sends")
        assert rec.get("committed_actions") == [], rec.get("committed_actions")
        assert "E_NO_ONSET" in r.stdout, r.stdout
    finally:
        close(env)


def test_QR_W_worker_gt_8s_baseline_truncates():
    env = make_suite(R9)
    try:
        arm(env, "quiet-rest", "none-declared")
        r = run_case(env, "quiet-rest", {env["wt"]: 18.0})
        assert r.returncode == 3, r.stdout
        assert "did not commit" in r.stdout, r.stdout
    finally:
        close(env)


def test_FV_EXPIRY_bounded_failure_not_success():
    env = make_suite(R9, bounds={"duration_s": 15,
                                 "escalation_window_s": 30})
    try:
        arm(env, "failed-verification", "corrupt-after-worker")
        r = run_case(env, "failed-verification", {env["wt"]: 40.0})
        assert r.returncode == 3, r.stdout
        assert '"verdict": "accept"' not in r.stdout, r.stdout
    finally:
        close(env)


def test_FV_WV_worker_and_verifier_gt_8s_baseline_truncates():
    # Both legs slow: exercises the full continuation the repair must add.
    # Baseline truncates at the worker slice before any handoff.
    env = make_suite(R9)
    try:
        arm(env, "failed-verification", "corrupt-after-worker")
        r = run_case(env, "failed-verification",
                     {env["wt"]: 18.0, env["vt"]: 18.0})
        assert r.returncode == 3, r.stdout
        assert '"verdict": "accept"' not in r.stdout, r.stdout
    finally:
        close(env)


def test_QR_WV_worker_and_verifier_gt_8s_baseline_truncates():
    env = make_suite(R9)
    try:
        arm(env, "quiet-rest", "none-declared")
        r = run_case(env, "quiet-rest", {env["wt"]: 18.0, env["vt"]: 18.0})
        assert r.returncode == 3, r.stdout
        assert "did not commit" in r.stdout, r.stdout
    finally:
        close(env)


def test_QR_EXPIRY_bounded_failure_not_success():
    env = make_suite(R9, bounds={"duration_s": 15,
                                 "escalation_window_s": 30})
    try:
        arm(env, "quiet-rest", "none-declared")
        r = run_case(env, "quiet-rest", {env["wt"]: 40.0})
        assert r.returncode == 3, r.stdout
        assert '"verdict": "accept"' not in r.stdout, r.stdout
    finally:
        close(env)
