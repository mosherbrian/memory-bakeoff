#!/bin/bash
# P13 runnable fixture turn: produces the artifact, the agent-loop claim and
# the stream end for one turn. Executed by the offline harness (and, live, by
# the seat following the task text). Every effect is a real file the candidate
# binary then reads; nothing is synthetic.
#   decision-turn.sh --artifacts DIR --claims DIR --stream FILE --item ID \
#     --action A --execution E --step S --outcome completed|failed [--check C]
set -uo pipefail
ARTIFACTS=""; CLAIMS=""; STREAM=""; ITEM=""; ACTION=""; EXECUTION=""; STEP=""; OUTCOME=""; CHECK=""
while [ $# -gt 0 ]; do case "$1" in
  --artifacts) ARTIFACTS=$2; shift 2;; --claims) CLAIMS=$2; shift 2;;
  --stream) STREAM=$2; shift 2;; --item) ITEM=$2; shift 2;;
  --action) ACTION=$2; shift 2;; --execution) EXECUTION=$2; shift 2;;
  --package) PACKAGE=$2; shift 2;; --step) STEP=$2; shift 2;; --outcome) OUTCOME=$2; shift 2;;
  --check) CHECK=$2; shift 2;; *) echo "unknown arg $1" >&2; exit 2;; esac; done
for v in PACKAGE ARTIFACTS CLAIMS STREAM ITEM ACTION EXECUTION STEP OUTCOME; do
  [ -n "${!v}" ] || { echo "missing --$(echo "$v" | tr '[:upper:]' '[:lower:]')" >&2; exit 2; }; done
mkdir -p "$ARTIFACTS" "$CLAIMS" "$(dirname "$STREAM")"
printf 'fixture-bytes-%s-%s' "$ACTION" "$EXECUTION" >"$ARTIFACTS/out.bin"
SHA=$(sha256sum "$ARTIFACTS/out.bin" | cut -d' ' -f1)
python3 - "$CLAIMS/$EXECUTION.json" <<PY
import json, sys
claim = {"package": "$PACKAGE", "attempt": "a1", "action": "$ACTION",
 "execution": "$EXECUTION", "contract_step": "$STEP", "outcome": "$OUTCOME",
 "artifacts": {"out.bin": {"path": "out.bin", "sha256": "$SHA"}}}
json.dump(claim, open(sys.argv[1], "w"), sort_keys=True)
PY
printf '{"t": "end", "item": "%s"}\n' "$ITEM" >>"$STREAM"
echo "turn done: $ACTION/$EXECUTION/$STEP $OUTCOME claim=$CLAIMS/$EXECUTION.json"
