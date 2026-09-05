#!/usr/bin/env python3
"""Gen58 Parts D and E: check the banks against a trusted implementation, then
run them over the historical trees. No generation happens here, and no test is
altered — the banks are already frozen and hashed.
"""
from __future__ import annotations

import ast, json, shutil, subprocess, sys, tempfile
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff.pi_state_control import tracked_digest as T           # noqa: E402
from memory_bakeoff.pi_state_control.harness_state import MUTATION_TOOLS  # noqa: E402

OUT = ROOT / "results" / "pi_model_assisted_evidence_gen58"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
GENERATIONS = {
    49: ROOT / "results/pi_state_control_gen49",
    52: ROOT / "results/pi_quiescent_completion_gen52",
    55: ROOT / "results/pi_quiescent_completion_gen55",
}
BANK_FILE = "test_generated_challenge.py"


def reference_fixes() -> dict[str, dict]:
    """The trusted positive implementations, from the committed Gen48 builder.

    Evaluator-only. These predate this generation, were never written into any
    fixture or prompt, and are never shown to the generator.
    """
    source = (ROOT / "scripts/build_intent_persistence_gen48_tasks.py").read_text()
    tree = ast.parse(source)
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else ""
        if name.endswith("_FIX") or name.endswith("_PARTIAL"):
            try:
                found[name] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return found


def fresh(repo: Path) -> Path:
    target = Path(tempfile.mkdtemp(prefix="gen58-"))
    shutil.rmtree(target)
    shutil.copytree(repo, target)
    shutil.rmtree(target / ".git", ignore_errors=True)
    return target


def apply_files(tree: Path, files: dict) -> None:
    for relative, text in files.items():
        target = tree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def run_bank(tree: Path, bank: str) -> dict:
    """Run only the generated bank, in a copy, leaving the tree untouched."""
    work = fresh(tree)
    (work / "tests" / BANK_FILE).write_text(bank)
    done = subprocess.run([sys.executable, "-m", "pytest", f"tests/{BANK_FILE}", "-q",
                           "-p", "no:cacheprovider"], cwd=work,
                          capture_output=True, text=True, timeout=300)
    combined = done.stdout + done.stderr
    failing = sorted(set(__import__("re").findall(r"(test_\w+)\s+(?:FAILED|ERROR)", combined))
                     | set(__import__("re").findall(r"::(test_\w+)\s+FAILED", combined)))
    tail = combined.strip().splitlines()[-1:] or [""]
    shutil.rmtree(work, ignore_errors=True)
    return {"exit": done.returncode, "passed": done.returncode == 0,
            "failing_tests": failing[:20], "tail": tail[0][:200]}


def resolve(worktree: Path, recorded: str) -> Path:
    parts = Path(recorded).parts
    for index, part in enumerate(parts):
        if part.startswith("run_"):
            return worktree.joinpath(*parts[index + 1:])
    return worktree / Path(recorded).name


def replay(run_dir: Path, worktree: Path) -> bool:
    pending, ok = deque(), True
    for row in [json.loads(l) for l in (run_dir / "tools.ndjson").read_text().splitlines() if l.strip()]:
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
        ok = ok and applied
    return ok


def main() -> int:
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    log = json.loads((OUT / "generation_log.json").read_text())
    fixes = reference_fixes()

    # Part C: assemble each task's bank from its accepted outputs, unfiltered.
    banks = {}
    for task in ("IP1", "IP2", "IP3", "IP4"):
        pieces, provenance = [], []
        for output in sorted(log["outputs"], key=lambda o: (o["task"], o["repetition"])):
            if output["task"] != task or not output["accepted"]:
                continue
            code = (OUT / "generated" / f"{output['run_id']}.py").read_text()
            # namespace each repetition so identically-named tests all run
            renamed = code.replace("def test_", f"def test_r{output['repetition']}_")
            pieces.append(f"# --- {output['run_id']} ---\n{renamed}")
            provenance.append({"run_id": output["run_id"], "code_sha256": output["code_sha256"],
                               "test_functions": output["test_functions"]})
        bank = "\n\n".join(pieces)
        banks[task] = {"bank": bank, "provenance": provenance,
                       "sha256": __import__("hashlib").sha256(bank.encode()).hexdigest(),
                       "accepted_outputs": len(provenance)}

    # Part D: does the bank pass a trusted implementation that predates it?
    reference = {}
    for task in banks:
        key = f"{task}_FIX"
        if key not in fixes or not banks[task]["bank"]:
            reference[task] = {"status": "UNMEASURED",
                               "why": ("no authoritative positive reference from fixture construction"
                                       if key not in fixes else "no accepted generator output")}
            continue
        repo = ROOT / manifest["tasks"][task]["repo_path"]
        tree = fresh(repo)
        apply_files(tree, fixes[key])
        result = run_bank(tree, banks[task]["bank"])
        shutil.rmtree(tree, ignore_errors=True)
        reference[task] = {"status": "measured", "bank_passes_reference": result["passed"],
                           "failing_tests": result["failing_tests"], "tail": result["tail"],
                           "unsafe_as_gate": not result["passed"]}

    # Part E: the historical population, bank executed only after freezing.
    runs = []
    for generation, base in GENERATIONS.items():
        for run_dir in sorted((base / "runs").iterdir()):
            leaf_path = run_dir / "leaf.json"
            if not leaf_path.exists():
                continue
            leaf = json.loads(leaf_path.read_text())
            task = leaf["slot"]["task"]
            repo = ROOT / manifest["tasks"][task]["repo_path"]
            tree = fresh(repo)
            reconstructable = replay(run_dir, tree)
            row = {"generation": generation, "run": run_dir.name, "arm": leaf["slot"]["arm"],
                   "task": task, "repetition": leaf["slot"]["repetition"],
                   "reconstructable": reconstructable,
                   "final_tracked_digest": T.tracked_digest(tree) if reconstructable else None}
            if reconstructable and banks[task]["bank"]:
                result = run_bank(tree, banks[task]["bank"])
                row["challenge_bank_fails_on_candidate"] = not result["passed"]
                row["failing_generated_tests"] = result["failing_tests"]
            else:
                row["challenge_bank_fails_on_candidate"] = None
            shutil.rmtree(tree, ignore_errors=True)
            row["hidden_verifier_passed"] = leaf["verifier"]["passed"]   # post hoc only
            runs.append(row)

    valid_tasks = {t for t, r in reference.items()
                   if r.get("status") == "measured" and r.get("bank_passes_reference")}
    population = [r for r in runs if r["reconstructable"]
                  and r["challenge_bank_fails_on_candidate"] is not None
                  and r["task"] in valid_tasks]
    wrong = [r for r in population if not r["hidden_verifier_passed"]]
    correct = [r for r in population if r["hidden_verifier_passed"]]
    flagged_wrong = [r for r in wrong if r["challenge_bank_fails_on_candidate"]]
    flagged_correct = [r for r in correct if r["challenge_bank_fails_on_candidate"]]

    crosstab = {
        "bank_fail_hidden_wrong": len(flagged_wrong),
        "bank_pass_hidden_wrong": len(wrong) - len(flagged_wrong),
        "bank_fail_hidden_correct": len(flagged_correct),
        "bank_pass_hidden_correct": len(correct) - len(flagged_correct),
        "reference_valid_tasks": sorted(valid_tasks),
        "excluded_unmeasured_or_unsafe": sorted(set(banks) - valid_tasks),
        "runs_not_reconstructable": sum(1 for r in runs if not r["reconstructable"]),
    }
    screen = {
        "hidden_wrong_flagged_rate": round(len(flagged_wrong) / len(wrong), 3) if wrong else None,
        "hidden_correct_flagged_rate": round(len(flagged_correct) / len(correct), 3) if correct else None,
        "meets_frozen_screen": bool(wrong) and bool(correct)
                               and len(flagged_wrong) / len(wrong) >= 0.5
                               and len(flagged_correct) / len(correct) <= 0.25,
    }
    sentinels = {name: next(({"run": r["run"], "hidden": r["hidden_verifier_passed"],
                              "bank_fails": r["challenge_bank_fails_on_candidate"],
                              "failing": r["failing_generated_tests"][:5]}
                             for r in runs if r["run"].endswith(suffix)
                             and r["generation"] == gen), None)
                 for name, (suffix, gen) in {
                     "gen49-IP1-r1-C": ("IP1-r1-pi_harness_state_control_v1", 49),
                     "gen49-IP1-r3-D": ("IP1-r3-pi_harness_state_control_task_floor_v1", 49),
                     "gen55-IP1-r1-F": ("IP1-r1-pi_harness_state_control_quiescent_tracked_k3_v1", 55),
                     "gen55-IP1-r2-F": ("IP1-r2-pi_harness_state_control_quiescent_tracked_k3_v1", 55),
                     "gen49-IP1-r1-D": ("IP1-r1-pi_harness_state_control_task_floor_v1", 49),
                 }.items()}

    # IP4 partial-fix sentinel, using the recorded partial from fixture construction
    if "IP4_PARTIAL" in fixes and banks["IP4"]["bank"]:
        tree = fresh(ROOT / manifest["tasks"]["IP4"]["repo_path"])
        apply_files(tree, fixes["IP4_PARTIAL"])
        result = run_bank(tree, banks["IP4"]["bank"])
        shutil.rmtree(tree, ignore_errors=True)
        sentinels["gen48-IP4-partial-fix"] = {"bank_fails": not result["passed"],
                                              "failing": result["failing_tests"][:5],
                                              "note": "evaluated with the partial fix recorded in the Gen48 builder"}

    result = {
        "evidence_class": "architecture_model_assisted_challenge_generation_component_pilot",
        "banks": {t: {k: v for k, v in b.items() if k != "bank"} for t, b in banks.items()},
        "reference_validity": reference,
        "crosstab": crosstab, "screen": screen, "sentinels": sentinels, "runs": runs,
    }
    for task, bank in banks.items():
        if bank["bank"]:
            (OUT / "generated" / f"bank_{task}.py").write_text(bank["bank"])
    (OUT / "evaluation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"reference_validity": reference, "crosstab": crosstab, "screen": screen,
                      "sentinels": sentinels}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
