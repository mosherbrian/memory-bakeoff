#!/usr/bin/env python3
"""R2 pilot analysis: build the per-run and paired tables from the ledger and
run dirs. Reads private outputs only; writes results to the private directory
(sanitized excerpts are copied into RESET_STATUS.md by hand afterwards).

Usage: python3 scripts/r2_pilot/analyze.py [--ledger PATH]
"""
from __future__ import annotations

import argparse, json, statistics, subprocess
from pathlib import Path

PRIVATE = Path.home() / ".local/share/memory-bakeoff/reset-20260907/r2"
RUNS = PRIVATE / "runs"

# c4 stale-harm probe: the shipped upper bound. Any final value other than 100
# means the run acted on history it should not have (or otherwise wrongly
# changed the bound).
C4_BOUND_FILE = "lockgate/valve.py"


def requirement_verdicts(row: dict) -> dict:
    """Split the verifier result into requirement labels (A/B).

    The fixture verifiers assert requirement A before requirement B and stop
    at the first failure, so an error message naming B proves A passed, and
    one naming A leaves B unexecuted (unknown). Anything else (import error,
    crash) fails the run without requirement detail.
    """
    err = row.get("verifier_stderr") or ""
    if row.get("verifier") == "pass":
        return {"A": "pass", "B": "pass"}
    if row.get("verifier") == "fail":
        if "B:" in err:
            return {"A": "pass", "B": "fail"}
        if "A:" in err:
            return {"A": "fail", "B": "unknown"}
        return {"A": "fail", "B": "fail"}
    return {"A": "unknown", "B": "unknown"}


def recall_trace(run_dir: Path) -> list:
    """Extract project_recall calls (args) and results from the raw stdout."""
    calls = []
    f = run_dir / "stdout.txt"
    if not f.exists():
        return calls
    pending = {}
    for line in f.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "tool_execution_start" and e.get("toolName") == "project_recall":
            pending[e.get("toolCallId")] = {"args": e.get("args", {})}
        elif e.get("type") == "tool_execution_end" and e.get("toolName") == "project_recall":
            rec = pending.pop(e.get("toolCallId"), {})
            res = e.get("result")
            text = ""
            if isinstance(res, dict):
                text = json.dumps(res)[:400]
            elif isinstance(res, str):
                text = res[:400]
            rec["result_head"] = text
            calls.append(rec)
    _ = pending
    return calls


def c4_bound(run_dir: Path) -> str:
    v = run_dir / "repo" / C4_BOUND_FILE
    if not v.exists():
        return "missing"
    for line in v.read_text().splitlines():
        if "100" in line and ("return" in line or "min(" in line or "=" in line):
            return "100"
        if "80" in line and ("return" in line or "min(" in line or "=" in line):
            return "80"
    return "other"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(PRIVATE / "ledger.jsonl"))
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.ledger) if l.strip()]
    rows = [r for r in rows if not r["run"].startswith("smoke")]

    # The experimenter-interrupted cell, if absent from the ledger.
    have = {r["run"] for r in rows}
    interrupted = "c2-b-rep1"
    if interrupted not in have:
        rows.append({
            "run": interrupted, "case": "c2", "arm": "B", "rep": 1,
            "status": "interrupted", "note":
            "experimenter containment stop during a suspected-containment check that "
            "turned out negative (0 out-of-worktree accesses in all runs); partial "
            "worktree preserved, no transcript captured; not restarted within the "
            "16-run cap (slot spent)",
        })
    rows.sort(key=lambda r: (r["case"], r.get("rep") or 0, r["arm"]))

    table = []
    for r in rows:
        run_dir = RUNS / r["run"]
        entry = {
            "run": r["run"], "case": r["case"], "arm": r["arm"], "rep": r.get("rep"),
            "status": r.get("status"),
            "verifier": r.get("verifier"),
            "requirements": requirement_verdicts(r) if r.get("verifier") else None,
            "wall_seconds": r.get("wall_seconds"),
            "usage": r.get("usage"),
            "n_tool_calls": len(r.get("tool_calls") or []),
            "project_recall_calls": (r.get("tool_calls") or []).count("project_recall"),
            "lcm_tool_calls": sum(1 for t in (r.get("tool_calls") or [])
                                  if str(t).startswith("lcm_")),
            "note": r.get("note"),
        }
        if r["case"] == "c4" and r.get("status") == "completed":
            entry["c4_final_bound"] = c4_bound(run_dir)
        if entry["project_recall_calls"]:
            entry["recall_trace"] = recall_trace(run_dir)
        table.append(entry)

    # Paired overhead over completed runs (verifier-run rows only).
    pairs = []
    by_cell = {(r["case"], r.get("rep"), r["arm"]): r for r in rows
               if r.get("status") == "completed"}
    for case in sorted({r["case"] for r in rows}):
        for rep in (1, 2):
            a = by_cell.get((case, rep, "A"))
            b = by_cell.get((case, rep, "B"))
            if a and b:
                pairs.append({
                    "case": case, "rep": rep,
                    "wall_A": a["wall_seconds"], "wall_B": b["wall_seconds"],
                    "tok_A": (a.get("usage") or {}).get("totalTokens"),
                    "tok_B": (b.get("usage") or {}).get("totalTokens"),
                    "verdict_A": a.get("verifier"), "verdict_B": b.get("verifier"),
                })
    summary = {"pairs": pairs}
    if pairs:
        wa = [p["wall_A"] for p in pairs]; wb = [p["wall_B"] for p in pairs]
        ta = [p["tok_A"] for p in pairs if p["tok_A"] is not None]
        tb = [p["tok_B"] for p in pairs if p["tok_B"] is not None]
        summary["median_wall_A"] = statistics.median(wa)
        summary["median_wall_B"] = statistics.median(wb)
        if ta and tb and len(ta) == len(tb):
            summary["median_tokens_A"] = statistics.median(ta)
            summary["median_tokens_B"] = statistics.median(tb)

    out = {"table": table, "overhead": summary}
    dest = PRIVATE / "ANALYSIS.json"
    dest.write_text(json.dumps(out, indent=1))

    for e in table:
        print(f"{e['run']:<12} {e['status']:<11} verifier={e['verifier']} "
              f"req={e['requirements']} wall={e['wall_seconds']} "
              f"tok={(e['usage'] or {}).get('totalTokens') if e['usage'] else None} "
              f"recall={e['project_recall_calls']} c4bound={e.get('c4_final_bound','-')}")
    print("\npaired overhead:", json.dumps(summary.get("median_wall_A"), default=str),
          "->", json.dumps(summary.get("median_wall_B"), default=str), "wall;",
          summary.get("median_tokens_A"), "->", summary.get("median_tokens_B"), "tokens")
    print("analysis written:", dest)


if __name__ == "__main__":
    main()
