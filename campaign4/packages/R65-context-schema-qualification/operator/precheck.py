"""R65 explicit pre-handoff / pre-finalization checks (no missing-file defaults). python precheck.py ARM_DIR -> JSON, exit 0 only if all pass."""
import hashlib, json, os, sys
a = sys.argv[1]; h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); fails = []
def need(p):
    q = os.path.join(a, p)
    if not os.path.isfile(q): fails.append(f"missing {p}"); return None
    return q
def j(p):
    q = need(p)
    try: return json.load(open(q)) if q else None
    except ValueError: fails.append(f"malformed {p}"); return None
claim = j("arm-claim.json")
if claim:
    for f, v in claim["files_sha256"].items():
        if not os.path.isfile(os.path.join(a, f)) or h(os.path.join(a, f)) != v: fails.append(f"pin {f}")
    for p, v in claim["dependency_sha256"].items():
        if h(p) != v: fails.append(f"dep {p}")
meta = j("operator-meta.json"); paths = j("paths.json")
if meta and (meta.get("label") != "D-24576" or meta.get("target") != "24576" or meta.get("kind") != "D" or meta["sessions"].get("s1") is not None): fails.append("meta label/target/kind/s1")
c = need("calls")
if c and open(c).read().strip() != "1": fails.append("calls != 1")
for p in ("arm.s1.meta", "arm.s1.jsonl"):
    if os.path.exists(os.path.join(a, p)): fails.append(f"unexpected {p} in D")
m = need("arm.s2.meta")
if m:
    t = open(m).read()
    if "\nexit=0\n" not in t or "\nwrapper_rc=0" not in t: fails.append("s2 child/wrapper not 0/0")
d = need("disposition.txt")
if d and open(d).read().splitlines() != ["HOLD awaiting adjudication"]: fails.append("disposition not exactly the expected adjudication HOLD")
sg = j("scan-gate-s2.json")
if sg and (sg.get("rc") != 0 or sg.get("gate") != "clean"): fails.append("scan not clean")
ev = j("events-s2.json")
if ev is not None and ev.get("counts") != {}: fails.append(f"events counts {ev.get('counts')}")
for s in ("mem-before-s1.manifest", "mem-before-s2.manifest"):
    q = need(s)
    if q and open(q).read().strip() != "ABSENT": fails.append(f"{s} not ABSENT")
need("mem-after-s2.manifest"); need("log"); need("report.md")
cand = j("candidate-r63.json")
if cand and cand["candidate"]["outcome"] != "candidate_primary": fails.append(f"candidate {cand['candidate']['outcome']}")
print(json.dumps({"arm": a, "pass": not fails, "fails": fails, "arm_claim_sha256": h(os.path.join(a, "arm-claim.json")) if claim else None}, indent=1)); sys.exit(1 if fails else 0)
