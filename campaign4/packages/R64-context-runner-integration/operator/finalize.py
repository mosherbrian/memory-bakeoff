"""R64 finalizer (outside the arm): python finalize.py LABEL RECEIPT.json [EVIDENCE_DIR] [OUT_DIR]
Checks, in order (requirements.md): whole-arm pins, label/target mapping, recomputed candidate, receipt binding, prior integrity HOLDs,
then the unchanged R63 gate. Writes OUT_DIR/LABEL.json only; never writes into the arm bundle."""
import hashlib, importlib.util, json, os, sys
PK = "/var/home/bmosher/memory-bake-off/campaign4/packages"
spec = importlib.util.spec_from_file_location("g63", f"{PK}/R63-context-evidence-gate/gate.py"); g63 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g63)
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def target_of(label): return label.split("-")[1] if label.startswith("D-") else label.split("-")[0]
def finalize(label, receipt, evd):
    a = os.path.join(evd, label); res = lambda st, why, **k: {"label": label, "status": st, "reason": why, "final_primary": False, **k}
    try: claim = json.load(open(f"{a}/arm-claim.json")); ch = h(f"{a}/arm-claim.json")
    except (OSError, ValueError): return res("HOLD_EVIDENCE", "arm-claim missing or malformed")
    try:
        bad = [f for f, v in claim["files_sha256"].items() if h(os.path.join(a, f)) != v] + [p for p, v in claim["dependency_sha256"].items() if h(p) != v]
        extra = [os.path.relpath(os.path.join(r, f), a) for r, _, fl in os.walk(a) for f in fl if f != "arm-claim.json" and os.path.relpath(os.path.join(r, f), a) not in claim["files_sha256"]]
    except (OSError, KeyError, TypeError): return res("HOLD_EVIDENCE", "pinned file unreadable")
    if bad or extra: return res("HOLD_EVIDENCE", f"pins changed {bad[:3]} extra {extra[:3]}")
    try: meta = json.load(open(f"{a}/operator-meta.json")); frozen = json.load(open(f"{a}/candidate-r63.json"))["candidate"]
    except (OSError, ValueError, KeyError): return res("HOLD_EVIDENCE", "operator-meta or candidate missing/malformed")
    if meta.get("label") != label or meta.get("target") != target_of(label): return res("HOLD_EVIDENCE", "label/target mapping mismatch")
    cand = g63.candidate(f"{a}/log", meta["target"], f"{a}/report.md")
    if json.loads(json.dumps(cand)) != frozen: return res("HOLD_EVIDENCE", "recomputed candidate differs from frozen candidate")
    rec = None
    if receipt:
        try: rec = json.load(open(receipt))
        except (OSError, ValueError): return res("HOLD", "receipt unreadable or malformed", candidate=cand["outcome"])
        if not isinstance(rec, dict) or rec.get("label") != label or rec.get("arm_claim_sha256") != ch:
            return res("HOLD", "receipt not bound to this arm (label/arm_claim_sha256)", candidate=cand["outcome"])
    integ = [l for l in open(f"{a}/disposition.txt").read().splitlines() if l.startswith("HOLD") and l != "HOLD awaiting adjudication" and not l.startswith("HOLD candidate ")] if os.path.exists(f"{a}/disposition.txt") else []
    if integ: return res("HOLD_INTEGRITY", "prior execution/scanner/memory/events HOLD cannot be overridden", holds=integ, candidate=cand["outcome"])
    g = g63.gate(cand, receipt if rec is not None else None)
    return {"label": label, "status": g["status"], "reason": g["reason"], "final_outcome": g["final_outcome"], "final_primary": g["final_primary"],
            "candidate": cand["outcome"], "arm_claim_sha256": ch, "receipt": receipt, "receipt_sha256": h(receipt) if receipt else None}
if __name__ == "__main__":
    L, R = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None)
    evd = sys.argv[3] if len(sys.argv) > 3 else f"{PK}/R64-context-runner-integration/evidence"
    out = sys.argv[4] if len(sys.argv) > 4 else f"{PK}/R64-context-runner-integration/finalized"
    r = finalize(L, R, evd); os.makedirs(out, exist_ok=True)
    p = f"{out}/{L}.json"
    if os.path.exists(p): print(json.dumps({"error": "finalization exists, not overwriting", "path": p})); sys.exit(4)
    json.dump(r, open(p, "w"), indent=1); print(json.dumps(r, indent=1))
