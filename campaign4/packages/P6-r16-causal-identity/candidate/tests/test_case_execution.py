"""P6-r8 composition tests: exact five-command sequence on one suite root
via subprocess CLI (simulated branch: same code, signed test executables);
fault arming per case; seat emulators as the named external steps; R2
aggregate + contamination + seal; retained H2/hash negatives. Injected
effects only."""
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
# Worker production delay (s) per case for the external timing step;
# lost exceeds the bounded worker wait (8s) so the first run misses it.
DELAYS = {"lost-completion": {"worker": 11.0}}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cli(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True, timeout=240,
                          cwd=PKG, env=env)


def write_test_bin(tmp):
    """Test deposit executable (labeled induced-fault hook, simulated
    branch only): deposits every dispatch into $FIXTURE_OUTBOX like the
    package wrapper, and honors the armed intervention for induced
    transport states (queued-first worker rc3, ambiguous-once verifier
    rc0+garbage). The tool's deliver loop independently verifies these
    receipts; the tool never invents them."""
    binp = os.path.join(tmp, "sim", "bin")
    os.makedirs(binp, exist_ok=True)
    with open(os.path.join(binp, "wake-deposit"), "w") as fh:
        fh.write("#!/bin/bash\n"
                 "out=\"$FIXTURE_OUTBOX\"\n"
                 "n=$(ls \"$out\" 2>/dev/null | wc -l)\n"
                 "python3 - \"$1\" \"$2\" \"$out/send-$(printf %03d $n).json\" <<'PYEOF'\n"
                 "import json,sys,time\n"
                 "json.dump({\"seat\":sys.argv[1],\"text\":sys.argv[2],\n"
                 "  \"received_at\":time.strftime(\"%Y-%m-%dT%H:%M:%SZ\",\n"
                 "  time.gmtime())}, open(sys.argv[3],\"w\"), sort_keys=True)\n"
                 "PYEOF\n"
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
                 "  if [ ! -f \"$out/seen-$1\" ]; then touch \"$out/seen-$1\";\n"
                 "    if printf '%s' \"$2\" | grep -q verifier; then\n"
                 "      echo \"garbage-no-receipt\"; exit 0\n"
                 "    fi\n"
                 "    echo \"wake: $1 -> queued\"; exit 3\n"
                 "  fi;;\n"
                 "esac\n"
                 "echo \"wake: $1 -> deposited-to-fixture-outbox\"; exit 0\n")
    open(os.path.join(binp, "systemd-run"), "w").write("#!/bin/bash\nexit 0\n")
    open(os.path.join(binp, "systemctl"), "w").write(
        "#!/bin/bash\necho \"ActiveState=inactive\"\n"
        "echo \"SubState=dead\"\nexit 0\n")
    for fn in ("wake-deposit", "systemd-run", "systemctl"):
        os.chmod(os.path.join(binp, fn), 0o755)
    open(os.path.join(tmp, "sim", "trace.log"), "w").close()


def make_suite():
    tmp = tempfile.mkdtemp(prefix="p6r8-")
    os.makedirs(os.path.join(tmp, "sim"))
    write_test_bin(tmp)
    wsid, vsid = "t8-worker-001", "t8-verifier-001"
    wt, vt = "p6-fixture-worker-t8", "p6-fixture-verifier-t8"
    socks = []
    for sid in (wsid, vsid):
        os.makedirs(os.path.join(tmp, "sim", "sock"), exist_ok=True)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(os.path.join(tmp, "sim", "sock", sid + ".sock"))
        socks.append(s)
    ino = {sid: os.stat(os.path.join(tmp, "sim", "sock", sid + ".sock"))
           .st_ino for sid in (wsid, vsid)}
    plan = dict(json.load(open(REAL_PLAN)))
    plan["host_commands"] = {"wake": tmp + "/sim/bin/wake",
                             "systemd_run": tmp + "/sim/bin/systemd-run",
                             "systemctl": tmp + "/sim/bin/systemctl"}
    planp = os.path.join(tmp, "plan.json")
    json.dump(plan, open(planp, "w"), sort_keys=True)
    binding = {"launcher_source": "live-agent-deck", "profile": "campaign4",
               "worker": {"session_id": wsid, "title": wt, "role_lane": WLANE,
                          "launch_command": WLANE,
                          "workdir": tmp + "/workdirs/" + wt,
                          "producer_root": tmp + "/stream",
                          "stream_path": tmp + "/stream/" + wsid + ".jsonl",
                          "socket": tmp + "/sim/sock/" + wsid + ".sock",
                          "incarnation": {"ino": ino[wsid], "mtime": 1.0}},
               "verifier": {"session_id": vsid, "title": vt,
                            "role_lane": VLANE, "launch_command": VLANE,
                            "workdir": tmp + "/workdirs/" + vt,
                            "producer_root": tmp + "/stream",
                            "stream_path": tmp + "/stream/" + vsid + ".jsonl",
                            "socket": tmp + "/sim/sock/" + vsid + ".sock",
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
               "deposit_sha256": sha(os.path.join(
                   SRC, "fixture-wake-deposit")),
               "seat_emulator_sha256": sha(SEAT),
               "fault_onset_sha256": sha(os.path.join(
                   SRC, "fault_onset.py"))}, open(sig, "w"))
    return {"tmp": tmp, "plan": planp, "binding": bindp, "cfg": cfg,
            "sig": sig, "reg": regp, "wsid": wsid, "vsid": vsid, "wt": wt,
            "vt": vt, "socks": socks}


@pytest.fixture()
def suite():
    e = make_suite()
    yield e
    for s in e["socks"]:
        s.close()


def emulators(env, case, hold=(), delays=None):
    """External seat steps (plan-named): emulators poll ONLY their inbox;
    texts reach the inbox exclusively through the tool's deliver loop.
    delays maps seat -> startup delay seconds (external timing control)."""
    delays = delays or {}
    procs = []
    for seat, role, sid in ((env["wt"], "worker", env["wsid"]),
                            (env["vt"], "verifier", env["vsid"])):
        if seat in hold:
            continue
        croot = os.path.join(env["tmp"], case)
        cmd = [sys.executable, SEAT, "--seat", seat, "--role", role,
               "--text-dir", os.path.join(croot, "inbox"), "--stream-file",
               os.path.join(env["tmp"], "sim", "stream", sid + ".jsonl"),
               "--onset-dir", os.path.join(croot, "onsets"), "--art-dir",
               os.path.join(croot, "art"), "--intervention",
               os.path.join(env["tmp"], "faults", case + ".json"),
               "--timeout-s", "60"]
        if delays.get(seat):
            cmd += ["--delay-s", str(delays[seat])]
        procs.append(subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    return procs


def case_delays(env, case):
    out = {}
    for seat, delay in DELAYS.get(case, {}).items():
        out[{"worker": env["wt"], "verifier": env["vt"]}[seat]] = delay
    return out


def run_case_cli(env, case, hold=(), delays=None):
    procs = emulators(env, case, hold=hold,
                      delays=delays if delays is not None
                      else case_delays(env, case))
    try:
        return cli("run-case", "--config", env["cfg"], "--plan",
                   env["plan"], "--signatures", env["sig"], "--case",
                   case, "--suite-root", env["tmp"], "--simulated",
                   "--registry-file", env["reg"],
                   "--out", os.path.join(env["tmp"], case, "receipt.json"),
                   env_extra={"FAULT_CASE": case, "FAULT_ROOT": os.path.join(env["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()


def test_r1_missing_intervention_is_incomplete(suite):
    r = cli("run-case", "--config", suite["cfg"], "--plan", suite["plan"],
            "--signatures", suite["sig"], "--case", "lost-completion",
            "--suite-root", suite["tmp"], "--simulated", "--registry-file",
            suite["reg"], "--out",
            os.path.join(suite["tmp"], "lost-completion", "receipt.json"))
    assert r.returncode == 3 and "E_NO_INTERVENTION" in r.stdout, r.stdout


def test_r1_causal_violation_fails(suite):
    r = cli("fault", "arm", "--case", "lost-completion", "--run-root",
            suite["tmp"], "--control", "delay-worker-completion",
            "--actor", "cairn")
    assert r.returncode == 0, r.stdout
    rec = json.load(open(suite["tmp"] + "/faults/lost-completion.json"))
    rec["armed_at"] = "2099-01-01T00:00:00Z"
    json.dump(rec, open(suite["tmp"] + "/faults/lost-completion.json", "w"))
    procs = emulators(suite, "lost-completion", delays=case_delays(suite, "lost-completion"))
    try:
        r = cli("run-case", "--config", suite["cfg"], "--plan",
                suite["plan"], "--signatures", suite["sig"], "--case",
                "lost-completion", "--suite-root", suite["tmp"],
                "--simulated", "--registry-file", suite["reg"], "--out",
                os.path.join(suite["tmp"], "lost-completion",
                             "receipt.json"),
                env_extra={"FAULT_CASE": "lost-completion", "FAULT_ROOT": os.path.join(suite["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
    assert r.returncode == 3 and "E_CAUSAL" in r.stdout, r.stdout


def test_r2_five_command_sequence_one_suite_root(suite):
    for case in CASES:
        r = cli("fault", "arm", "--case", case, "--run-root", suite["tmp"],
                "--control", CONTROLS[case], "--actor", "cairn")
        assert r.returncode == 0, (case, r.stdout)
    for case in CASES:
        procs = emulators(suite, case, delays=case_delays(suite, case))
        try:
            r = cli("run-case", "--config", suite["cfg"], "--plan",
                    suite["plan"], "--signatures", suite["sig"], "--case",
                    case, "--suite-root", suite["tmp"], "--simulated",
                    "--registry-file", suite["reg"], "--out",
                    os.path.join(suite["tmp"], case, "receipt.json"),
                    env_extra={"FAULT_CASE": case, "FAULT_ROOT": os.path.join(suite["tmp"], "faults")})
        finally:
            for p in procs:
                try:
                    p.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    p.kill()
        assert r.returncode == 0, (case, r.stdout)
    seen, execs = set(), set()
    for case in CASES:
        rec = json.load(open(os.path.join(suite["tmp"], case,
                                          "receipt.json")))
        for a, e in rec["executions"].items():
            assert (a, e) not in seen, (case, a)
            seen.add((a, e))
            execs.add(e)
    assert len(execs) == 10
    cfg = json.load(open(suite["cfg"]))
    assert os.path.basename(cfg["worker"]["stream_path"]) == \
        suite["wsid"] + ".jsonl"
    r = cli("verify-suite", "--suite-root", suite["tmp"], "--config",
            suite["cfg"])
    assert r.returncode == 0 and '"suite": "PASS"' in r.stdout, r.stdout
    r = cli("rollback", "--config", suite["cfg"], "--suite-root",
            suite["tmp"], "--archive-dir", suite["tmp"] + "/archive")
    assert r.returncode == 0, r.stdout
    for case in CASES:
        assert os.path.exists(os.path.join(
            suite["tmp"], "archive", case, "rollback-report.json")), case
    procs = emulators(suite, "positive-handoff")
    try:
        r = cli("run-case", "--config", suite["cfg"], "--plan",
                suite["plan"], "--signatures", suite["sig"], "--case",
                "positive-handoff", "--suite-root", suite["tmp"],
                "--simulated", "--registry-file", suite["reg"], "--out",
                os.path.join(suite["tmp"], "positive-handoff",
                             "receipt.json"),
                env_extra={"FAULT_CASE": "positive-handoff", "FAULT_ROOT": os.path.join(suite["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
    assert r.returncode == 3 and "E_SEALED" in r.stdout, r.stdout


def test_retained_gate_negatives(suite):
    base = json.load(open(suite["sig"]))
    sig = dict(base)
    del sig["candidate_harness_sha256"]
    sp = os.path.join(suite["tmp"], "omit.json")
    json.dump(sig, open(sp, "w"))
    r = cli("gate", "--config", suite["cfg"], "--plan", suite["plan"],
            "--signatures", sp, "--registry-file", suite["reg"])
    assert r.returncode == 3 and "E_TOOL_CHANGED" in r.stdout, r.stdout
    reg = json.load(open(suite["reg"]))
    reg[0]["status"] = "stopped"
    json.dump(reg, open(suite["reg"], "w"))
    r = cli("gate", "--config", suite["cfg"], "--plan", suite["plan"],
            "--signatures", suite["sig"], "--registry-file", suite["reg"])
    assert r.returncode == 3 and "E_EXPIRED" in r.stdout, r.stdout


def test_r2_cross_contamination_rejected(tmp_path):
    # Unshared R2 mutation: case B's latency carries case A's action.
    # All other evidence is fully valid, so only E_CONTAMINATION can fire.
    import hashlib as _hl
    root = str(tmp_path)
    cfg = {"timing_bounds": {"detect_s": 30.0, "recover_s": 60.0,
                             "total_s": 90.0,
                             "suspicion_detect_s": 180.0,
                             "suspicion_recover_s": 60.0,
                             "suspicion_total_s": 240.0},
           "cases": {c: {} for c in CASES}}
    cfgp = os.path.join(root, "cfg.json")
    json.dump(cfg, open(cfgp, "w"))
    acts = {}
    for i, case in enumerate(CASES):
        acts[case] = "p6c-x%d" % i
        os.makedirs(os.path.join(root, case))
    for case in CASES:
        d = os.path.join(root, case)
        lat = [{"action": acts[case], "execution": "ex-%s" % case,
                "dispatch_at": "2026-09-22T04:00:00Z",
                "detected_at": "2026-09-22T04:00:05Z",
                "committed_at": "2026-09-22T04:00:20Z",
                "outcome": "transition-committed",
                "onset_at": "2026-09-22T04:00:00Z"}]
        if case == "lost-completion":  # contaminated: A's action in B's file
            lat.append({"action": acts["positive-handoff"],
                        "execution": "ex-positive-handoff",
                        "dispatch_at": "2026-09-22T04:00:00Z",
                        "detected_at": "2026-09-22T04:00:05Z",
                        "committed_at": "2026-09-22T04:00:20Z",
                        "outcome": "transition-committed",
                        "onset_at": "2026-09-22T04:00:00Z"})
        open(os.path.join(d, "latency.jsonl"), "w").write(
            "\n".join(json.dumps(r) for r in lat) + "\n")
        open(os.path.join(d, "witness-rows.jsonl"), "w").write(
            json.dumps({"action": acts[case], "execution": "ex-%s" % case,
                        "case": case, "onset_at": "2026-09-22T04:00:00Z",
                        "onset_provenance": "p",
                        "onset_uncertainty_s": 1,
                        "detected_at": "2026-09-22T04:00:05Z",
                        "outcome": "observed-end", "ack": True}) + "\n")
        open(os.path.join(d, "manifest.json"), "w").write("{}")
        ev = {n: _hl.sha256(open(os.path.join(d, n), "rb").read())
              .hexdigest() for n in ("latency.jsonl", "witness-rows.jsonl",
                                     "manifest.json")}
        ap = os.path.join(d, "applied.json")
        json.dump({"case": case, "actions": [acts[case]],
                   "executions": ["ex-%s" % case]}, open(ap, "w"))
        json.dump({"case": case, "timecheck": {"verdict": "accept"},
                   "executions": {acts[case]: "ex-%s" % case},
                   "settled_actions": [acts[case]],
                   "applied_receipt": ap,
                   "evidence_sha256": ev},
                  open(os.path.join(d, "receipt.json"), "w"))
    r = cli("verify-suite", "--suite-root", root, "--config", cfgp)
    assert r.returncode == 3 and "E_CONTAMINATION" in r.stdout, r.stdout


def test_r1f_forged_production_without_delivery_rejected(suite):
    # R1-F: hold-verifier-texts armed on a positive run, with a
    # pre-planted verifier end (+onset, no claim). The candidate alone
    # adopts it; the early provenance gate must reject E_UNDELIVERED
    # because no delivery record exists for that production. This also
    # proves the hold actually withholds (a delivered text would pass
    # the gate and fail later instead).
    import time as _t
    r = cli("fault", "arm", "--case", "positive-handoff", "--run-root",
            suite["tmp"], "--control", "hold-verifier-texts",
            "--actor", "cairn")
    assert r.returncode == 0, r.stdout
    os.makedirs(os.path.join(suite["tmp"], "sim", "stream"), exist_ok=True)
    os.makedirs(os.path.join(suite["tmp"], "positive-handoff", "onsets"),
                exist_ok=True)
    with open(os.path.join(suite["tmp"], "sim", "stream",
                           suite["vsid"] + ".jsonl"), "w") as fh:
        fh.write('{\"t\":\"end\",\"item\":\"z9-forged-1\"}\n')
    json.dump({"onset_at": _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()),
               "provenance": "forged-fixture", "uncertainty_s": 1},
              open(os.path.join(suite["tmp"], "positive-handoff", "onsets",
                                "z9-forged-1.json"), "w"))
    procs = emulators(suite, "positive-handoff")
    try:
        r = cli("run-case", "--config", suite["cfg"], "--plan",
                suite["plan"], "--signatures", suite["sig"], "--case",
                "positive-handoff", "--suite-root", suite["tmp"],
                "--simulated", "--registry-file", suite["reg"], "--out",
                os.path.join(suite["tmp"], "positive-handoff",
                             "receipt.json"),
                env_extra={"FAULT_CASE": "positive-handoff", "FAULT_ROOT": os.path.join(suite["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
    assert r.returncode == 3 and "E_UNDELIVERED" in r.stdout, r.stdout

def test_r1f_disabled_induction_fails_incomplete(suite):
    # R1-F: armed transport fault but a deposit wrapper that never
    # induces (always started). The case must go INCOMPLETE on missing
    # induced evidence, never pass on the declaration alone.
    plain = os.path.join(suite["tmp"], "sim", "bin", "wake-deposit")
    with open(plain, "w") as fh:
        fh.write("#!/bin/bash\n"
                 "n=$(ls \"$FIXTURE_OUTBOX\" 2>/dev/null | wc -l)\n"
                 "python3 - \"$1\" \"$2\" \"$FIXTURE_OUTBOX/send-$(printf %03d $n).json\" <<'PYEOF'\n"
                 "import json,sys,time\n"
                 "json.dump({\"seat\":sys.argv[1],\"text\":sys.argv[2],\n"
                 " \"received_at\":time.strftime(\"%Y-%m-%dT%H:%M:%SZ\",\n"
                 " time.gmtime())}, open(sys.argv[3],\"w\"))\n"
                 "PYEOF\n"
                 "echo \"wake: $1 -> started\"; exit 0\n")
    os.chmod(plain, 0o755)
    r = cli("fault", "arm", "--case", "queued-ambiguous-restart",
            "--run-root", suite["tmp"], "--control",
            "transport-queued-first", "--actor", "cairn")
    assert r.returncode == 0, r.stdout
    procs = emulators(suite, "queued-ambiguous-restart")
    try:
        r = cli("run-case", "--config", suite["cfg"], "--plan",
                suite["plan"], "--signatures", suite["sig"], "--case",
                "queued-ambiguous-restart", "--suite-root", suite["tmp"],
                "--simulated", "--registry-file", suite["reg"], "--out",
                os.path.join(suite["tmp"], "queued-ambiguous-restart",
                             "receipt.json"),
                env_extra={"FAULT_CASE": "queued-ambiguous-restart", "FAULT_ROOT": os.path.join(suite["tmp"], "faults")})
    finally:
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
    assert r.returncode == 3 and "INCOMPLETE" in r.stdout, r.stdout
    assert '"verdict": "accept"' not in r.stdout, r.stdout
