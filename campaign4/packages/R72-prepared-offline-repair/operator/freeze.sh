#!/bin/sh
# Immutable per-arm bundle: sh freeze.sh LABEL OPDIR EVIDENCE_DIR. Temp dir + rename; refuses to overwrite; arm-claim.json
# lists every file hash plus the frozen dependency hashes; missing standard artefacts are listed as missing, not invented.
set -u; L=$1; OP=$2; E=$3; mkdir -p $E
[ -e $E/$L ] && { echo "HOLD bundle exists, not overwriting" >> $OP/disposition.txt; exit 1; }
T=$E/.tmp-$L-$$; mkdir -p $T && cp -a $OP/. $T/ && mv $T $E/$L || exit 1
python - $E/$L $L <<'PY'
import json, hashlib, os, sys
from datetime import datetime, timezone
d, L = sys.argv[1], sys.argv[2]; PK = "/var/home/bmosher/memory-bake-off/campaign4/packages"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
fs = {os.path.relpath(os.path.join(r, f), d): h(os.path.join(r, f)) for r, _, fl in os.walk(d) for f in fl if f != "arm-claim.json"}
std = ["paths.json", "calls", "log", "arm.s1.meta", "arm.s1.jsonl", "arm.s2.meta", "arm.s2.jsonl", "arm.s1.prompt.txt", "arm.s2.prompt.txt",
       "candidate-r63.json", "operator-meta.json", "report.md", "disposition.txt", "mem-compare", "events-s1.json", "events-s2.json", "scan-gate-s1.json", "scan-gate-s2.json", "mem-before-s1.manifest",
       "mem-after-s1.manifest", "mem-before-s2.manifest", "mem-after-s2.manifest"]
R64 = f"{PK}/R72-prepared-offline-repair"
deps = [f"{R64}/{p}" for p in ("operator/run-arm.sh", "operator/freeze.sh", "operator/finalize.py", "launch/common.sh", "launch/session.sh", "fixture/bench.sh", "fixture/setup.sh",
        "templates/session1-N.txt", "templates/session1-I.txt", "templates/session1-R-12288.txt", "templates/session1-R-24576.txt",
        "templates/session2.md", "fixtures/RD-12288/MEMORY.md", "fixtures/RD-12288/bench-prefs.md", "fixtures/RD-24576/MEMORY.md", "fixtures/RD-24576/bench-prefs.md", "fixtures/ID/MEMORY.md", "fixtures/ID/fetch-fallback.md")] + [f"{PK}/R56-context-runner-readiness/scanner/{p}" for p in ("scan.py", "operator/scan_gate.py")] + [
        f"{R64}/operator/gate_r72.py", f"{PK}/R54-memory-dependent-task-design/events.py"]
json.dump({"arm": L, "at": datetime.now(timezone.utc).isoformat(), "files_sha256": fs, "missing": [s for s in std if s not in fs],
           "dependency_sha256": {p: h(p) for p in deps}}, open(os.path.join(d, "arm-claim.json"), "w"), indent=1)
PY
