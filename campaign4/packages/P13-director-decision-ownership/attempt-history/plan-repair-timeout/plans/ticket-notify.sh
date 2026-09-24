#!/bin/bash
# P13 fixture ticket stub (versioned; installed by the live plan). Records the
# labelled Claude notice to the fixture ticket log. No real Signal page.
set -u
echo "$(date -u +%FT%TZ) TICKET-NOTICE: $*" >> "${FIXTURE_TICKET_LOG:-/dev/null}"
