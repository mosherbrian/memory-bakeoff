"""`gate-suitability-report-v1`: report the three numbers, retire the verdict word.

Across Gen60, Gen61, Gen62 and Gen64 the frozen screen returned PASSED four
times while the evidence underneath it moved from "half the banks are unusable"
to "the banks are empty" and back again. A verdict that survives all of that is
not reporting the thing the programme is trying to learn.

So this replaces the headline with the quantities it was hiding. For a given
generation it states, without collapsing them into a word:

- **unsafe bank rate** - how many banks reject a known-correct implementation,
  which is the false-alarm measure that decides whether a gate is usable;
- **retention** - how much of each bank survived whatever filter ran, so a
  filter cannot buy safety by deleting evidence;
- **detection** - which known-wrong implementations were caught, and which
  previously-caught ones were lost, named individually.

There is deliberately no threshold and no pass/fail here. The old screen still
exists and still runs; this reads the same recorded outcomes and refuses to
summarise them into a single claim, because that summary is what went wrong.
"""
from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "gate-suitability-report-v1"


def unsafe_rate(result: dict[str, Any]) -> tuple[int, int]:
    """Banks that reject known-correct code, over banks that exist at all."""
    statuses = result.get("statuses", {})
    considered = [n for n, s in statuses.items() if s != "NO_BANK"]
    unsafe = [n for n in considered if statuses[n] in ("UNSAFE_AS_GATE",)]
    return len(unsafe), len(considered)


def caught(result: dict[str, Any]) -> tuple[int, int]:
    return result.get("flagged_wrongs", 0), \
        result.get("primary_population", {}).get("wrong_candidates", 0)


def detection_losses(result: dict[str, Any], baseline: dict[str, Any]) -> list[str]:
    """Wrongs the baseline caught that this run does not, named.

    Restricted to tasks BOTH runs actually scored. Comparing raw caught-sets
    across runs counts tasks that entered or left the eligible population as
    detection changes, which they are not - Gen62's population grew from four
    tasks to seven precisely because its banks stopped being unsafe, and that
    must not be read as catching more or losing more.
    """
    shared = (set(result.get("primary_population", {}).get("tasks", []))
              & set(baseline.get("primary_population", {}).get("tasks", [])))

    def caught_set(payload: dict[str, Any]) -> set[str]:
        found = set()
        for task, entry in payload.get("tasks", {}).items():
            if task not in shared:
                continue
            for name, outcome in entry.get("wrongs", {}).items():
                if not outcome.get("passed"):
                    found.add(f"{task}/{name}")
        return found
    return sorted(caught_set(baseline) - caught_set(result))


def report(label: str, result: dict[str, Any],
           baseline: dict[str, Any] | None = None) -> dict[str, Any]:
    unsafe, banks = unsafe_rate(result)
    found, wrongs = caught(result)
    kept = {k: v for k, v in (result.get("retention") or {}).items() if v is not None}
    return {
        "generation": label,
        "unsafe_banks": unsafe, "banks_considered": banks,
        "unsafe_rate": unsafe / banks if banks else None,
        "retention_min": min(kept.values()) if kept else None,
        "retention_max": max(kept.values()) if kept else None,
        "banks_hollowed": len(result.get("hollowed_tasks", [])),
        "wrongs_caught": found, "wrongs_in_population": wrongs,
        "detection_losses_vs_baseline": (
            detection_losses(result, baseline) if baseline else []),
        "comparison_tasks": sorted(
            set(result.get("primary_population", {}).get("tasks", []))
            & set((baseline or {}).get("primary_population", {}).get("tasks", []))
        ) if baseline else [],
        "gate_suitable": None,
        "why_no_verdict": "gate suitability is not a single number; read the unsafe "
                          "rate, the retention range and the named detection losses",
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "replaces": "PASSED/FAILED as the headline for the generated-evidence question",
        "why": "the frozen screen returned PASSED for a run with half its banks "
               "unusable, for a run that changed nothing, and for a run that had "
               "deleted 84% of its tests; the word tracked none of it",
        "reports": ["unsafe bank rate", "retention range", "banks hollowed",
                    "wrongs caught out of the eligible population",
                    "detection losses named individually"],
        "no_threshold": "this module applies no bar and reaches no verdict; the "
                        "screen still exists and still runs, and its output is "
                        "recorded as secondary",
        "reads_only": "committed outcome files; no model call, no re-run",
    }
