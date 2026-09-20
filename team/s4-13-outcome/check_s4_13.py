#!/usr/bin/env python3
"""Declared check for QUEUE row S4-13 (executable, exit-code gated).

1. part (a): re-run m4_replay.py, verify rc 0, no harness findings, frozen
   bundle sha cited, replay counts exactly-once (286 unique), RI dedup 26->1;
2. part (b): re-run m124_window_table.py, verify rc 0, no findings, window
   values equal team/WINDOW-campaign-1.json's declared instants, M1 medians
   reproduce the S4-9 report cross-check values exactly;
3. determinism: both re-runs reproduce the committed outputs on every key
   except generated_at_utc;
4. the receipt file exists and cites the bundle sha and the window file.

Exit 0 iff all hold.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TEAM = Path("/var/home/bmosher/memory-bake-off/team")
HERE = TEAM / "s4-13-outcome"
FROZEN_BUNDLE_SHA = "88f875e7a7eb94663033d4a0dc684537486266ea3d51099ad945394f50095d10"
CHECKS = [
    (HERE / "m4_replay.py", HERE / "calibration.json"),
    (HERE / "m124_window_table.py", HERE / "m124-window-summary.json"),
]


def run_and_load(script, committed):
    """Re-run the runner (it overwrites its committed output deterministically)
    and return (before, after) as parsed JSON for the byte-diff check."""
    before = json.loads(Path(committed).read_text())
    r = subprocess.run([sys.executable, str(script)], capture_output=True,
                       text=True, timeout=600)
    if r.returncode != 0:
        return None, None, f"{script.name} exited {r.returncode}: {r.stderr[-200:]}"
    return before, json.loads(Path(committed).read_text()), None


def strip_time(d):
    return {k: v for k, v in d.items() if k != "generated_at_utc"}


def main():
    findings = []
    for script, committed in CHECKS:
        before, fresh, err = run_and_load(script, committed)
        if err:
            findings.append(err)
            continue
        if strip_time(before) != strip_time(fresh):
            findings.append(f"{Path(committed).name}: re-run differs from committed output")
        if fresh.get("harness_findings"):
            findings.append(f"{Path(committed).name}: harness findings: {fresh['harness_findings']}")

    cal = json.loads((HERE / "calibration.json").read_text())
    if cal["bundle_sha256"] != FROZEN_BUNDLE_SHA:
        findings.append("calibration.json does not cite the frozen bundle sha")
    rc = cal["replay_counts"]
    if rc["n_unique_event_ids"] != 286 or rc["n_events"] != 286:
        findings.append("replay is not exactly-once over 286 events")
    if not (rc["ri_events"] == 26 and rc["ri_groups"] == 1):
        findings.append(f"RI dedup unexpected: {rc['ri_events']} events / {rc['ri_groups']} groups")

    summ = json.loads((HERE / "m124-window-summary.json").read_text())
    win = json.loads((TEAM / "WINDOW-campaign-1.json").read_text())
    if summ["window"]["start_utc"] != win["start_utc"] or summ["window"]["end_utc"] != win["end_utc"]:
        findings.append("summary window does not equal the S4-9-declared instants")
    m1 = summ["M1"]
    if m1["median_token_delta_pct_crosscheck"] != m1["crosscheck_target_S4_9"]["tokens"]:
        findings.append("M1 token median does not reproduce S4-9")
    if m1["median_wall_delta_pct_crosscheck"] != m1["crosscheck_target_S4_9"]["wall"]:
        findings.append("M1 wall median does not reproduce S4-9")

    table = HERE / "m124-window-table.md"
    n_rows = sum(1 for l in table.open() if l.startswith("| ") and not l.startswith("| pair")) if table.exists() else 0
    if n_rows != 122:
        findings.append(f"table has {n_rows} pair rows, expected 122")

    receipt = TEAM / "S4-13-OUTCOME-MEASUREMENT-RECEIPT.md"
    if not receipt.exists():
        findings.append("receipt missing")
    else:
        text = receipt.read_text()
        if FROZEN_BUNDLE_SHA not in text or "WINDOW-campaign-1.json" not in text:
            findings.append("receipt does not cite the frozen bundle sha and/or window file")

    for f in findings:
        print(f"FINDING: {f}")
    print(f"s4-13 check: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
