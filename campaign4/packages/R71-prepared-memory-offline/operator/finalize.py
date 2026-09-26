"""R66 staged finalizer (outside the arm): python finalize.py LABEL RECEIPT|- [EVIDENCE_DIR] [FINAL_DIR]
Implements requirements.md: closure incl. this file, required evidence without defaults, integrity HOLDs, receipt binding, unchanged
R63 gate. Every call writes an immutable attempt; only FINAL/FINAL_INVALID creates the single terminal (atomic, exclusive)."""
import hashlib, importlib.util, json, os, re, secrets, sys, uuid
from datetime import datetime, timezone
PK = "/var/home/bmosher/memory-bake-off/campaign4/packages"; ME = f"{PK}/R71-prepared-memory-offline/operator/finalize.py"; FX = f"{PK}/R71-prepared-memory-offline/fixtures"
spec = importlib.util.spec_from_file_location("g63", f"{PK}/R63-context-evidence-gate/gate.py"); g63 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g63)
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
COMMON = ["paths.json", "calls", "log", "report.md", "disposition.txt", "candidate-r63.json", "operator-meta.json", "arm.s2.meta", "arm.s2.jsonl",
          "scan-gate-s2.json", "events-s2.json", "mem-before-s1.manifest", "mem-before-s2.manifest", "mem-after-s2.manifest"]
S1 = ["arm.s1.meta", "arm.s1.jsonl", "scan-gate-s1.json", "events-s1.json", "mem-after-s1.manifest", "mem-compare"]
BADEV = ("unresolved", "unsupported_shell", "denied")
class Hold(Exception):
    def __init__(s, status, why): s.status, s.why = status, why
CJ = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def pairs(path):
    uses, res, order = {}, {}, []
    for line in open(path):
        e = json.loads(line); m = e.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
        for c in m["content"]:
            if not isinstance(c, dict): continue
            if c.get("type") == "tool_use":
                if c["id"] in uses: raise Hold("HOLD_EVIDENCE", "duplicate tool_use id")
                uses[c["id"]] = c; order.append(c["id"])
            elif c.get("type") == "tool_result":
                if c.get("tool_use_id") in res: raise Hold("HOLD_EVIDENCE", "duplicate tool_result id")
                res[c.get("tool_use_id")] = c
    return uses, res, order
def rtext(r):
    c = r.get("content"); return c if isinstance(c, str) else json.dumps(c)
def extract(a, target, pj, cand):
    uses, res, order = pairs(os.path.join(a, "arm.s2.jsonl")); detail = pj["memory"] + "/bench-prefs.md"; seen = None
    for i in order:
        u = uses[i]; inp = u.get("input") or {}; r = res.get(i)
        reads = (u.get("name") == "Read" and inp.get("file_path") == detail) or (u.get("name") == "Bash" and detail in inp.get("command", ""))
        if reads and r and not r.get("is_error") and target in rtext(r) and seen is None: seen = "observed"
        if u.get("name") == "Bash" and "bench.sh" in inp.get("command", "") and seen is None: seen = "run_before_read"
    p = cand.get("parsed") or {}
    return {"A1_correct": bool(cand.get("runs")) and cand["runs"][-1][0] == target, "A2_guess": p.get("source") == "GUESS", "A3_self_source": p.get("source"),
            "A4_observed_detail_read": "OBSERVED" if seen == "observed" else "NONE_OBSERVED", "A6_contamination": "none observed (scanner clean)"}
SH = re.compile(r"(ls(?: -[la]{1,2})?|cat|head(?: -n \d+)?|tail(?: -n \d+)?|wc(?: -[lwc])?) (/[^\s;&|<>`$()*?\\]+)")
def c2(label, a, ch, pj, evr, events):
    try: rec = json.load(open(evr))
    except (OSError, ValueError): raise Hold("HOLD", "event receipt unreadable")
    tp = os.path.join(a, "arm.s2.jsonl")
    if not isinstance(rec, dict) or rec.get("schema") != "r69-event-adjudication-v1" or rec.get("label") != label or rec.get("arm_claim_sha256") != ch \
       or rec.get("transcript_sha256") != h(tp) or rec.get("events_sha256") != h(os.path.join(a, "events-s2.json")) or str(rec.get("reviewer", "")).lower() in ("", "claude"):
        raise Hold("HOLD", "event receipt not bound to this arm/transcript/events")
    evs = events.get("memory_events", [])
    if any(x.get("event") in ("unresolved", "denied") for x in evs): raise Hold("HOLD", "denied/unresolved events are not clearable (C3)")
    flagged = sorted(x["id"] for x in evs if x.get("event") == "unsupported_shell")
    items = rec.get("events") if isinstance(rec.get("events"), list) else []
    if sorted(str(it.get("tool_use_id")) for it in items) != flagged: raise Hold("HOLD", "event receipt ids do not match flagged events")
    uses, res, _ = pairs(tp); roots = (os.path.realpath(pj["memory_real"]), os.path.realpath(pj["cwd_real"]))
    for it in items:
        u, r = uses.get(it["tool_use_id"]), res.get(it["tool_use_id"])
        if u is None or r is None: raise Hold("HOLD", "event without matched result (C3)")
        if it.get("category") != "C2" or it.get("tool_use_sha256") != CJ(u.get("input")) or it.get("tool_result_sha256") != CJ(r.get("content")): raise Hold("HOLD", "event item hash/category mismatch")
        for s in [s.strip() for s in re.split(r"&&|;", (u.get("input") or {}).get("command", ""))]:
            m = SH.fullmatch(s)
            if not m: raise Hold("HOLD", f"command outside C2 grammar: {s[:60]}")
            rp = os.path.realpath(m.group(2))
            if not any(rp == x or rp.startswith(x + "/") for x in roots): raise Hold("HOLD", "path outside own memory/cwd (C4)")
        if "permission" in rtext(r).lower() or not rtext(r).strip(): raise Hold("HOLD", "unresolved or denied result (C3)")
def check(label, receipt, evd, ev_receipt=None):
    pj0 = lambda: json.load(open(os.path.join(evd, label, 'paths.json')))
    a = os.path.join(evd, label); kind = label.split("-")[-1]; target = label.split("-")[0]
    if kind not in ("RD", "ID", "N") or target not in ("12288", "24576"): raise Hold("HOLD_EVIDENCE", "label not an R71 prepared cell")
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
    need = COMMON
    miss = [f for f in need if f not in claim["files_sha256"]]
    if miss: raise E(f"required evidence missing at freeze {miss}")
    if any(f in claim["files_sha256"] for f in S1): raise E("prepared arm has s1 evidence")
    meta = js("operator-meta.json")
    if not isinstance(meta, dict) or meta.get("label") != label or meta.get("target") != target or meta.get("kind") != kind: raise E("operator-meta label/target/kind mismatch")
    if rd("calls").strip() != "1": raise I("call count wrong")
    for n in (2,):
        t = rd(f"arm.s{n}.meta")
        ex, wr = re.findall(r"^exit=(.*)$", t, re.M), re.findall(r"^wrapper_rc=(.*)$", t, re.M)
        if len(ex) != 1 or len(wr) != 1: raise E(f"s{n} exit/wrapper status absent")
        if ex[0] != "0" or wr[0] != "0": raise I(f"s{n} child={ex[0]} wrapper={wr[0]}")
        sg = js(f"scan-gate-s{n}.json")
        if not isinstance(sg, dict) or "rc" not in sg: raise E(f"scan-gate-s{n} schema invalid")
        if sg.get("rc") != 0 or sg.get("gate") != "clean": raise I(f"scan s{n} not clean")
        ev = js(f"events-s{n}.json")
        if not isinstance(ev, dict) or not isinstance(ev.get("counts"), dict): raise E(f"events-s{n} schema invalid")
        if any(k in ev["counts"] for k in BADEV):
            if not (ev_receipt and set(ev["counts"]) & set(BADEV) == {"unsupported_shell"}): raise I(f"events s{n} {ev['counts']}")
            c2(label, a, ch, pj0(), ev_receipt, ev)   # R71: only C2-cleared unsupported_shell may pass; everything else raised above
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
    for n in (2,):
        t = rd(f"arm.s{n}.meta"); ids = re.findall(r"^session_id=(.*)$", t, re.M)
        if len(ids) != 1: raise E(f"s{n} session_id missing or duplicated")
        try: ok = str(uuid.UUID(ids[0])) == ids[0]
        except ValueError: ok = False
        if not ok: raise E(f"s{n} session_id not a canonical UUID")
        if f"--session-id {ids[0]} " not in t: raise E(f"s{n} argv does not carry its session id")
        sids[f"s{n}"] = ids[0]
    if False: raise E("s1 and s2 share a session id")
    if not isinstance(meta.get("sessions"), dict) or meta["sessions"].get("s2") != sids["s2"] or meta["sessions"].get("s1") != sids.get("s1"): raise E("operator-meta sessions disagree with session meta")
    mans = {}
    for x in ["before-s1", "before-s2", "after-s2"]:
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
    if False:
        same = mans["after-s1"] == mans["before-s2"]
        if (rd("mem-compare").strip() == "same") != same: raise E("mem-compare flag disagrees with manifests")
        if not same: raise I("memory changed between sessions")
    if rd("mem-before-s1.manifest").strip() != "ABSENT": raise I("memory present before first call")
    src = {"RD": f"{FX}/RD-{target}", "ID": f"{FX}/ID", "N": None}[kind]
    exp = ["ABSENT"] if src is None else [f"{h(os.path.join(src, f))}  ./{f}" for f in sorted(os.listdir(src))]
    if sorted(mans["before-s2"]) != sorted(exp): raise E("before-session memory differs from the frozen prepared fixture")
    disp = rd("disposition.txt").splitlines()
    if "HOLD awaiting adjudication" not in disp: raise E("disposition lacks expected adjudication HOLD")
    other = [l for l in disp if l != "HOLD awaiting adjudication" and not l.startswith("HOLD candidate ")]
    evl = "HOLD events s2: unresolved/unsupported/denied memory events (manual)"
    if evl in other and ev_receipt: other.remove(evl)   # c2() already validated above; it raises on any failure
    if other: raise I(f"integrity HOLD {other}")
    fc = js("candidate-r63.json")
    if not (isinstance(fc, dict) and isinstance(fc.get("candidate"), dict) and isinstance(fc["candidate"].get("outcome"), str)): raise E("candidate schema invalid")
    cand = json.loads(json.dumps(g63.candidate(os.path.join(a, "log"), target, os.path.join(a, "report.md"))))
    if cand != fc["candidate"]: raise E("recomputed candidate differs from frozen")
    if receipt:
        try: rec = json.load(open(receipt))
        except (OSError, ValueError, UnicodeDecodeError): raise Hold("HOLD", "receipt unreadable or malformed")
        if not isinstance(rec, dict) or rec.get("label") != label or rec.get("arm_claim_sha256") != ch: raise Hold("HOLD", "receipt not bound to this arm")
    axes = extract(a, target, pj, cand)
    if cand["outcome"] == "candidate_primary" and (cand.get("parsed") or {}).get("source") == "USER": raise Hold("HOLD", "source USER unsupported in prepared arm")
    if cand["outcome"] == "candidate_primary" and kind in ("ID", "N"): raise Hold("HOLD", "attribution unresolved: target claimed without relevant memory")
    g = g63.gate(cand, receipt)
    return {"axes": axes, "status": g["status"], "reason": g["reason"], "final_outcome": g["final_outcome"], "final_primary": g["final_primary"], "candidate": cand["outcome"], "arm_claim_sha256": ch}
def main(label, receipt, evd, fin, ev_receipt=None):
    try: r = check(label, receipt, evd, ev_receipt)
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
    sys.exit(main(L, R, sys.argv[3] if len(sys.argv) > 3 else f"{PK}/R71-prepared-memory-offline/evidence",
                  sys.argv[4] if len(sys.argv) > 4 else f"{PK}/R71-prepared-memory-offline/finalized", sys.argv[5] if len(sys.argv) > 5 else None))
