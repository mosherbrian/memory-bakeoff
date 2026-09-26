"""R51 operator gate around scan.py. python scan_gate.py OUT.json -- <scan.py args...>
Runs scan.py with a 60 s timeout, validates its JSON and exit code, and writes OUT.json with 'gate'.
gate: clean|contaminated|ambiguous|evidence_invalid (scanner verdicts, exit 0-3) or evaluator_failure (exit 5)
for: timeout, invocation failure, crash/scanner_error, empty or non-JSON output, non-object, unknown status,
missing/mistyped required fields, or status/rc mismatch. The operator runner HOLDS the arm on evaluator_failure
and never records it as clean or contaminated."""
import json, subprocess, sys, os
SCAN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scan.py")
RC = {"clean": 0, "contaminated": 1, "ambiguous": 2, "evidence_invalid": 3, "scanner_error": 4}
REQ = {"clean": {"events": int, "executed": list, "attempted_denied": list, "unresolved": list, "contamination": list, "ambiguous": list},
       "evidence_invalid": {"reason": str}, "scanner_error": {}}
REQ["contaminated"] = REQ["ambiguous"] = REQ["clean"]
def gate(out, args, scan=SCAN, timeout=60):
    g = {"scanner": scan, "args": args}
    try:
        p = subprocess.run([sys.executable, scan] + args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        g.update(gate="evaluator_failure", reason="timeout")
    except OSError as e:
        g.update(gate="evaluator_failure", reason=f"invocation: {e}")
    else:
        g["rc"] = p.returncode
        try: d = json.loads(p.stdout)
        except ValueError: d = None
        if not isinstance(d, dict): g.update(gate="evaluator_failure", reason="output not a JSON object")
        elif d.get("status") not in RC: g.update(gate="evaluator_failure", reason=f"unknown status {d.get('status')!r}")
        elif d["status"] == "scanner_error": g.update(gate="evaluator_failure", reason="scanner_error")
        elif RC[d["status"]] != p.returncode: g.update(gate="evaluator_failure", reason=f"status/rc mismatch {d['status']}/{p.returncode}")
        else:
            bad = [k for k, t in REQ[d["status"]].items() if not isinstance(d.get(k), t)]
            if bad: g.update(gate="evaluator_failure", reason=f"missing/mistyped fields {bad}")
            else: g.update(gate=d["status"], result=d)
    json.dump(g, open(out, "w"), indent=1)
    return {"clean": 0, "contaminated": 1, "ambiguous": 2, "evidence_invalid": 3}.get(g["gate"], 5)
if __name__ == "__main__":
    i = sys.argv.index("--")
    sys.exit(gate(sys.argv[1], sys.argv[i + 1:]))
