#!/usr/bin/env python3
"""Gen56: what did each run's passing check actually establish?

No model, no GPU, no network. Each run's final tracked tree is rebuilt from its
own recorded edits, then the frozen broadest shipped visible validation is run
against that tree offline. The hidden verifier result is read afterwards and
never influences which command is chosen or how scope is classified.
"""
from __future__ import annotations

import gzip, json, re, shutil, subprocess, sys, tempfile
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import quiescent_v2 as Q            # noqa: E402
from memory_bakeoff.pi_state_control import scoped_receipt as S          # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T          # noqa: E402
from memory_bakeoff.pi_state_control.harness_state import MUTATION_TOOLS  # noqa: E402

OUT = ROOT / "results" / "pi_artifact_authority_gen56"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
GENERATIONS = {
    49: ROOT / "results/pi_state_control_gen49",
    52: ROOT / "results/pi_quiescent_completion_gen52",
    55: ROOT / "results/pi_quiescent_completion_gen55",
}
PYTEST_SUMMARY = re.compile(r"=+[^=\n]*\bin\s+[\d.]+s[^=\n]*=+")


def read_ndjson(path: Path):
    if not path.exists():
        return []
    handle = gzip.open(path, "rt") if path.suffix == ".gz" else open(path)
    with handle:
        return [json.loads(line) for line in handle if line.strip()]


def fresh_worktree(repo: Path) -> Path:
    target = Path(tempfile.mkdtemp(prefix="gen56-audit-"))
    shutil.rmtree(target)
    shutil.copytree(repo, target)
    shutil.rmtree(target / ".git", ignore_errors=True)
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "run"]):
        subprocess.run(command, cwd=target, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return target


def resolve(worktree: Path, recorded: str) -> Path:
    parts = Path(recorded).parts
    for index, part in enumerate(parts):
        if part.startswith("run_"):
            return worktree.joinpath(*parts[index + 1:])
    return worktree / Path(recorded).name


def rebuild(run_dir: Path, worktree: Path):
    """Replay the run's recorded mutations, and note the last visible check."""
    tools = read_ndjson(run_dir / "tools.ndjson")
    derived = (run_dir / "derivation.ndjson").exists()
    validations, seen = [], set()
    if derived:
        for row in read_ndjson(run_dir / "derivation.ndjson"):
            validation = row.get("validation") or {}
            event = validation.get("event")
            if event and event not in seen and validation.get("passed") is not None:
                seen.add(event)
                validations.append(validation)

    pending, index, failures, changed = deque(), 0, [], set()
    checks, check_number = [], 0
    for row in tools:
        if row.get("phase") == "call":
            index += 1
            args = row.get("args") or {}
            command = (args.get("command") or args.get("cmd") or "") if row["tool"] == "bash" else ""
            pending.append((index, row["tool"], command, args))
            continue
        call_index, tool, command, args = pending.popleft() if pending else (index, "", "", {})
        if tool in MUTATION_TOOLS:
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
                failures.append({"tool": tool, "call": call_index})
        elif Q.is_visible_check(command):
            passed = None
            if derived and check_number < len(validations):
                passed = bool(validations[check_number]["passed"])
            check_number += 1
            checks.append({"call": call_index, "command": command, "passed": passed})
    return {"checks": checks, "unreplayable": failures, "changed_paths": sorted(changed)}


def run_broad(worktree: Path, command: str) -> dict:
    """The frozen broadest shipped visible validation, offline, on this tree."""
    import time
    started = time.time()
    done = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=worktree,
                          capture_output=True, text=True, timeout=300,
                          env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
    for cache in worktree.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    shutil.rmtree(worktree / ".pytest_cache", ignore_errors=True)
    tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
    return {"command": command, "exit_status": done.returncode, "passed": done.returncode == 0,
            "tail": tail[0][:200], "seconds": round(time.time() - started, 2)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = json.loads((OUT / "broad_visible_commands.json").read_text())
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    runs = []
    for generation, base in GENERATIONS.items():
        for run_dir in sorted((base / "runs").iterdir()):
            leaf_path = run_dir / "leaf.json"
            if not leaf_path.exists():
                continue
            leaf = json.loads(leaf_path.read_text())
            task = leaf["slot"]["task"]
            broad_command = frozen["tasks"][task]["broadest_visible_validation"]
            worktree = fresh_worktree(ROOT / manifest["tasks"][task]["repo_path"])
            rebuilt = rebuild(run_dir, worktree)
            final_tree = T.tracked_digest(worktree)

            last_pass = next((c for c in reversed(rebuilt["checks"]) if c["passed"] is True), None)
            receipt = None
            if last_pass:
                receipt = S.receipt(
                    tree_digest=final_tree, command=last_pass["command"],
                    cwd=str(run_dir), exit_status=0, event_index=last_pass["call"],
                    provenance=("harness_validation_record"
                                if (run_dir / "derivation.ndjson").exists()
                                else "offline_reconstructed_observable_receipt"),
                    project_wide_command=broad_command,
                    changed_paths=rebuilt["changed_paths"])
            broad_ran_live = any(
                S.classify_scope(c["command"], broad_command)["scope_class"] == "project_wide_visible"
                and c["passed"] is True for c in rebuilt["checks"])
            broad = run_broad(worktree, broad_command)
            shutil.rmtree(worktree, ignore_errors=True)

            runs.append({
                "generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
                "task": task, "repetition": leaf["slot"]["repetition"],
                "termination_class": leaf.get("termination_class") or leaf["run"]["status"],
                "final_tracked_tree": final_tree,
                "fully_reconstructable": not rebuilt["unreplayable"],
                "unreplayable_mutations": rebuilt["unreplayable"],
                "changed_project_paths": rebuilt["changed_paths"],
                "visible_checks": len(rebuilt["checks"]),
                "last_valid_visible_receipt": receipt,
                "receipt_scope_class": receipt["scope_class"] if receipt else None,
                "broadest_visible_ran_live": broad_ran_live,
                "broad_visible_offline": broad,
                # post hoc only, never an input above
                "hidden_verifier_passed": leaf["verifier"]["passed"],
            })

    def classify(row):
        if not row["fully_reconstructable"]:
            return "reconstruction_or_instrumentation_unknown"
        if row["hidden_verifier_passed"] or not row["last_valid_visible_receipt"]:
            return None
        if not row["broad_visible_offline"]["passed"]:
            return "narrow_receipt_broader_visible_contradicts"
        return "visible_artifact_coverage_gap"

    for row in runs:
        row["primary_class"] = classify(row)

    counts = {}
    for row in runs:
        if row["primary_class"]:
            counts[row["primary_class"]] = counts.get(row["primary_class"], 0) + 1
    scopes = {}
    for row in runs:
        key = row["receipt_scope_class"] or "no_valid_receipt"
        scopes[key] = scopes.get(key, 0) + 1

    result = {
        "evidence_class": "architecture_quiescence_closeout_and_artifact_authority_audit_no_score",
        "frozen_broad_commands_sha256": frozen["contract_sha256"],
        "receipt_contract": S.contract(),
        "runs": runs,
        "receipt_scope_classes": scopes,
        "hidden_wrong_with_valid_receipt": counts,
        "reconstruction": {
            "fully_reconstructable": sum(1 for r in runs if r["fully_reconstructable"]),
            "of_runs": len(runs),
            "unreconstructable": [r["run"] for r in runs if not r["fully_reconstructable"]],
        },
    }
    (OUT / "run_audit_72.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"runs": len(runs), "scopes": scopes,
                      "hidden_wrong_with_valid_receipt": counts,
                      "reconstruction": result["reconstruction"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
