#!/bin/sh
# R53: freeze one arm's evidence into the package, write its immutable arm claim, hand the review to corvid
# (5 min from handoff), write the handoff receipt outside the claim, and notify Tern.
set -u; L=$1; R=/var/home/bmosher/memory-bake-off/campaign4/packages/R53-restart-memory-trial; OP=/tmp/campaign4-r53-op/$L
T=$R/evidence/.tmp-$L-$$; mkdir -p $T && cp -a $OP/. $T/ && mv $T $R/evidence/$L || exit 1
python - $R/evidence/$L $L <<'PY'
import json, hashlib, os, sys
from datetime import datetime, timezone
d, L = sys.argv[1], sys.argv[2]
fs = {os.path.relpath(os.path.join(r, f), d): hashlib.sha256(open(os.path.join(r, f), "rb").read()).hexdigest() for r, _, fl in os.walk(d) for f in fl if f != "arm-claim.json"}
g = json.load(open(os.path.join(d, "grade-raw.json")))
json.dump({"arm": L, "qid": f"R53-{L}", "question_id": "Q-WORK-BENEFIT", "review_question_id": "Q-EVALUATOR-VALIDITY", "at": datetime.now(timezone.utc).isoformat(),
           "operator_raw": {k: g[k] for k in ("measured", "restored", "primary_PASS")}, "files_sha256": fs}, open(os.path.join(d, "arm-claim.json"), "w"), indent=1)
PY
cd /var/home/bmosher/memory-bake-off/campaign4 && git add packages/R53-restart-memory-trial/evidence/$L && git commit -qm "R53 $L evidence and arm claim" -q
CH=$(sha256sum $R/evidence/$L/arm-claim.json | cut -c1-64); HO=$(date -u +%FT%TZ); DL=$(date -u -d '+5 min' +%FT%TZ)
cat > $R/operator/review-task-$L.txt <<TXT
R53 arm $L review (corvid), ONE verdict, due $DL (5 min from handoff). Read-only, no model calls, no repair.
Evidence: $R/evidence/$L/ (arm-claim.json sha256 $CH): prompts and argv in A*.s1/.s2.meta, s1/s2 jsonl, memory manifests (mem-after-s1, mem-before-s2), oplog, arm-final/, grade-raw.json, scan-gate-s1/s2.json, disposition.txt if any.
Use R53 copies: scanner $R/scanner/scan.py with $R/scanner/operator/scan_gate.py; grader python /var/home/bmosher/memory-bake-off/campaign4/packages/R42-benchmark-trace-repair/grade.py <arm-final copy or original arm path in $L.arm.json> <oplog> <block value>. Follow $R/operator-review-checklist.md and $R/../R53-restart-memory-trial/package.md.
Report separately: save, survival, availability, detail read, inferred index delivery (with caveat), applied, measured, restored, primary, report number, final-state true/false/unstated, refusals, command composition, contamination/integrity, attribution.
Write $R/grades/$L.json and $R/grades/$L.md.
TXT
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake corvid "$(cat $R/operator/review-task-$L.txt)" >/dev/null 2>&1
python -c "import json;json.dump({'arm':'$L','reviewer':'corvid (493c0317-1790000758)','arm_claim_sha256':'$CH','handoff':'$HO','review_deadline':'$DL'},open('$R/operator/handoff-$L.json','w'),indent=1)"
git add $R/operator && git commit -qm "R53 $L review handoff" -q
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R53 $L evidence frozen: $R/evidence/$L/arm-claim.json sha256 $CH; $(tail -1 $OP/run.log | cut -d' ' -f3-); raw $(python -c "import json;d=json.load(open('$R/evidence/$L/grade-raw.json'));print({k:d[k] for k in ('measured','restored','primary_PASS')})"). Review to corvid at $HO, deadline $DL (receipt operator/handoff-$L.json). Next arm waits for your decision." >/dev/null 2>&1
echo "$L handed off $HO -> $DL"
