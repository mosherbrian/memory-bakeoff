"""R51 deterministic tests: scanner v4 cases, R50 regressions, frozen R49 A-N (labelled reanalysis), and gate failure modes.
python tests/run_tests.py  -> tests/results.json; exit 0 only if every case matches its expected outcome."""
import json, os, subprocess, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(H, "tests"); sys.path.insert(0, os.path.join(H, "operator"))
import scan_gate
ARM, MEM, DENY = "/tmp/r51t/arm1", "/var/home/bmosher/.claude/projects/-tmp-r51t-arm1/memory", ["/tmp/r51t/arm2", "/tmp/r51t/ops"]
for d in (ARM, *DENY): os.makedirs(d, exist_ok=True)
def use(i, n, inp): return json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": i, "name": n, "input": inp}]}})
def res(i, err=False): return json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": i, "is_error": err, "content": "x"}]}})
def deny(i): return json.dumps({"type": "system", "subtype": "permission_denied", "tool_use_id": i, "message": "denied"})
I = json.dumps({"type": "system", "subtype": "init"}); F = json.dumps({"type": "result"})
NEW = {  # name: (lines, expected status)
 "unresolved_allowed": ([I, use("a", "Read", {"file_path": "state/x"}), F], "ambiguous"),
 "unresolved_forbidden": ([I, use("a", "Bash", {"command": "cat ~/.claude/history.jsonl"}), F], "ambiguous"),
 "mixed_confirmed_forbidden_plus_unresolved": ([I, use("a", "Read", {"file_path": "../arm2/r"}), res("a"), use("b", "Read", {"file_path": "state/x"}), F], "contaminated"),
 "mixed_clean_plus_unresolved": ([I, use("a", "Read", {"file_path": "state/x"}), res("a"), use("b", "Read", {"file_path": "state/y"}), F], "ambiguous"),
 "denied_before_use": ([I, deny("a"), use("a", "Bash", {"command": "cat /tmp/r51t/ops/m"}), F], "clean"),
 "denied_after_use": ([I, use("a", "Bash", {"command": "cat /tmp/r51t/ops/m"}), deny("a"), F], "clean"),
 "contradictory_forbidden": ([I, use("a", "Bash", {"command": "cat /tmp/r51t/ops/m"}), res("a"), deny("a"), F], "contaminated"),
 "contradictory_allowed": ([I, use("a", "Read", {"file_path": "state/x"}), res("a"), deny("a"), F], "ambiguous"),
 "denied_with_error_result": ([I, use("a", "Bash", {"command": "cat /tmp/r51t/ops/m"}), deny("a"), res("a", True), F], "clean"),
 "all_resolved_clean": ([I, use("a", "Read", {"file_path": "state/x"}), res("a"), F], "clean"),
}
out, ok = {}, True
for k, (lines, exp) in NEW.items():
    p = os.path.join(T, k + ".jsonl"); open(p, "w").write("\n".join(lines) + "\n")
    rc = scan_gate.gate(os.path.join(T, k + ".gate.json"), [p, ARM, MEM, *DENY]); g = json.load(open(os.path.join(T, k + ".gate.json")))["gate"]
    out[k] = {"expected": exp, "gate": g, "rc": rc, "ok": g == exp}; ok &= g == exp
# R50 regression cases (same expected statuses as R50 summary)
R50 = os.path.join(H, "..", "R50-restart-instrument-repair", "scan-tests")
EXP50 = {"clean_basic": "clean", "string_system_message": "clean", "denied_forbidden_not_access": "clean", "executed_forbidden_history": "contaminated",
 "relative_other_arm": "contaminated", "symlink_escape": "contaminated", "own_transcript": "contaminated", "quoted_heredoc_prose_paths": "clean",
 "unquoted_heredoc": "ambiguous", "indirect_interpreter": "ambiguous", "unknown_tool": "ambiguous", "empty": "evidence_invalid", "malformed": "evidence_invalid", "non_object": "evidence_invalid"}
os.makedirs("/tmp/r50t/arm1", exist_ok=True); os.makedirs("/tmp/r50t/arm2", exist_ok=True); os.makedirs("/tmp/r50t/ops", exist_ok=True)
for k, exp in EXP50.items():
    rc = scan_gate.gate(os.path.join(T, "r50-" + k + ".gate.json"), [os.path.join(R50, k + ".jsonl"), "/tmp/r50t/arm1", "/var/home/bmosher/.claude/projects/-tmp-r50t-arm1/memory", "/tmp/r50t/arm2", "/tmp/r50t/ops"])
    g = json.load(open(os.path.join(T, "r50-" + k + ".gate.json")))["gate"]
    out["r50:" + k] = {"expected": exp, "gate": g, "ok": g == exp}; ok &= g == exp
# frozen R49 A-N (labelled reanalysis)
E = os.path.join(H, "..", "R49-restart-memory-trial", "evidence", "A-N"); a = json.load(open(os.path.join(E, "A-N.arm.json")))
for s, exp in (("s1", "clean"), ("s2", "clean")):
    scan_gate.gate(os.path.join(T, f"A-N-{s}-reanalysis.gate.json"), [os.path.join(E, f"A-N.{s}.jsonl"), a["cwd"], a["memory"], "/tmp/campaign4-r49-op", "/home/bmosher/memory-bake-off/campaign4/packages"])
    g = json.load(open(os.path.join(T, f"A-N-{s}-reanalysis.gate.json")))["gate"]; out["A-N:" + s] = {"expected": exp, "gate": g, "ok": g == exp, "label": "reanalysis"}; ok &= g == exp
# gate failure modes with stub scanners
STUBS = {"malformed_output": "print('not json')", "unknown_status": "import json;print(json.dumps({'status':'weird'}))",
 "rc_mismatch": "import json,sys;print(json.dumps({'status':'clean','events':1,'executed':[],'attempted_denied':[],'unresolved':[],'contamination':[],'ambiguous':[]}));sys.exit(1)",
 "missing_fields": "import json;print(json.dumps({'status':'clean'}))", "crash": "raise SystemExit(4)", "empty_output": "pass",
 "timeout": "import time;time.sleep(5)", "scanner_error_status": "import json,sys;print(json.dumps({'status':'scanner_error'}));sys.exit(4)"}
for k, code in STUBS.items():
    sp = os.path.join(T, "stub_" + k + ".py"); open(sp, "w").write(code + "\n")
    rc = scan_gate.gate(os.path.join(T, "gate-" + k + ".json"), ["x"], scan=sp, timeout=2)
    g = json.load(open(os.path.join(T, "gate-" + k + ".json")))["gate"]; out["gate:" + k] = {"expected": "evaluator_failure", "gate": g, "rc": rc, "ok": g == "evaluator_failure" and rc == 5}; ok &= out["gate:" + k]["ok"]
rc = scan_gate.gate(os.path.join(T, "gate-invocation.json"), ["x"], scan="/nonexistent/scan.py", timeout=2)
g = json.load(open(os.path.join(T, "gate-invocation.json")))["gate"]; out["gate:invocation_failure"] = {"expected": "evaluator_failure", "gate": g, "rc": rc, "ok": g == "evaluator_failure"}; ok &= g == "evaluator_failure"
json.dump({"all_ok": ok, "cases": out}, open(os.path.join(T, "results.json"), "w"), indent=1)
print("all_ok", ok, sum(v["ok"] for v in out.values()), "/", len(out)); [print(k, v) for k, v in out.items() if not v["ok"]]
sys.exit(0 if ok else 1)
