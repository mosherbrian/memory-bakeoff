#!/bin/bash
export AGENTDECK_PROFILE=campaign4
while read -r id; do [ -n "$id" ] || continue; agent-deck session stop "$id"; agent-deck session remove "$id"; done < "/home/bmosher/p13-prep-p13l4/fixture-ids.txt" >> "/home/bmosher/p13-prep-p13l4/cleanup.log" 2>&1
