"""Grader and aggregation for a FUTURE reader-interference-v5 run.

Tracked and hashed into the Gen116 contract so that "this exact grader ran" is
attestable. Gen114 shipped a runner that did not exist at its pinned commit;
that is the defect this file exists to prevent.

It is NOT executed against a model in Generation 116. Running it requires sealed
response evidence that does not exist yet.
"""
from __future__ import annotations
import json, collections
from pathlib import Path
from typing import Any, Mapping, Sequence
from memory_bakeoff import reader_interference_v6 as V5

CONTROL_CONDITIONS = ("CLEAN_CURRENT", "CLEAN_HISTORICAL_AS_OF", "INSUFFICIENT_CURRENT")
CONFLICT_CONDITIONS = ("CONFLICT_CURRENT_FIRST", "CONFLICT_STALE_FIRST")


def grade_all(responses: Sequence[Mapping[str, Any]],
              cases: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for r in responses:
        case = cases[r["case_id"]]
        parsed = V6.parse_response(r["text"])
        g = V6.grade(parsed, case)
        rows.append({"case_id": r["case_id"], "core": case["core"],
                     "condition": case["condition"], **g})
    return rows


def control_gate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """A core is interpretable only if all three controls pass. Fails closed."""
    by_core: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    for row in rows:
        by_core[row["core"]][row["condition"]] = row["meets_success_state"]
    out = {}
    for core, conds in by_core.items():
        passed = [c for c in CONTROL_CONDITIONS if conds.get(c)]
        out[core] = {"controls_passed": f"{len(passed)}/{len(CONTROL_CONDITIONS)}",
                     "interpretable": len(passed) == len(CONTROL_CONDITIONS),
                     "status": ("INTERPRETABLE" if len(passed) == len(CONTROL_CONDITIONS)
                                else "NOT_INTERPRETABLE_CONTROL_FAILURE")}
    return out


def estimands(rows: Sequence[Mapping[str, Any]], gates: Mapping[str, Any],
              unique_prompts: int) -> dict[str, Any]:
    """Q1-Q9. The independent unit is the CORE; cells are never observations."""
    by = {(r["core"], r["condition"]): r for r in rows}
    cores = sorted({r["core"] for r in rows})
    ok = [c for c in cores if gates[c]["interpretable"]]

    def sel(core, cond):
        r = by.get((core, cond))
        return bool(r and r["meets_success_state"])

    q1 = [c for c in ok if all(sel(c, k) for k in CONFLICT_CONDITIONS)]
    q2 = [c for c in ok if sel(c, "CLEAN_CURRENT")
          and not all(sel(c, k) for k in CONFLICT_CONDITIONS)]
    q3 = [{"core": c,
           "current_first": sel(c, "CONFLICT_CURRENT_FIRST"),
           "stale_first": sel(c, "CONFLICT_STALE_FIRST")}
          for c in ok if sel(c, "CONFLICT_CURRENT_FIRST") != sel(c, "CONFLICT_STALE_FIRST")]
    conflict_rows = [r for r in rows if r["condition"] in CONFLICT_CONDITIONS]
    tally = collections.Counter(r["answer_class"] for r in conflict_rows)
    return {
        "independent_unit": "core",
        "cores_total": len(cores), "cores_interpretable": len(ok),
        "Q1_cores_selecting_current_in_both_orders": f"{len(q1)}/{len(ok)}",
        "Q2_cores_with_interference": [c for c in q2],
        "Q3_order_discordant_cores": q3,
        "Q4_stale_capture_cells": tally[V6.STALE_ONLY] + tally[V6.STALE_WITH_HISTORY],
        "Q5_unresolved_both_cells": tally[V6.UNRESOLVED_BOTH],
        # CURRENT_WITH_HISTORY *is* the reconciliation under a structured
        # contract, and it is a success state. The first draft added a separate
        # RECONCILED_CURRENT count to it, summing a success class with a
        # non-success one under a single number.
        "Q6_reconciled_to_current_cells": tally[V6.CURRENT_WITH_HISTORY],
        "Q7_explicit_simultaneous_contradiction_cells": tally[V6.SIMULTANEOUS],
        "Q8_all_cores_pass_all_controls": all(gates[c]["interpretable"] for c in cores),
        "conflict_cells": len(conflict_rows),
        "unique_prompts": unique_prompts,
        "cells_are_not_observations": True,
        "no_binomial_ci_on_paired_cells": True,
    }


def run_marker(gates: Mapping[str, Any], estim: Mapping[str, Any],
               linkage_ok: bool, seal_ok: bool, manifest_ok: bool) -> dict[str, Any]:
    """RUN_EVIDENCE only if every gate passed. Never backfilled."""
    eligible = bool(linkage_ok and seal_ok and manifest_ok and estim["Q8_all_cores_pass_all_controls"])
    return {"marker": "RUN_EVIDENCE" if eligible else "NON_EVIDENCE",
            "linkage_complete": linkage_ok, "raw_sealed": seal_ok,
            "manifest_verified": manifest_ok,
            "all_controls_passed": estim["Q8_all_cores_pass_all_controls"],
            "across_core_confirmatory_label_allowed": eligible and estim["cores_interpretable"] == 12,
            "may_not_be_backfilled": True}


def main() -> None:  # pragma: no cover - requires a run that does not exist yet
    raise SystemExit("Generation 116 froze this grader and did not run it. "
                     "A run requires control-plane authorisation and sealed responses.")


if __name__ == "__main__":
    main()
