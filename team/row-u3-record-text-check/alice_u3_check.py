#!/usr/bin/env python3
"""Alice second-seat of Assay's U3 record-text-identity prototype (`e8da8b03…`).

Independent extractor (own regex/normalizer, does not import the prototype):
recounts ids-with-text, canonical cross-checks, forks/drifts, unindexed, on the
canonical tree; plus a case-SENSITIVE variant to test whether casefolding masks
a fork.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

IMPL = Path("/var/home/bmosher/memory-bake-off/implementer")
REPO = IMPL / "repo"
DSH3 = IMPL / "repo-glm-dsh3"
DSH2 = IMPL / "repo-glm-dsh2"
PROTO = DSH2 / "scripts" / "verify-20260913-assay-record-text-identity" / "record_text_identity_prototype.py"
CANON = REPO / "src" / "memory_bakeoff" / "corpus.py"
ROOTS = [REPO / "results", REPO / "research"]
LINE = re.compile(r"(?:-\s*)?\[(M\d{3,4})\]\s*(.+)")
CANONRE = re.compile(r'R\("(M\d{3,4})",\s*"((?:[^"\\]|\\.)*)"')
EXTS = (".json", ".jsonl", ".csv", ".md", ".txt")

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def n_case(s): return " ".join(s.split()).strip().casefold()
def n_raw(s): return " ".join(s.split()).strip()

def extract(path, norm):
    found = defaultdict(set)
    def add(i, t):
        if t: found[i].add(norm(t))
    raw = path.read_text(encoding="utf-8", errors="replace")
    def walk(o):
        if isinstance(o, str):
            for ln in o.splitlines():
                m = LINE.match(ln.strip())
                if m: add(m.group(1), m.group(2))
        elif isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    if path.suffix == ".json":
        try: walk(json.loads(raw))
        except Exception:
            for ln in raw.splitlines():
                m = LINE.match(ln.strip())
                if m: add(m.group(1), m.group(2))
    elif path.suffix == ".jsonl":
        for ln in raw.splitlines():
            try: walk(json.loads(ln))
            except Exception:
                m = LINE.match(ln.strip())
                if m: add(m.group(1), m.group(2))
    else:
        for ln in raw.splitlines():
            m = LINE.match(ln.strip())
            if m: add(m.group(1), m.group(2))
    return found

def census(norm):
    canon = {i: norm(t) for i, t in CANONRE.findall(CANON.read_text(errors="replace"))}
    found = defaultdict(set)
    for root in ROOTS:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in EXTS:
                try:
                    for i, ts in extract(p, norm).items(): found[i] |= ts
                except OSError: pass
    forks = sorted(i for i, ts in found.items() if len(ts) > 1)
    drift = sorted(i for i, ts in found.items() if len(ts) == 1 and i in canon
                   and next(iter(ts)) != canon[i])
    checked = sorted(i for i in found if i in canon)
    unindexed = sorted(i for i in found if i not in canon)
    return {"ids_with_text": len(found), "canonical_rows": len(canon),
            "checked_vs_canon": len(checked), "forks": forks, "drift": drift,
            "unindexed": len(unindexed)}

out = {"hashes": {"prototype": sha(PROTO), "corpus_repo": sha(CANON),
                  "corpus_dsh3": sha(DSH3/"src"/"memory_bakeoff"/"corpus.py"),
                  "corpus_dsh2": sha(DSH2/"src"/"memory_bakeoff"/"corpus.py")},
       "checks": {}, "findings": []}
out["is_hashed"] = out["hashes"]["prototype"] == "e8da8b039d5091e36bd8bc074bd90f37524a54ed09d1217e6f6cf54fd524d45f"
st = subprocess.run([sys.executable, str(PROTO), "--self-test"], capture_output=True, text=True)
out["checks"]["prototype_self_test_rc"] = st.returncode
out["checks"]["case_insensitive_census"] = census(n_case)
out["checks"]["case_sensitive_census"] = census(n_raw)
# run the prototype itself on the canonical tree
pr = subprocess.run([sys.executable, str(PROTO), "results", "research"],
                    cwd=str(REPO), capture_output=True, text=True)
out["checks"]["prototype_run"] = {"rc": pr.returncode,
                                  "summary": [l.strip() for l in pr.stdout.splitlines() if l.startswith("===")],
                                  "counts": [l.strip() for l in pr.stdout.splitlines() if "forks/drifts" in l]}
c = out["checks"]
if not out["is_hashed"]: out["findings"].append("prototype hash mismatch")
if c["prototype_self_test_rc"] != 0: out["findings"].append("prototype self-test failed")
if c["case_insensitive_census"]["forks"] or c["case_insensitive_census"]["drift"]:
    out["findings"].append("independent census found forks/drift")
if c["case_sensitive_census"]["forks"] and not c["case_insensitive_census"]["forks"]:
    out["findings"].append("casefold masks a case-only fork")
print(json.dumps(out, indent=1)); raise SystemExit(0)
