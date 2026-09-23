"""P6-r8 D1-D4 host composition tests: the corrected NO-simulated branch
with the exact proposed plan; external host/model boundaries intercepted
only (test wake stub records argv/env; actual package deposit executable;
actual fixture controller). Adversarial seat titles carry no role
substring. Injected effects only; no live seats/sends."""
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
SCRIPT = os.path.join(SRC, "case_entry.py")
SEAT = os.path.join(SRC, "seat_emulator.py")
DEPOSIT = os.path.join(SRC, "fixture-wake-deposit")
REAL_PLAN = os.path.join(PKG, "stagec-plan.json")
WLANE = "/home/bmosher/.config/agent-deck/acp-go"
VLANE = "/home/bmosher/.config/agent-deck/acp-go-deepseek"
CASES = ["positive-handoff", "lost-completion", "failed-verification",
         "queued-ambiguous-restart", "quiet-rest"]
CONTROLS = {"positive-handoff": "none-declared",
            "lost-completion": "delay-worker-completion",
            "failed-verification": "corrupt-after-worker",
            "queued-ambiguous-restart": "transport-queued-first",
            "quiet-rest": "none-declared"}
DELAYS = {"lost-completion": {"worker": 11.0}}

sys.path.insert(0, SRC)


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cli(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True, timeout=240,
                          cwd=PKG, env=env)


def write_host_bin(tmp):
    """Test wake stub: records argv/env (proving true wake argv/env +
    explicit profile), honors the armed intervention for induced queued/
    ambiguous returns (labeled induced), and hands texts to DELIVER_INBOX.
    It never supplies controller semantics."""
    binp = os.path.join(tmp, "bin")
    os.makedirs(binp, exist_ok=True)
    wake = os.path.join(binp, "wake")
    with open(wake, "w") as fh:
        fh.write("#!/bin/bash\n"
                 "echo \"ARGV:$1\" >> \"%s/wake-calls.log\"\n"
                 "echo \"PROFILE:${AGENTDECK_PROFILE:-unset}\" >> \"%s/wake-calls.log\"\n"
                 "echo \"CWD:$(pwd)\" >> \"%s/wake-calls.log\"\n"
                 "printf '%%s' \"$2\" > \"$DELIVER_INBOX/to-$1-$(date +%%s%%N).txt\"\n"
                 "if [ \"$2\" = \"probe-ambiguous\" ]; then\n"
                 "  echo \"garbage-no-receipt\"; exit 0\n"
                 "fi\n"
                 "ctl=$(python3 -c \"import json,os;\n"
                 "p=os.path.join(os.environ.get('FAULT_ROOT',''),\n"
                 "  os.environ.get('FAULT_CASE','')+'.json');\n"
                 "d=json.load(open(p)) if os.path.exists(p) else {};\n"
                 "print(d.get('control',''))\" 2>/dev/null)\n"
                 "case \"$ctl\" in\n"
                  "*transport-queued-first*)\n"
                  "  if [ ! -f \"$DELIVER_INBOX/seen-$1\" ]; then touch \"$DELIVER_INBOX/seen-$1\";\n"
                  "    if [ \"$1\" = \"omega-07\" ]; then\n"
                  "      echo \"garbage-no-receipt\"; exit 0\n"
                  "    fi\n"
                  "    echo \"wake: $1 -> queued\"; exit 3\n"
                  "  fi;;\n"
                 "esac\n"
                 "echo \"wake: $1 -> started\"; exit 0\n"
                 % (tmp, tmp, tmp))
    open(os.path.join(binp, "systemd-run"), "w").write("#!/bin/bash\nexit 0\n")
    open(os.path.join(binp, "systemctl"), "w").write(
        "#!/bin/bash\necho \"ActiveState=inactive\"\n"
        "echo \"SubState=dead\"\nexit 0\n")
    for fn in ("wake", "systemd-run", "systemctl"):
        os.chmod(os.path.join(binp, fn), 0o755)


def make_host_suite():
    tmp = tempfile.mkdtemp(prefix="p6r8h-")
    write_host_bin(tmp)
    # Adversarial titles: no role substring; authority comes only from
    # signed bindings.
    wsid, vsid = "h-worker-001", "h-verifier-001"
    wt, vt = "alpha-12", "omega-07"
    socks = []
    for sid in (wsid, vsid):
        os.makedirs(os.path.join(tmp, "sock"), exist_ok=True)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(os.path.join(tmp, "sock", sid + ".sock"))
        socks.append(s)
    ino = {sid: os.stat(os.path.join(tmp, "sock", sid + ".sock")).st_ino
           for sid in (wsid, vsid)}
    plan = dict(json.load(open(REAL_PLAN)))
    plan["host_commands"] = {"deposit_wake": DEPOSIT,
                             "wake": tmp + "/bin/wake",
                             "systemd_run": tmp + "/bin/systemd-run",
                             "systemctl": tmp + "/bin/systemctl"}
    plan["live_run_dirs"] = {"root": tmp + "/run",
                             "claims": tmp + "/run/claims",
                             "art": tmp + "/run/art",
                             "onsets": tmp + "/run/onsets",
                             "msgs": tmp + "/run/msgs",
                             "db": tmp + "/run/fixture.db",
                             "latency": tmp + "/run/latency.jsonl",
                             "witness": tmp + "/run/witness-rows.jsonl"}
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
    r = cli("derive-config", "--plan", planp, "--binding", bindp,
            "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    json.dump({"signer": "tern", "purpose": "stagec-task",
               "plan_sha256": sha(planp), "binding_sha256": sha(bindp),
               "config_sha256": sha(cfg),
               "stagec_entry_sha256": sha(SCRIPT),
               "candidate_harness_sha256":
               "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142",
               "r3_harness_sha256": sha(os.path.join(
                   SRC, "r3harness", "harness.py")),
               "fixture_control_sha256": sha(os.path.join(
                   SRC, "fixture_control.py")),
               "deposit_sha256": sha(DEPOSIT),
               "seat_emulator_sha256": sha(SEAT),
               "fault_onset_sha256": sha(os.path.join(
                   SRC, "fault_onset.py"))}, open(sig, "w"))
    return {"tmp": tmp, "plan": planp, "binding": bindp, "cfg": cfg,
            "sig": sig, "reg": regp, "wsid": wsid, "vsid": vsid, "wt": wt,
            "vt": vt, "socks": socks}


@pytest.fixture()
def hsuite():
    e = make_host_suite()
    yield e
    for s in e["socks"]:
        s.close()


def emulators(env, case, delays=None):
    delays = delays or {}
    procs = []
    for seat, role, sid in ((env["wt"], "worker", env["wsid"]),
                            (env["vt"], "verifier", env["vsid"])):
        croot = os.path.join(env["tmp"], case)
        cmd = [sys.executable, SEAT, "--seat", seat, "--role", role,
               "--text-dir", os.path.join(croot, "inbox"), "--stream-file",
               os.path.join(env["tmp"], "stream", sid + ".jsonl"),
               "--onset-dir", os.path.join(croot, "onsets"), "--art-dir",
               os.path.join(croot, "art"), "--intervention",
               os.path.join(env["tmp"], "faults", case + ".json"),
               "--timeout-s", "60"]
        if delays.get(seat):
            cmd += ["--delay-s", str(delays[seat])]
        procs.append(subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    return procs


def run_host_case(env, case, delays=None):
    procs = emulators(env, case, delays=delays or {})
    try:
        return cli("run-case", "--config", env["cfg"], "--plan",
                   env["plan"], "--signatures", env["sig"], "--case",
                   case, "--suite-root", env["tmp"], "--registry-file",
                   env["reg"], "--out",
                   os.path.join(env["tmp"], case, "receipt.json"),
                   env_extra={"FAULT_CASE": case, "FAULT_ROOT": os.path.join(env["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()


def test_d1_plan_literal_and_executable(hsuite):
    plan = json.load(open(hsuite["plan"]))
    for key in ("deposit_wake", "wake", "systemd_run", "systemctl"):
        val = plan["host_commands"][key]
        assert os.path.isfile(val) and os.access(val, os.X_OK), (key, val)
        assert "\n" not in val, key  # literal path, never prose
    assert "substitutions" in plan and "binding_manifest" not in plan.get(
        "host_commands", {})
    import case_entry as ce
    assert ce._plan_dirs(plan, {"onsets": "/tmp", "art": "/tmp",
                                "latency": "/tmp/x",
                                "root": "/tmp"})["wake_shim"] == DEPOSIT


def test_d4_full_host_sequence(hsuite):
    for case in CASES:
        r = cli("fault", "arm", "--case", case, "--run-root",
                hsuite["tmp"], "--control", CONTROLS[case],
                "--actor", "cairn")
        assert r.returncode == 0, (case, r.stdout)
    delays = {"lost-completion": {hsuite["wt"]: 11.0}}
    results = {}
    for case in CASES:
        r = run_host_case(hsuite, case,
                          delays=delays.get(case, {}))
        assert r.returncode == 0, (case, r.stdout)
        results[case] = json.loads(r.stdout)["timecheck"]
    assert results["positive-handoff"] == "accept"
    assert results["lost-completion"] == "accept"
    assert results["failed-verification"] == "accept-open"
    assert results["queued-ambiguous-restart"] == "accept"
    assert results["quiet-rest"] == "accept"
    rec = json.load(open(os.path.join(hsuite["tmp"], "positive-handoff",
                                      "receipt.json")))
    assert rec["sends"] == {"worker": 1, "verifier": 1}, rec["sends"]
    assert rec["settled_actions"] == sorted(rec["settled_actions"])
    assert len(rec["settled_actions"]) == 2
    qrec = json.load(open(os.path.join(
        hsuite["tmp"], "queued-ambiguous-restart", "receipt.json")))
    assert qrec["induced"] is True
    kinds = {s.get("state") for s in
             qrec.get("transport_states", {}).values()}
    assert {"queued", "ambiguous"} <= kinds, kinds
    # true wake argv/env recorded by the stub, distinct signed roles
    calls = open(os.path.join(hsuite["tmp"], "wake-calls.log")).read()
    assert "PROFILE:campaign4" in calls
    assert hsuite["wt"] in calls and hsuite["vt"] in calls
    # no-overlay positive trace: transport evidence, no shim artifacts
    assert "CALL wake" not in calls
    r = cli("verify-suite", "--suite-root", hsuite["tmp"], "--config",
            hsuite["cfg"])
    assert r.returncode == 0 and '"suite": "PASS"' in r.stdout, r.stdout
    r = cli("rollback", "--config", hsuite["cfg"], "--suite-root",
            hsuite["tmp"], "--archive-dir", hsuite["tmp"] + "/archive")
    assert r.returncode == 0, r.stdout
    for case in CASES:
        assert os.path.exists(os.path.join(
            hsuite["tmp"], "archive", case, "rollback-report.json")), case


def test_d2_unknown_and_mismatch_rejected_before_wake(tmp_path):
    import fixture_control as fc
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "outbox"))
    with open(os.path.join(root, "outbox", "send-000.json"), "w") as fh:
        json.dump({"seat": "ghost-seat", "text": "{\"action\":\"a9\","
                  "\"execution\":\"ex-9\"}", "received_at": "t"}, fh)
    with pytest.raises(Exception) as e:
        fc.deliver_pending(os.path.join(root, "outbox"),
                           os.path.join(root, "inbox"),
                           {"control": "none-declared", "case": "c"},
                           {"alpha-12": {"role": "worker", "action": "a1",
                                         "execution": "ex-1"}}, root)
    assert "E_UNKNOWN_SEAT" in str(e.value)
    root2 = os.path.join(str(tmp_path), "mismatch")
    os.makedirs(os.path.join(root2, "outbox"))
    with open(os.path.join(root2, "outbox", "send-000.json"), "w") as fh:
        json.dump({"seat": "alpha-12", "text": "{\"action\":\"WRONG\","
                  "\"execution\":\"ex-1\"}", "received_at": "t"}, fh)
    with pytest.raises(Exception) as e:
        fc.deliver_pending(os.path.join(root2, "outbox"),
                           os.path.join(root2, "inbox"),
                           {"control": "none-declared", "case": "c"},
                           {"alpha-12": {"role": "worker", "action": "a1",
                                         "execution": "ex-1"}}, root2)
    assert "E_MISMATCH" in str(e.value)


def test_d3_reopen_reconciliation_no_blind_resend(tmp_path):
    import fixture_control as fc
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "outbox"))
    os.makedirs(os.path.join(root, "inbox"))
    with open(os.path.join(root, "outbox", "send-000.json"), "w") as fh:
        json.dump({"seat": "alpha-12", "text": "{\"action\":\"a1\","
                  "\"execution\":\"ex-1\"}", "received_at": "t"}, fh)
    bindings = {"alpha-12": {"role": "worker", "action": "a1",
                             "execution": "ex-1"}}
    recs = fc.deliver_pending(os.path.join(root, "outbox"),
                              os.path.join(root, "inbox"),
                              {"control": "none-declared", "case": "c"},
                              bindings, root)
    assert len(recs) == 1 and recs[0]["delivered_at"]
    # reopen: intent already done -> no resend, nothing redelivered
    recs2 = fc.deliver_pending(os.path.join(root, "outbox"),
                               os.path.join(root, "inbox"),
                               {"control": "none-declared", "case": "c"},
                               bindings, root)
    assert recs2 == []
    assert len(os.listdir(os.path.join(root, "inbox"))) == 1
    report = fc.reconcile_journal(os.path.join(root, "outbox"),
                                  os.path.join(root, "inbox"), root)
    assert report["redelivered"] == []


def test_d4_new_surface_hash_drift_rejects(hsuite):
    base = json.load(open(hsuite["sig"]))
    sig = dict(base)
    sig["fixture_control_sha256"] = "0" * 64
    sp = os.path.join(hsuite["tmp"], "drift.json")
    json.dump(sig, open(sp, "w"))
    r = cli("gate", "--config", hsuite["cfg"], "--plan", hsuite["plan"],
            "--signatures", sp, "--registry-file", hsuite["reg"])
    assert r.returncode == 3 and "E_TOOL_CHANGED" in r.stdout, r.stdout
