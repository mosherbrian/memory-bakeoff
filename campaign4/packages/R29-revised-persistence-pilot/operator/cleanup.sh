#!/bin/sh
# R29 absolute-end cleanup: stops ONLY the private run service and the private timer units
# (prefix agent-loop-campaign4-r29-). Stops nothing else; deletes nothing; state and evidence stay.
LOG=/home/bmosher/memory-bake-off/campaign4/packages/R29-revised-persistence-pilot/operator/cleanup-log.txt
{ date -u +%FT%TZ; for u in agent-loop-r29-private-run.service $(systemctl --user list-units --all --plain --no-legend 'agent-loop-campaign4-r29-*' | awk '{print $1}'); do
  echo "stop $u"; systemctl --user stop "$u"; echo "rc=$?"; done; } >> $LOG 2>&1
