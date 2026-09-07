#!/usr/bin/env bash
# What happens after the doorbell, so the night is not hostage to Sol answering.
#
# Last night's failure was polling an answer channel ~90 times and calling it
# blocked. The rule here: Sol gets a bounded window, then the fallback control
# plane authors the next brief, and either way there is queued work that needs
# no control plane at all.
set -uo pipefail
cd /var/home/bmosher/pilot-gen45
while systemctl --user is-active --quiet converge; do sleep 60; done
echo "=== $(date -Is) converge finished ==="
tail -5 research/pilot_ordering/converge.log 2>/dev/null

if ! grep -q "convergence attempt complete" research/pilot_ordering/converge.log 2>/dev/null; then
  echo "=== doorbell did not fire. No Sol window to wait on. Going straight to queued work. ==="
else
  echo "=== $(date -Is) doorbell rang. Sol window: 45 minutes, then fallback. ==="
  for i in $(seq 1 9); do
    sleep 300
    if python scripts/consume-instruction 125 >/dev/null 2>&1; then
      echo "=== $(date -Is) SOL ANSWERED at rung $i. The loop is control-plane directed again. ==="
      exit 0
    fi
  done
  echo "=== $(date -Is) Sol silent for 45m. Fallback control plane authors Gen125. ==="
  RIVALS_OUT=/var/home/bmosher/rivals/proposals/gen125 \
    /var/home/bmosher/rivals/propose-generation /var/home/bmosher/pilot-gen45 || true
  echo "=== $(date -Is) provisional Gen125 brief queued for Sol's ratification ==="
fi

echo "=== $(date -Is) queued work that needs NO control plane ==="
python scripts/verify_substrate.py 2>&1 | tail -40
echo "=== $(date -Is) after-converge done ==="
