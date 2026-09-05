#!/usr/bin/env python3
"""Gen56 Parts D/E: the six frozen sentinels, and the breadth counterfactual."""
from __future__ import annotations

import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import tracked_digest as T   # noqa: E402

OUT = ROOT / "results" / "pi_artifact_authority_gen56"
GEN48 = ROOT / "results" / "pi_state_control_gen48"

SENTINELS = {
    "gen49-IP1-r1-C": {"generation": 49, "match": "IP1-r1-pi_harness_state_control_v1",
                       "why": "known visible-receipt false assurance; narrow validation was part of the observed mechanism"},
    "gen49-IP1-r1-D": {"generation": 49, "match": "IP1-r1-pi_harness_state_control_task_floor_v1",
                       "why": "paired successful comparator that ran the whole tests directory"},
    "gen49-IP1-r3-D": {"generation": 49, "match": "IP1-r3-pi_harness_state_control_task_floor_v1",
                       "why": "known false assurance with the human-direction floor active"},
    "gen55-IP1-r1-F": {"generation": 55, "match": "IP1-r1-pi_harness_state_control_quiescent_tracked_k3_v1",
                       "why": "live stop on a hidden-verifier-wrong tree; C partner passed"},
    "gen55-IP1-r2-F": {"generation": 55, "match": "IP1-r2-pi_harness_state_control_quiescent_tracked_k3_v1",
                       "why": "live stop on a hidden-verifier-wrong tree; C partner also failed after timeout"},
}


def ip4_fixture_diagnostic() -> dict:
    """Does IP4's broadest shipped visible check itself miss a known partial fix?"""
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    repo = ROOT / manifest["tasks"]["IP4"]["repo_path"]
    probe = manifest["tasks"]["IP4"].get("incomplete_visible_check_probe")
    tree = Path(tempfile.mkdtemp(prefix="gen56-ip4-"))
    shutil.rmtree(tree)
    shutil.copytree(repo, tree)
    broad = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=tree,
                           capture_output=True, text=True, timeout=300)
    verifier = subprocess.run([sys.executable, "-B", str(ROOT / manifest["tasks"]["IP4"]["verifier_path"])],
                              cwd=tree, capture_output=True, text=True, timeout=180)
    shutil.rmtree(tree, ignore_errors=True)
    return {
        "sentinel": "gen48-IP4-partial-fix-fixture-diagnostic",
        "why": "fixture-level evidence that the broadest shipped visible check can itself be incomplete",
        "recorded_probe_in_manifest": probe,
        "broadest_visible_on_shipped_fixture_passes": broad.returncode == 0,
        "hidden_verifier_on_shipped_fixture_passes": verifier.returncode == 0,
        "note": ("the shipped fixture is the unfixed starting state, so both failing here is "
                 "expected; the diagnostic that matters is whether any tree exists on which the "
                 "broad visible check passes and the hidden verifier fails, which the 72-run "
                 "audit answers directly"),
    }


def main() -> int:
    audit = json.loads((OUT / "run_audit_72.json").read_text())
    by_run = {r["run"]: r for r in audit["runs"]}

    sentinels = []
    for name, spec in SENTINELS.items():
        row = next((r for r in audit["runs"]
                    if r["generation"] == spec["generation"] and r["run"].endswith(spec["match"])), None)
        if row is None:
            sentinels.append({"sentinel": name, "why": spec["why"], "found": False})
            continue
        receipt = row["last_valid_visible_receipt"]
        sentinels.append({
            "sentinel": name, "why": spec["why"], "found": True, "run": row["run"],
            "hidden_verifier_passed": row["hidden_verifier_passed"],
            "receipt_scope_class": row["receipt_scope_class"],
            "receipt_command": receipt["validation_command"] if receipt else None,
            "broadest_visible_ran_live": row["broadest_visible_ran_live"],
            "broad_visible_offline_passes": row["broad_visible_offline"]["passed"],
            "broad_visible_tail": row["broad_visible_offline"]["tail"],
            "primary_class": row["primary_class"],
            # the question the brief asks of each live sentinel
            "would_a_broader_shipped_visible_check_have_contradicted_the_receipt":
                (row["last_valid_visible_receipt"] is not None
                 and not row["broad_visible_offline"]["passed"]),
            "fully_reconstructable": row["fully_reconstructable"],
        })
    sentinels.append(ip4_fixture_diagnostic())

    # Part E: the counterfactual screen, deterministic categories only.
    categories, per_run = {}, []
    for row in audit["runs"]:
        receipt = row["last_valid_visible_receipt"]
        broad_passes = row["broad_visible_offline"]["passed"]
        hidden = row["hidden_verifier_passed"]
        if not row["fully_reconstructable"]:
            category = "unknown"
        elif row["broadest_visible_ran_live"] and receipt:
            category = "already_satisfied_live"
        elif receipt and not broad_passes and not hidden:
            category = "would_block_false_assurance"
        elif receipt and broad_passes and not hidden:
            category = "would_not_help_artifact_gap"
        elif broad_passes and hidden:
            category = "would_add_validation_only"
        else:
            category = "unknown"
        categories[category] = categories.get(category, 0) + 1
        per_run.append({"run": row["run"], "category": category,
                        "broad_seconds": row["broad_visible_offline"]["seconds"]})

    counterfactual = {
        "hypothetical": "require_broad_visible_before_strong_completion",
        "implemented_live": False,
        "categories": categories,
        "per_run": per_run,
        "deterministic_cost_only": {
            "extra_broad_check_runs": sum(1 for r in audit["runs"] if not r["broadest_visible_ran_live"]),
            "total_extra_seconds": round(sum(
                r["broad_visible_offline"]["seconds"] for r in audit["runs"]
                if not r["broadest_visible_ran_live"]), 2),
            "extra_tool_calls_per_affected_run": 1,
            "note": "measured offline runtime of the broad check only; no model behaviour is estimated",
        },
    }
    (OUT / "sentinels.json").write_text(json.dumps(sentinels, indent=2, sort_keys=True) + "\n")
    (OUT / "breadth_counterfactual.json").write_text(
        json.dumps(counterfactual, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sentinels": [{k: s.get(k) for k in
                                     ("sentinel", "hidden_verifier_passed", "receipt_scope_class",
                                      "broad_visible_offline_passes", "primary_class",
                                      "would_a_broader_shipped_visible_check_have_contradicted_the_receipt")}
                                    for s in sentinels],
                      "counterfactual": categories,
                      "cost": counterfactual["deterministic_cost_only"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
