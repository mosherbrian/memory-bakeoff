#!/bin/bash
# P13 fixture wake (reviewed source; installed to the private ROOT by the
# live plan). Logs the delivery and reports started. Delivery evidence goes
# to $FIXTURE_WAKE_LOG (per-run file, exported by the plan).
set -u
echo "$(date -u +%FT%TZ) wake $1 $2" >> "${FIXTURE_WAKE_LOG:-/dev/null}"
echo "wake: $1 -> started"
