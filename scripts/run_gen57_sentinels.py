#!/usr/bin/env python3
"""Gen57: the six frozen sentinels under both coverage diagnostics."""
from __future__ import annotations

import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import artifact_coverage as A   # noqa: E402

OUT = ROOT / "results" / "pi_artifact_coverage_gen57"
GEN48 = ROOT / "results" / "pi_state_control_gen48"

LIVE = {
    "gen49-IP1-r1-C": ("IP1-r1-pi_harness_state_control_v1", 49,
                       "hidden wrong, false assurance, explicit-subset receipt"),
    "gen49-IP1-r3-D": ("IP1-r3-pi_harness_state_control_task_floor_v1", 49,
                       "hidden wrong, project-wide receipt"),
    "gen55-IP1-r1-F": ("IP1-r1-pi_harness_state_control_quiescent_tracked_k3_v1", 55,
                       "hidden wrong, project-wide receipt, live quiescent stop"),
    "gen55-IP1-r2-F": ("IP1-r2-pi_harness_state_control_quiescent_tracked_k3_v1", 55,
                       "hidden wrong, explicit-subset receipt, live quiescent stop"),
    "gen49-IP1-r1-D": ("IP1-r1-pi_harness_state_control_task_floor_v1", 49,
                       "hidden-correct successful comparator"),
}


def ip4_partial_fix() -> dict:
    """The fixture where the shipped visible test passes a known partial fix."""
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    repo = ROOT / manifest["tasks"]["IP4"]["repo_path"]
    probe = manifest["tasks"]["IP4"].get("incomplete_visible_check_probe") or {}
    reference = manifest["tasks"]["IP4"].get("reference_fix_path")

    initial = Path(tempfile.mkdtemp(prefix="gen57-ip4-i-")); shutil.rmtree(initial)
    shutil.copytree(repo, initial)
    final = Path(tempfile.mkdtemp(prefix="gen57-ip4-f-")); shutil.rmtree(final)
    shutil.copytree(repo, final)

    # Recreate the partial fix the manifest already documents, from its own
    # recorded probe rather than from the hidden verifier's contents.
    partial = probe.get("partial_implementation_patch")
    applied = False
    if partial:
        for relative, text in partial.items():
            (final / relative).write_text(text)
        applied = True

    result = {
        "sentinel": "gen48-IP4-partial-fix-fixture-diagnostic",
        "why": "fixture-level evidence that the broadest shipped visible test can pass a partial fix",
        "recorded_probe": probe,
        "partial_implementation_reconstructed": applied,
    }
    if applied:
        targets = [p for p in A.production_paths(final) if p.suffix == ".py"]
        traced = A.run_traced_broad_check(final, targets)
        result["broad_visible_passes_on_partial_fix"] = traced["passed"]
        hunks = A.production_hunks(initial, final)
        survived = 0
        for hunk in hunks:
            probe_run = A.reverse_probe(final, hunk["patch"])
            if not probe_run["applied"]:
                shutil.rmtree(probe_run["work"], ignore_errors=True)
                continue
            done = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                                   "-p", "no:cacheprovider"], cwd=probe_run["tree"],
                                  capture_output=True, text=True, timeout=300)
            survived += done.returncode == 0
            shutil.rmtree(probe_run["work"], ignore_errors=True)
        result["reversion_probes"] = len(hunks)
        result["survived_reversions"] = survived
    else:
        result["note"] = ("the manifest records the probe's outcome but not a reconstructable "
                          "partial-fix patch, so the fixture-level diagnostic is reported from "
                          "the recorded probe rather than recomputed")
    shutil.rmtree(initial, ignore_errors=True)
    shutil.rmtree(final, ignore_errors=True)
    return result


def main() -> int:
    audit = json.loads((OUT / "run_audit_72.json").read_text())
    by_run = {r["run"]: r for r in audit["runs"]}
    sentinels = []
    for name, (suffix, generation, why) in LIVE.items():
        row = next((r for r in audit["runs"]
                    if r["generation"] == generation and r["run"].endswith(suffix)), None)
        if row is None:
            sentinels.append({"sentinel": name, "why": why, "found": False})
            continue
        line = row["changed_line_execution"]
        rev = row["change_reversion_sensitivity"]
        sentinels.append({
            "sentinel": name, "why": why, "found": True, "run": row["run"],
            "hidden_verifier_passed": row["hidden_verifier_passed"],
            "gen56_class": row["gen56_class"],
            "reconstructable": row["reconstructable"],
            "changed_production_paths": row["changed_production_paths"],
            "tests_changed_since_initial": row["tests_changed_since_initial"],
            "line_category": line.get("category"),
            "all_changed_lines_hit": line.get("all_changed_executable_lines_hit"),
            "hit_fraction": line.get("hit_fraction"),
            "reversion_hunks": rev.get("hunks_total"),
            "reversion_killed": rev.get("killed"),
            "reversion_survived": rev.get("survived"),
            "any_survived_reversion": rev.get("any_survived_reversion"),
        })
    sentinels.append(ip4_partial_fix())
    (OUT / "sentinels.json").write_text(json.dumps(sentinels, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{k: s.get(k) for k in
                       ("sentinel", "hidden_verifier_passed", "all_changed_lines_hit",
                        "hit_fraction", "any_survived_reversion", "reversion_killed",
                        "reversion_survived", "tests_changed_since_initial",
                        "broad_visible_passes_on_partial_fix", "partial_implementation_reconstructed")}
                      for s in sentinels], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
