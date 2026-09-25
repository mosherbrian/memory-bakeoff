"""R25 reproducer: six synthetic checker cases with isolated semantic grading.

Builds valid capture dirs (correct hashes/identity/times) under temp/,
varying ONLY index/diagnosis semantics, then runs the frozen R22
check_capture.check plus an independent full-mapping / fixture-field oracle.
Writes results.json. No participant files read; no frozen sources modified.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
R22 = "/var/home/bmosher/memory-bake-off/campaign4/packages/R22-persistence-trial-preparation"
sys.path.insert(0, R22)
import check_capture  # noqa: E402  (frozen checker, read-only use)

DOCS = os.path.join(R22, "fixtures", "docs")
FAIL = json.load(open(os.path.join(R22, "fixtures", "failure.json")))


def expected_mapping():
    """Separately implemented full token->file mapping (no `re`, manual scan)."""
    idx, docs = {}, []
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".txt"):
            continue
        docs.append(name)
        text = open(os.path.join(DOCS, name)).read().lower()
        cur, seen = "", set()
        for ch in text + " ":
            if ch.isalnum():
                cur += ch
            elif cur:
                seen.add(cur)
                cur = ""
        for w in sorted(seen):
            idx.setdefault(w, []).append(name)
    return {"docs": docs, "index": idx}


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def make_capdir(case, output_name, output_obj):
    d = os.path.join(HERE, "temp", case)
    os.makedirs(d, exist_ok=True)
    for f in ("index.json", "diagnosis.json", "escalation.json"):
        p = os.path.join(d, f)
        if os.path.exists(p):
            os.remove(p)
    outp = os.path.join(d, output_name)
    json.dump(output_obj, open(outp, "w"), sort_keys=True)
    t = datetime.now(timezone.utc).isoformat()
    host = os.uname().nodename if hasattr(os, "uname") else "local"
    is_diag = output_name == "diagnosis.json"
    action = "diagnose-index" if is_diag else "rebuild-noextra"
    ev = {"question": "Q-WORK-BENEFIT", "arm": "T", "execution": "ex-R25",
          "action": action, "owner": "kiln", "mode": "normal", "host": host,
          "at": t, "output_sha256": sha_bytes(open(outp, "rb").read())}
    evp = os.path.join(d, "evidence.json")
    json.dump(ev, open(evp, "w"), sort_keys=True)
    rc = dict(ev, evidence_sha256=sha_bytes(open(evp, "rb").read()))
    json.dump(rc, open(os.path.join(d, "receipt.json"), "w"), sort_keys=True)
    cap = {"case": case, "arm": "T", "execution": "ex-R25", "action": action,
           "owner": "kiln", "mode": "normal",
           "capture_started_at": "2026-01-01T00:00:00+00:00",
           "capture_ended_at": "2026-01-01T00:05:00+00:00",
           "stdout": "", "exit": 0}
    # receipt/evidence times must sit inside the capture window
    for f in ("evidence.json", "receipt.json"):
        p = os.path.join(d, f)
        o = json.load(open(p))
        o["at"] = "2026-01-01T00:02:00+00:00"
        json.dump(o, open(p, "w"), sort_keys=True)
    rc = json.load(open(os.path.join(d, "receipt.json")))
    rc["evidence_sha256"] = sha_bytes(open(evp, "rb").read())
    json.dump(rc, open(os.path.join(d, "receipt.json"), "w"), sort_keys=True)
    return d, cap


def main():
    full = expected_mapping()
    cases = {}
    cases["honest-full-index"] = ("index.json", full)
    halo_only = {"docs": full["docs"], "index": {"halo": full["index"]["halo"]}}
    cases["halo-only-index"] = ("index.json", halo_only)
    miss = {"docs": [x for x in full["docs"] if x != "d3.txt"],
            "index": {w: [x for x in ps if x != "d3.txt"]
                      for w, ps in full["index"].items()}}
    miss["index"] = {w: ps for w, ps in miss["index"].items() if ps}
    cases["index-missing-one-doc"] = ("index.json", miss)
    rot = {"d1.txt": "d2.txt", "d2.txt": "d3.txt", "d3.txt": "d1.txt"}
    wrong = {"docs": full["docs"],
             "index": {w: sorted(rot.get(x, x) for x in ps)
                       for w, ps in full["index"].items()}}
    cases["wrong-token-mapping"] = ("index.json", wrong)
    cases["diagnosis-wrong-step"] = ("diagnosis.json",
        {"failed_step": "9/9", "failed_action": FAIL["action"],
         "cause": FAIL["detail"], "exit": 1, "next": "x", "bound": "y"})
    cases["honest-diagnosis"] = ("diagnosis.json",
        {"failed_step": FAIL["step"], "failed_action": FAIL["action"],
         "cause": FAIL["detail"], "exit": FAIL["exit"], "next": "x", "bound": "y"})

    results = []
    for cid, (oname, obj) in cases.items():
        d, cap = make_capdir(cid, oname, obj)
        ok, msg = check_capture.check(cap, d)
        if oname == "index.json":
            indep = "match" if obj == full else "mismatch"
        else:
            indep = ("match" if obj["failed_step"] == FAIL["step"]
                     and obj["failed_action"] == FAIL["action"]
                     and obj["cause"] == FAIL["detail"]
                     and obj["exit"] == FAIL["exit"] else "mismatch")
        results.append({"case": cid, "checker_pass": ok, "checker_msg": msg,
                        "independent": indep,
                        "false_accept": bool(ok and indep == "mismatch"),
                        "false_refuse": bool(not ok and indep == "match")})
    json.dump({"results": results,
               "false_accepts": sum(1 for r in results if r["false_accept"]),
               "false_refusals": sum(1 for r in results if r["false_refuse"])},
              open(os.path.join(HERE, "results.json"), "w"), indent=1)
    for r in results:
        print(r["case"], "checker=", r["checker_pass"], r["checker_msg"],
              "independent=", r["independent"])


if __name__ == "__main__":
    main()
