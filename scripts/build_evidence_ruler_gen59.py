#!/usr/bin/env python3
"""Gen59: write the ruler to disk, then measure whether it really contains the problem.

Every `passes_visible` label in the task definitions is a prediction. This script
treats them as such: it materialises every candidate, runs the shipped visible
tests and the hidden evaluator against each, and reports what actually happened.
A task only enters the primary ruler if the measurements agree with the design.
"""
from __future__ import annotations

import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler.tasks_gen59 import TASKS      # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T   # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
OUT = ROOT / "results" / "pi_evidence_ruler_gen59"
# What a future generator is allowed to read, and what it must never reach.
GENERATOR_VISIBLE = ("spec.txt", "repo")
EVALUATOR_ONLY = ("truth",)


def write_tree(target: Path, files: dict[str, str]) -> None:
    for relative, text in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def materialise(task: str, overlay: dict[str, str]) -> Path:
    tree = Path(tempfile.mkdtemp(prefix=f"gen59-{task}-"))
    shutil.rmtree(tree)
    shutil.copytree(FIXTURES / task / "repo", tree)
    write_tree(tree, overlay)
    # `tracked_digest` builds its tree from HEAD, so an un-initialised directory
    # digests as the empty string and every candidate looks identical.
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                     "commit", "-qm", "candidate"]):
        subprocess.run(command, cwd=tree, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tree


def run_visible(tree: Path) -> dict:
    done = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"],
                          cwd=tree, capture_output=True, text=True, timeout=180,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
    return {"passed": done.returncode == 0, "tail": tail[0][:160]}


def run_hidden(task: str, tree: Path) -> dict:
    verifier = FIXTURES / task / "truth" / "verifier.py"
    # Running a script puts the script's own directory on sys.path, not the tree,
    # so the candidate package would not import and every positive would "fail".
    done = subprocess.run([sys.executable, "-B", str(verifier)], cwd=tree,
                          capture_output=True, text=True, timeout=180,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                               "PYTHONPATH": str(tree)})
    tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
    return {"passed": done.returncode == 0, "tail": tail[0][:160]}


def main() -> int:
    if FIXTURES.exists():
        shutil.rmtree(FIXTURES)
    OUT.mkdir(parents=True, exist_ok=True)

    manifest, matrix, diversity = {}, {}, {}
    for name, spec in TASKS.items():
        task_dir = FIXTURES / name
        (task_dir).mkdir(parents=True)
        (task_dir / "spec.txt").write_text(spec["spec"].strip() + "\n")
        write_tree(task_dir / "repo", spec["repo"])
        truth = task_dir / "truth"
        truth.mkdir()
        (truth / "verifier.py").write_text(spec["verifier"])
        (truth / "candidates.json").write_text(json.dumps(
            {"positives": spec["positives"], "wrongs": spec["wrongs"],
             "requirements": spec["requirements"]}, indent=2, sort_keys=True) + "\n")

        rows, digests = [], {}
        for label, overlay in spec["positives"].items():
            tree = materialise(name, overlay)
            digests[f"positive:{label}"] = T.tracked_digest(tree)
            rows.append({"candidate": label, "kind": "positive",
                         "visible": run_visible(tree), "hidden": run_hidden(name, tree),
                         "tracked_digest": digests[f"positive:{label}"]})
            shutil.rmtree(tree, ignore_errors=True)
        for label, wrong in spec["wrongs"].items():
            tree = materialise(name, wrong["overlay"])
            digests[f"wrong:{label}"] = T.tracked_digest(tree)
            rows.append({"candidate": label, "kind": "wrong",
                         "failed_requirement": wrong["failed_requirement"],
                         "why": wrong["why"],
                         "self_modified_visible_test": wrong.get("self_modified_visible_test", False),
                         "predicted_passes_visible": wrong["passes_visible"],
                         "visible": run_visible(tree), "hidden": run_hidden(name, tree),
                         "tracked_digest": digests[f"wrong:{label}"]})
            shutil.rmtree(tree, ignore_errors=True)

        positives = [r for r in rows if r["kind"] == "positive"]
        wrongs = [r for r in rows if r["kind"] == "wrong"]
        visible_pass_wrongs = [r for r in wrongs if r["visible"]["passed"]]
        checks = {
            "at_least_two_positives": len(positives) >= 2,
            "all_positives_pass_visible": all(r["visible"]["passed"] for r in positives),
            "all_positives_pass_hidden": all(r["hidden"]["passed"] for r in positives),
            "positives_are_structurally_distinct":
                len({r["tracked_digest"] for r in positives}) == len(positives),
            "at_least_three_wrongs": len(wrongs) >= 3,
            "all_wrongs_fail_hidden": all(not r["hidden"]["passed"] for r in wrongs),
            "at_least_two_wrongs_pass_visible": len(visible_pass_wrongs) >= 2,
        }
        mispredicted = [r["candidate"] for r in wrongs
                        if r["predicted_passes_visible"] != r["visible"]["passed"]]
        admitted = all(checks.values())
        matrix[name] = {"rows": rows, "checks": checks, "admitted": admitted,
                        "wrongs_passing_visible": len(visible_pass_wrongs),
                        "mispredicted_visible_labels": mispredicted}
        manifest[name] = {
            "title": spec["title"], "mechanism": spec["mechanism"],
            "requirements": spec["requirements"],
            "spec_sha256": hashlib.sha256(spec["spec"].encode()).hexdigest(),
            "repo_tracked_digest": T.tracked_digest(FIXTURES / name / "repo")
                if (FIXTURES / name / "repo" / ".git").exists() else None,
            "candidate_digests": digests,
            "generator_visible_paths": list(GENERATOR_VISIBLE),
            "evaluator_only_paths": list(EVALUATOR_ONLY),
            "admitted": admitted,
        }
        diversity[name] = {
            "positive_digests": [r["tracked_digest"] for r in positives],
            "distinct": len({r["tracked_digest"] for r in positives}),
            "self_modified_test_candidate":
                any(r.get("self_modified_visible_test") for r in wrongs),
        }
        print(f"{name}: admitted={admitted} wrongs_passing_visible={len(visible_pass_wrongs)} "
              f"{'' if admitted else [k for k, v in checks.items() if not v]}")

    admitted = [n for n, m in matrix.items() if m["admitted"]]
    summary = {
        "ruler": "evidence-generation-gen59-v1",
        "authored": len(TASKS), "admitted": len(admitted), "admitted_tasks": sorted(admitted),
        "rejected_tasks": sorted(set(TASKS) - set(admitted)),
        "total_known_wrong_candidates": sum(
            len([r for r in matrix[n]["rows"] if r["kind"] == "wrong"]) for n in admitted),
        "total_visible_pass_hidden_fail": sum(
            matrix[n]["wrongs_passing_visible"] for n in admitted),
        "mechanisms": sorted({TASKS[n]["mechanism"] for n in admitted}),
    }
    (OUT / "task_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (OUT / "candidate_matrix.json").write_text(
        json.dumps({"summary": summary, "tasks": matrix}, indent=2, sort_keys=True) + "\n")
    (OUT / "reference_diversity.json").write_text(json.dumps(diversity, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
