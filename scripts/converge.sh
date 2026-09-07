#!/usr/bin/env bash
# Wait for the overnight chain, then hand the loop back to Sol.
# The doorbell has its own gates: recap required, review newer than HEAD, review
# not FIX FIRST, ledger clean, tree clean, origin/main pin. This does not bypass
# any of them - if it refuses, that refusal is the outcome and it is logged.
set -uo pipefail
cd /var/home/bmosher/pilot-gen45
while systemctl --user is-active --quiet overnight-ordering; do sleep 60; done
echo "=== $(date -Is) overnight chain finished; attempting convergence ==="
LATEST=$(ls -td /var/home/bmosher/rivals/reviews/*/ | head -1)
echo "latest review: $LATEST"
cat "$LATEST/decision.txt" 2>/dev/null || echo "(no decision.txt)"
echo "--- dry run ---"
python scripts/doorbell 124 handoff/GEN124_RECAP.md handoff/GEN124_TECHNICAL.md
RC=$?
if [ $RC -ne 0 ]; then
  echo "=== $(date -Is) doorbell REFUSED (rc=$RC). Not rung. This is the gate working. ==="
  exit $RC
fi
echo "--- firing ---"
python scripts/doorbell --fire 124 handoff/GEN124_RECAP.md handoff/GEN124_TECHNICAL.md
echo "=== $(date -Is) convergence attempt complete ==="
