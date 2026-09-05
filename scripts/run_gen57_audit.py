#!/usr/bin/env python3
"""Gen57 Part E: both coverage diagnostics over the same 72 recorded runs.

No model, no GPU, no network. Diagnostics are computed first; the hidden
verifier is read only afterwards, for cross-tabs.
"""
from __future__ import annotations

import json, shutil, subprocess, sys, tempfile, time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import artifact_coverage as A     # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T        # noqa: E402
from memory_bakeoff.pi_state_control.harness_state import MUTATION_TOOLS  # noqa: E402

OUT = ROOT / "results" / "pi_artifact_coverage_gen57"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
GEN56 = ROOT / "results" / "pi_artifact_authority_gen56"
GENERATIONS = {
    49: ROOT / "results/pi_state_control_gen49",
    52: ROOT / "results/pi_quiescent_completion_gen52",
    55: ROOT / "results/pi_quiescent_completion_gen55",
}


def read_ndjson(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def fresh(repo: Path) -> Path:
    target = Path(tempfile.mkdtemp(prefix="gen57-run-"))
    shutil.rmtree(target)
    shutil.copytree(repo, target)
    shutil.rmtree(target / ".git", ignore_errors=True)
    return target


def resolve(worktree: Path, recorded: str) -> Path:
    parts = Path(recorded).parts
    for index, part in enumerate(parts):
        if part.startswith("run_"):
            return worktree.joinpath(*parts[index + 1:])
    return worktree / Path(recorded).name


def replay(run_dir: Path, worktree: Path) -> dict:
    """Same committed-mutation discipline as Gen56."""
    pending, failures, changed = deque(), [], set()
    for row in read_ndjson(run_dir / "tools.ndjson"):
        if row.get("phase") == "call":
            pending.append((row["tool"], row.get("args") or {}))
            continue
        tool, args = pending.popleft() if pending else ("", {})
        if tool not in MUTATION_TOOLS:
            continue
        recorded = args.get("path") or args.get("file_path")
        target = resolve(worktree, recorded) if recorded else None
        applied = False
        if target is not None:
            if tool in ("edit", "multi_edit") and target.exists():
                text = target.read_text()
                edits = args.get("edits") or []
                if edits and all(e.get("oldText") in text for e in edits if e.get("oldText")):
                    for edit in edits:
                        text = text.replace(edit["oldText"], edit["newText"], 1)
                    target.write_text(text)
                    applied = True
            elif tool == "write" and args.get("content") is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(args["content"])
                applied = True
        if applied:
            changed.add(str(target.relative_to(worktree)))
        else:
            failures.append({"tool": tool})
    return {"unreplayable": failures, "changed_paths": sorted(changed)}


def line_diagnostic(initial: Path, final: Path) -> dict:
    targets = [p for p in A.production_paths(final) if p.suffix == ".py"]
    changed, total = {}, 0
    unsupported = []
    for path in targets:
        relative = str(path.relative_to(final))
        info = A.changed_lines(initial, final, relative)
        if info["status"] == "deleted_only":
            unsupported.append({"path": relative, "why": "deleted_only"})
            continue
        lines = sorted(set(info["lines"]) & A.executable_lines(path))
        if lines:
            changed[relative] = lines
            total += len(lines)
    for path in A.production_paths(final):
        if path.suffix != ".py":
            unsupported.append({"path": str(path.relative_to(final)), "why": "non_python"})
    if total == 0:
        return {"category": "no_production_change", "changed_line_total": 0,
                "unsupported": unsupported}
    traced = A.run_traced_broad_check(final, targets)
    hit, missed = 0, []
    for relative, lines in changed.items():
        resolved = str((final / relative).resolve())
        for line in lines:
            if (resolved, line) in traced["hits"]:
                hit += 1
            else:
                missed.append(f"{relative}:{line}")
    return {"category": "measured", "changed_line_total": total, "changed_line_hit_count": hit,
            "hit_fraction": round(hit / total, 3),
            "all_changed_executable_lines_hit": hit == total,
            "missed_lines": missed[:20], "unsupported": unsupported,
            "traced_broad_passes": traced["passed"], "trace_seconds": traced["seconds"]}


def reversion_diagnostic(initial: Path, final: Path) -> dict:
    started = time.time()
    hunks = A.production_hunks(initial, final)
    digest_before = T.tracked_digest(final)
    killed = survived = unknown = 0
    details = []
    for hunk in hunks:
        probe = A.reverse_probe(final, hunk["patch"])
        if not probe["applied"]:
            unknown += 1
            details.append({"hunk": hunk["index"], "outcome": "unknown",
                            "reason": probe["apply_error"][:120], "paths": hunk["paths"]})
            shutil.rmtree(probe["work"], ignore_errors=True)
            continue
        done = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                               "-p", "no:cacheprovider"], cwd=probe["tree"],
                              capture_output=True, text=True, timeout=300)
        combined = done.stdout + done.stderr
        outcome = "killed_reversion" if done.returncode != 0 else "survived_reversion"
        killed += outcome == "killed_reversion"
        survived += outcome == "survived_reversion"
        details.append({"hunk": hunk["index"], "outcome": outcome, "paths": hunk["paths"],
                        "failure_kind": ("collection_or_syntax"
                                         if "error" in combined.lower() and done.returncode != 0
                                         else "assertion" if done.returncode != 0 else None)})
        shutil.rmtree(probe["work"], ignore_errors=True)
    return {"hunks_total": len(hunks), "applicable": len(hunks) - unknown,
            "killed": killed, "survived": survived, "unknown": unknown,
            "any_survived_reversion": survived > 0, "details": details,
            "final_digest_unchanged_after_probes": T.tracked_digest(final) == digest_before,
            "seconds": round(time.time() - started, 2)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    gen56 = {r["run"]: r for r in json.loads((GEN56 / "run_audit_72.json").read_text())["runs"]}

    runs = []
    for generation, base in GENERATIONS.items():
        for run_dir in sorted((base / "runs").iterdir()):
            leaf_path = run_dir / "leaf.json"
            if not leaf_path.exists():
                continue
            leaf = json.loads(leaf_path.read_text())
            task = leaf["slot"]["task"]
            repo = ROOT / manifest["tasks"][task]["repo_path"]
            initial, final = fresh(repo), fresh(repo)
            rebuilt = replay(run_dir, final)
            reconstructable = not rebuilt["unreplayable"]
            row = {
                "generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
                "task": task, "repetition": leaf["slot"]["repetition"],
                "reconstructable": reconstructable,
                "final_tracked_digest": T.tracked_digest(final) if reconstructable else None,
                "changed_production_paths": [p for p in rebuilt["changed_paths"]
                                             if not p.startswith("tests/")],
                "tests_changed_since_initial": any(p.startswith("tests/")
                                                   for p in rebuilt["changed_paths"]),
                "gen56_class": (gen56.get(run_dir.name) or {}).get("primary_class"),
                "gen56_receipt_scope": (gen56.get(run_dir.name) or {}).get("receipt_scope_class"),
            }
            if reconstructable:
                row["changed_line_execution"] = line_diagnostic(initial, final)
                row["change_reversion_sensitivity"] = reversion_diagnostic(initial, final)
            else:
                row["changed_line_execution"] = {"category": "reconstruction_unknown"}
                row["change_reversion_sensitivity"] = {"category": "reconstruction_unknown"}
            # post hoc only, after both diagnostics are fixed for this tree
            row["hidden_verifier_passed"] = leaf["verifier"]["passed"]
            runs.append(row)
            shutil.rmtree(initial, ignore_errors=True)
            shutil.rmtree(final, ignore_errors=True)

    def signal_line(row):
        block = row["changed_line_execution"]
        if block.get("category") != "measured":
            return None
        return not block["all_changed_executable_lines_hit"]

    def signal_reversion(row):
        block = row["change_reversion_sensitivity"]
        if block.get("category") == "reconstruction_unknown" or block.get("applicable", 0) == 0:
            return None
        return block["any_survived_reversion"]

    def crosstab(signal):
        table = {}
        for row in runs:
            flag = signal(row)
            if flag is None:
                table["not_applicable"] = table.get("not_applicable", 0) + 1
                continue
            key = ("flagged" if flag else "clean") + ("_hidden_wrong" if not row["hidden_verifier_passed"]
                                                      else "_hidden_correct")
            table[key] = table.get(key, 0) + 1
        return table

    gap_runs = [r for r in runs if r["gen56_class"] == "visible_artifact_coverage_gap"]
    correct_runs = [r for r in runs if r["hidden_verifier_passed"] and r["reconstructable"]]

    def screen(signal, name):
        gap_applicable = [r for r in gap_runs if signal(r) is not None]
        gap_flagged = [r for r in gap_applicable if signal(r)]
        correct_applicable = [r for r in correct_runs if signal(r) is not None]
        correct_flagged = [r for r in correct_applicable if signal(r)]
        gap_rate = len(gap_flagged) / len(gap_applicable) if gap_applicable else 0.0
        correct_rate = len(correct_flagged) / len(correct_applicable) if correct_applicable else 0.0
        return {"diagnostic": name,
                "coverage_gap_flagged": len(gap_flagged), "coverage_gap_applicable": len(gap_applicable),
                "coverage_gap_rate": round(gap_rate, 3),
                "hidden_correct_flagged": len(correct_flagged),
                "hidden_correct_applicable": len(correct_applicable),
                "hidden_correct_rate": round(correct_rate, 3),
                "meets_frozen_screen": gap_rate >= 0.5 and correct_rate <= 0.25,
                "flagged_gap_runs": [r["run"] for r in gap_flagged]}

    result = {
        "evidence_class": "architecture_visible_artifact_coverage_diagnostics_offline_no_score",
        "contract": A.contract(),
        "runs": runs,
        "crosstabs": {"changed_line_execution": crosstab(signal_line),
                      "change_reversion_sensitivity": crosstab(signal_reversion)},
        "screening": {"changed_line_execution": screen(signal_line, "changed-line-execution-v1"),
                      "change_reversion_sensitivity": screen(signal_reversion,
                                                             "change-reversion-sensitivity-v1")},
        "cost": {
            "total_trace_seconds": round(sum(r["changed_line_execution"].get("trace_seconds", 0)
                                             for r in runs), 2),
            "total_reversion_seconds": round(sum(r["change_reversion_sensitivity"].get("seconds", 0)
                                                 for r in runs), 2),
            "total_reversion_probes": sum(r["change_reversion_sensitivity"].get("hunks_total", 0)
                                          for r in runs),
        },
        "reconstruction": {"reconstructable": sum(1 for r in runs if r["reconstructable"]),
                           "of_runs": len(runs),
                           "unknown": [r["run"] for r in runs if not r["reconstructable"]]},
    }
    (OUT / "run_audit_72.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("crosstabs", "screening", "cost", "reconstruction")},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
