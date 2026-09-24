#!/bin/bash
# P13 fixture pager stub: the private watcher's page goes here, never to Signal.
echo "PAGE $*" >> "${FIXTURE_TICKET_LOG:-/dev/null}.pages"
cat >> "${FIXTURE_TICKET_LOG:-/dev/null}.pages"
