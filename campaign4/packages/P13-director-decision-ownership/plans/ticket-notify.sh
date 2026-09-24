#!/bin/bash
# P13 fixture Claude-rung adapter (versioned; installed by the live plan next to
# a copy of the installed escalations tool). Writes the PRIVATE HOME ledger
# (HOME is set by the rung's exec) with the installed key rule, and records a
# labelled notice in the fixture ticket log. No chat, no Signal, no shared ledger.
set -u
t=$(cat)
printf '%s\n' "$t" | "$(dirname "$0")/escalations" --add "$1" --source p13-fixture || exit 1
echo "$(date -u +%FT%TZ) FIXTURE-NOTICE $1" >> "${FIXTURE_TICKET_LOG:-/dev/null}"
