"""R66 staged finalizer (outside the arm): python finalize.py LABEL RECEIPT|- [EVIDENCE_DIR] [FINAL_DIR]
Implements requirements.md: closure incl. this file, required evidence without defaults, integrity HOLDs, receipt binding, unchanged
R63 gate. Every call writes an immutable attempt; only FINAL/FINAL_INVALID creates the single terminal (atomic, exclusive)."""
import hashlib, importlib.util, json, os, re, secrets, sys, uuid
from datetime import datetime, timezone
PK = "/var/home/bmosher/memory-bake-off/campaign4/packages"; ME = f"{PK}/R67-identity-boundary-validation/operator/finalize.py"
spec = importlib.util.spec_from_file_location("g63", f"{PK}/R63-context-evidence-gate/gate.py"); g63 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g63)
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
COMMON = ["paths.json", "calls", "log", "report.md", "disposition.txt", "candidate-r63.json", "operator-meta.json", "arm.s2.meta", "arm.s2.jsonl",
          "scan-gate-s2.json", "events-s2.json", "mem-before-s1.manifest", "mem-before-s2.manifest", "mem-after-s2.manifest"]
S1 = ["arm.s1.meta", "arm.s1.jsonl", "scan-gate-s1.json", "events-s1.json", "mem-after-s1.manifest", "mem-compare"]
BADEV = ("unresolved", "unsupported_shell", "denied")
class Hold(Exception):
    def __init__(s, status, why): s.status, s.why = status, why
def check(label, receipt, evd):
    a = os.path.join(evd, label); kind = "D" if label.startswith("D-") else label.split("-")[-1]; target = label.split("-")[1] if kind == "D" else label.split("-")[0]
    E = lambda why: Hold("HOLD_EVIDENCE", why); I = lambda why: Hold("HOLD_INTEGRITY", why)
    def rd(f):
        try: return open(os.path.join(a, f)).read()
        except (OSError, UnicodeDecodeError): raise E(f"required {f} missing or unreadable")
    def js(f):
        try: return json.loads(rd(f))
        except ValueError: raise E(f"{f} malformed JSON")
    claim = js("arm-claim.json"); ch = h(os.path.join(a, "arm-claim.json"))
    if not (isinstance(claim, dict) and isinstance(claim.get("files_sha256"), dict) and isinstance(claim.get("dependency_sha256"), dict) and isinstance(claim.get("missing"), list)):
        raise E("arm-claim schema invalid")
    if claim["dependency_sha256"].get(ME) != h(ME): raise E("finalizer not pinned in arm closure or changed since freeze")
    for p, v in claim["dependency_sha256"].items():
        if not os.path.isfile(p) or h(p) != v: raise E(f"dependency changed {p}")
    for f, v in claim["files_sha256"].items():
        if not os.path.isfile(os.path.join(a, f)) or h(os.path.join(a, f)) != v: raise E(f"pinned file changed {f}")
    extra = [os.path.relpath(os.path.join(r, f), a) for r, _, fl in os.walk(a) for f in fl if f != "arm-claim.json" and os.path.relpath(os.path.join(r, f), a) not in claim["files_sha256"]]
    if extra: raise E(f"unpinned files {extra[:3]}")
    need = COMMON + ([] if kind == "D" else S1)
    miss = [f for f in need if f not in claim["files_sha256"]]
    if miss: raise E(f"required evidence missing at freeze {miss}")
    if kind == "D" and any(f in claim["files_sha256"] for f in S1 if f != "mem-compare"): raise E("D arm has s1 evidence")
    meta = js("operator-meta.json")
    if not isinstance(meta, dict) or meta.get("label") != label or meta.get("target") != target or meta.get("kind") != kind: raise E("operator-meta label/target/kind mismatch")
    if rd("calls").strip() != ("1" if kind == "D" else "2"): raise I("call count wrong")
    for n in ((2,) if kind == "D" else (1, 2)):
        t = rd(f"arm.s{n}.meta")
        ex, wr = re.findall(r"^exit=(.*)$", t, re.M), re.findall(r"^wrapper_rc=(.*)$", t, re.M)
        if len(ex) != 1 or len(wr) != 1: raise E(f"s{n} exit/wrapper status absent")
        if ex[0] != "0" or wr[0] != "0": raise I(f"s{n} child={ex[0]} wrapper={wr[0]}")
        sg = js(f"scan-gate-s{n}.json")
        if not isinstance(sg, dict) or "rc" not in sg: raise E(f"scan-gate-s{n} schema invalid")
        if sg.get("rc") != 0 or sg.get("gate") != "clean": raise I(f"scan s{n} not clean")
        ev = js(f"events-s{n}.json")
        if not isinstance(ev, dict) or not isinstance(ev.get("counts"), dict): raise E(f"events-s{n} schema invalid")
        if any(k in ev["counts"] for k in BADEV): raise I(f"events s{n} {ev['counts']}")
    # R67 content checks: paths/mapping, session identity, memory manifests vs snapshots (frozen evidence only)
    pj = js("paths.json"); keys = ("cwd", "cwd_real", "project", "project_real", "memory", "memory_real")
    if not isinstance(pj, dict) or any(not isinstance(pj.get(k), str) or not os.path.isabs(pj[k]) or os.path.normpath(pj[k]) != pj[k] for k in keys): raise E("paths.json schema invalid")
    if not re.fullmatch(r"/tmp/c4x-[0-9a-f]{12}", pj["cwd"]): raise E("paths.json cwd not an opaque c4x dir")
    roots = {"/var/home/bmosher/.claude/projects"} | ({os.environ["R67_TEST_PROJECTS"]} if os.environ.get("R67_TEST_PROJECTS") else set())
    if os.path.dirname(pj["project"]) not in roots or os.path.basename(pj["project"]) != re.sub(r"[/.]", "-", pj["cwd"]) or pj["memory"] != pj["project"] + "/memory": raise E("paths.json project/memory mapping wrong")
    aa = js("arm.arm.json")
    if not isinstance(aa, dict) or aa.get("cwd") != pj["cwd"] or aa.get("memory") != pj["memory"]: raise E("arm.arm.json disagrees with paths.json")
    if any(l.rsplit(" ", 1)[-1] != pj["cwd_real"] for l in rd("log").splitlines()): raise E("trace cwd differs from paths.json cwd_real")
    sids = {}
    for n in ((2,) if kind == "D" else (1, 2)):
        t = rd(f"arm.s{n}.meta"); ids = re.findall(r"^session_id=(.*)$", t, re.M)
        if len(ids) != 1: raise E(f"s{n} session_id missing or duplicated")
        try: ok = str(uuid.UUID(ids[0])) == ids[0]
        except ValueError: ok = False
        if not ok: raise E(f"s{n} session_id not a canonical UUID")
        if f"--session-id {ids[0]} " not in t: raise E(f"s{n} argv does not carry its session id")
        sids[f"s{n}"] = ids[0]
    if kind != "D" and sids["s1"] == sids["s2"]: raise E("s1 and s2 share a session id")
    if not isinstance(meta.get("sessions"), dict) or meta["sessions"].get("s2") != sids["s2"] or meta["sessions"].get("s1") != sids.get("s1"): raise E("operator-meta sessions disagree with session meta")
    mans = {}
    for x in ["before-s1", "before-s2", "after-s2"] + ([] if kind == "D" else ["after-s1"]):
        m = rd(f"mem-{x}.manifest"); lines = m.strip().splitlines()
        snap = os.path.join(a, f"mem-{x}"); files = sorted(os.path.relpath(os.path.join(r, f), snap) for r, _, fl in os.walk(snap) for f in fl) if os.path.isdir(snap) else None
        if files is None: raise E(f"snapshot mem-{x} missing")
        if lines in (["ABSENT"], ["EMPTY_DIR"]):
            if files: raise E(f"mem-{x} manifest says {lines[0]} but snapshot has files")
        else:
            pairs = [re.fullmatch(r"([0-9a-f]{64})  \./(.+)", l) for l in lines]
            if not lines or not all(pairs) or len({q.group(2) for q in pairs}) != len(pairs): raise E(f"mem-{x} manifest malformed")
            if sorted((q.group(2), q.group(1)) for q in pairs) != [(f, h(os.path.join(snap, f))) for f in files]: raise E(f"mem-{x} manifest does not match snapshot")
        mans[x] = lines
    if kind != "D":
        same = mans["after-s1"] == mans["before-s2"]
        if (rd("mem-compare").strip() == "same") != same: raise E("mem-compare flag disagrees with manifests")
        if not same: raise I("memory changed between sessions")
    if rd("mem-before-s1.manifest").strip() != "ABSENT": raise I("memory present before first call")
    if kind == "D" and rd("mem-before-s2.manifest").strip() != "ABSENT": raise I("D memory present before its call")
    if kind != "D" and rd("mem-compare").strip() != "same": raise I("memory changed between sessions")
    disp = rd("disposition.txt").splitlines()
    if "HOLD awaiting adjudication" not in disp: raise E("disposition lacks expected adjudication HOLD")
    other = [l for l in disp if l != "HOLD awaiting adjudication" and not l.startswith("HOLD candidate ")]
    if other: raise I(f"integrity HOLD {other}")
    fc = js("candidate-r63.json")
    if not (isinstance(fc, dict) and isinstance(fc.get("candidate"), dict) and isinstance(fc["candidate"].get("outcome"), str)): raise E("candidate schema invalid")
    cand = json.loads(json.dumps(g63.candidate(os.path.join(a, "log"), target, os.path.join(a, "report.md"))))
    if cand != fc["candidate"]: raise E("recomputed candidate differs from frozen")
    if receipt:
        try: rec = json.load(open(receipt))
        except (OSError, ValueError, UnicodeDecodeError): raise Hold("HOLD", "receipt unreadable or malformed")
        if not isinstance(rec, dict) or rec.get("label") != label or rec.get("arm_claim_sha256") != ch: raise Hold("HOLD", "receipt not bound to this arm")
    g = g63.gate(cand, receipt)
    return {"status": g["status"], "reason": g["reason"], "final_outcome": g["final_outcome"], "final_primary": g["final_primary"], "candidate": cand["outcome"], "arm_claim_sha256": ch}
def main(label, receipt, evd, fin):
    try: r = check(label, receipt, evd)
    except Hold as x: r = {"status": x.status, "reason": x.why, "final_outcome": None, "final_primary": False}
    r.update(label=label, at=datetime.now(timezone.utc).isoformat(), receipt=receipt, receipt_sha256=(h(receipt) if receipt and os.path.isfile(receipt) else None), finalizer_sha256=h(ME))
    d = os.path.join(fin, label); os.makedirs(os.path.join(d, "attempts"), exist_ok=True)
    ap = os.path.join(d, "attempts", f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{secrets.token_hex(4)}.json")
    r["terminal"] = r["status"] in ("FINAL", "FINAL_INVALID")
    with open(ap, "x") as f: json.dump(r, f, indent=1)
    rc = 0
    if r["terminal"]:
        try: os.link(ap, os.path.join(d, "terminal.json")); r["terminal_written"] = True
        except FileExistsError: r["terminal_written"] = False; rc = 4
    print(json.dumps({**r, "attempt": ap}, indent=1)); return rc
if __name__ == "__main__":
    L = sys.argv[1]; R = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    sys.exit(main(L, R, sys.argv[3] if len(sys.argv) > 3 else f"{PK}/R67-identity-boundary-validation/evidence",
                  sys.argv[4] if len(sys.argv) > 4 else f"{PK}/R67-identity-boundary-validation/finalized"))
