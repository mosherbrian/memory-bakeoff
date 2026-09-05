#!/usr/bin/env python3
"""Gen102 summary: paired arms, three mechanism kinds kept apart. No supersession score."""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import supersession_binding as SB   # noqa: E402

OUT = ROOT / "results" / "supersession_ablation_gen102"
ARMS = {"perseus": ("off", "on"), "hindsight": ("off", "on"),
        "mem0": ("off",), "agentmemory": ("on",)}


def load(engine, arm):
    path = OUT / f"{engine}-{arm}.json"
    return json.loads(path.read_text())["rows"] if path.exists() else None


def fold(rows):
    per = {}
    for row in rows:
        key = (row["core"], row["load"])
        per.setdefault(key, []).append(row)
    return {f"{core}|L{load}": {
        "stale_retrievable": {r["superseded_retrievable"] for r in group} == {True},
        "current_retrievable": {r["current_retrievable"] for r in group} == {True},
        "current_rank": sorted({r.get("current_rank") for r in group},
                               key=lambda v: (v is None, v)),
    } for (core, load), group in sorted(per.items())}


def main() -> int:
    report = {"mechanism_kinds": SB.kinds(), "engines": {}}
    for engine, arms in ARMS.items():
        entry = {"kind": SB.BINDINGS[engine]["kind"], "arms": {}}
        for arm in arms:
            rows = load(engine, arm)
            entry["arms"][arm] = fold(rows) if rows else None
        if SB.BINDINGS[engine].get("available_in_pinned_profile") is False:
            entry["on_arm_status"] = SB.BINDINGS[engine]["arm_status"]
            entry["why"] = SB.BINDINGS[engine]["why_unavailable"]
        if engine in ("agentmemory",):
            entry["single_arm"] = ("automatic mechanism; an OFF arm is a "
                                   "configuration the product does not offer")
        report["engines"][engine] = entry

    # The comparison that matters, stated per engine and never pooled.
    effect = {}
    for engine, entry in report["engines"].items():
        off, on = entry["arms"].get("off"), entry["arms"].get("on")
        if not off or not on:
            effect[engine] = {"paired": False,
                              "reason": entry.get("on_arm_status")
                              or entry.get("single_arm")}
            continue
        removed = sum(1 for k in off
                      if off[k]["stale_retrievable"] and not on[k]["stale_retrievable"])
        lost = sum(1 for k in off
                   if off[k]["current_retrievable"] and not on[k]["current_retrievable"])
        effect[engine] = {"paired": True, "cells": len(off),
                          "stale_removed_in": removed,
                          "current_newly_lost_in": lost,
                          "kind": entry["kind"]}
    report["effect_per_engine"] = effect
    report["no_supersession_score"] = (
        "explicit lineage, a state transition and a product decision are three "
        "different mechanisms; they are reported separately and never summed")
    (OUT / "summary.json").write_text(json.dumps(report, indent=1, sort_keys=True,
                                                 default=str))
    for engine, entry in effect.items():
        print(f"{engine:12s} {report['engines'][engine]['kind']:<18} {entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
