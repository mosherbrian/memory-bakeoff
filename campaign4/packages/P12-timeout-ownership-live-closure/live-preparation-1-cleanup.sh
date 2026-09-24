#!/usr/bin/env bash
# P12-prepare-1 exact-ID cleanup fallback. Stops/removes ONLY the IDs in ids.txt.
set -u
D=/home/bmosher/memory-bake-off/campaign4/packages/P12-timeout-ownership-live-closure/live-preparation-1
IDS="$D/fixture-ids.txt"
ARCH="$D/cleanup-archive"
mkdir -p "$ARCH"
export AGENTDECK_PROFILE=campaign4
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
agent-deck -p campaign4 list --json > "$ARCH/$STAMP-registry-before.json" 2>&1
[ -f "$IDS" ] || { echo "no ids file; nothing owned" > "$ARCH/$STAMP-results.txt"; exit 0; }
: > "$ARCH/$STAMP-results.txt"
while read -r ID; do
  [ -n "$ID" ] || continue
  for op in stop remove; do
    agent-deck session "$op" "$ID" >> "$ARCH/$STAMP-results.txt" 2>&1
    echo "rc=$? $op $ID" >> "$ARCH/$STAMP-results.txt"
  done
done < "$IDS"
