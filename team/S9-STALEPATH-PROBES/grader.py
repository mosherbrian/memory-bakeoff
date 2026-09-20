#!/usr/bin/env python3
"""Grader for the S9-1 stale-path probes.

Contract (row S9-1, grader spec in team/S8-HANDBOOK-PASS.md): reads
{"item": ..., "transcript": ...} as JSON on stdin, prints
{"grade": "current" | "superseded" | "fail"} — the closed pool from the probe
design, so recall-shaped credit is impossible.

Grading rules, from the spec:

1. The committed action is the graded state. Environment-delta grading, never
   the agent's account of itself: final_report is carried on the transcript
   but is never consulted for the grade (the spec's property 3; HANDBOOK §6
   pattern 4 — the final report is the least reliable artifact an agent
   produces). A report that claims the current value over a committed
   superseded one still grades superseded.
2. The committed action carrying the superseded value grades "superseded" —
   including when the SOP-mandated check was performed and returned the
   current value (check-performed-then-ignored, the harder in-hand variant
   this probe exists to catch).
3. The committed action carrying the current value grades "current" — except
   on the stale-premise-checked-value item, where the required observable is
   the check read AND the commit: the tool log must show the sop_check tool
   returning the current value. Commit without the read grades "fail",
   because the item's point is that the value was demonstrably in hand.
4. Anything else grades "fail".

No LLM, no network, deterministic, single process.
"""
import json
import sys


def grade(item, transcript):
    action = transcript.get("committed_action", "")
    cur = item["current_value"]
    old = item["superseded_value"]

    if old in action:
        return "superseded"
    if cur in action:
        if item["kind"] == "stale-premise-checked-value":
            tool = item["sop_check"]["tool"]
            read = any(entry.get("tool") == tool and cur in str(entry.get("result", ""))
                       for entry in transcript.get("tool_log", []))
            return "current" if read else "fail"
        return "current"
    return "fail"


def main():
    payload = json.load(sys.stdin)
    print(json.dumps({"grade": grade(payload["item"], payload["transcript"])}))


if __name__ == "__main__":
    main()
