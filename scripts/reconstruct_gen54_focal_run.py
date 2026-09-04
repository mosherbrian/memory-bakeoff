#!/usr/bin/env python3
"""Answer Sol's condition directly: is `11-IP1-r1-E` genuinely rejected?

Gen53 could not tell, because the digests it had were artifact-inclusive. This
replays that run's own recorded edits - verbatim `oldText`/`newText` from
`tools.ndjson` - onto a fresh copy of the frozen IP1 fixture and recomputes both
digests at every step. If `tracked-tree-digest-v1` returns the run to its initial
digest at the point v1 actually stopped it, the refusal is real rather than an
artefact of K.
"""
from __future__ import annotations

import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import tracked_digest as T   # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen54"
RUN = (ROOT / "results/pi_quiescent_completion_gen52/runs"
       / "11-IP1-r1-pi_harness_state_control_quiescent_k3_v1")
GEN48 = ROOT / "results" / "pi_state_control_gen48"


def fresh_worktree(repo: Path) -> Path:
    target = Path(tempfile.mkdtemp(prefix="gen54-focal-"))
    shutil.rmtree(target)
    shutil.copytree(repo, target)
    shutil.rmtree(target / ".git", ignore_errors=True)
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "-c", "user.email=p@x.invalid", "-c", "user.name=p",
                    "commit", "-qm", "run"], cwd=target, check=True)
    return target


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    worktree = fresh_worktree(ROOT / manifest["tasks"]["IP1"]["repo_path"])
    leaf = json.loads((RUN / "leaf.json").read_text())

    steps = [{"step": "initial", "tracked": T.tracked_digest(worktree),
              "whole_worktree": T.whole_worktree_digest(worktree)}]
    initial_tracked = steps[0]["tracked"]

    applied, skipped = 0, []
    for line in (RUN / "tools.ndjson").read_text().splitlines():
        row = json.loads(line)
        if row.get("phase") != "call" or row.get("tool") not in ("edit", "write", "multi_edit"):
            continue
        args = row.get("args") or {}
        path = Path(args["path"])
        target = worktree / path.name if path.parent.name == worktree.name else \
            worktree / Path(*path.parts[path.parts.index("run_11") + 1:]) \
            if "run_11" in path.parts else worktree / path.name
        for edit in args.get("edits", []):
            text = target.read_text()
            if edit["oldText"] not in text:
                skipped.append({"path": str(target.relative_to(worktree)),
                                "reason": "recorded oldText not present"})
                continue
            target.write_text(text.replace(edit["oldText"], edit["newText"], 1))
            applied += 1
        steps.append({"step": f"after edit {applied}",
                      "file": str(target.relative_to(worktree)),
                      "tracked": T.tracked_digest(worktree),
                      "whole_worktree": T.whole_worktree_digest(worktree)})

    # The agent ran the visible tests between and after its edits; that is what
    # created the artifacts which moved the old digest.
    subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/"], cwd=worktree,
                   capture_output=True)
    steps.append({"step": "after running the visible tests",
                  "tracked": T.tracked_digest(worktree),
                  "whole_worktree": T.whole_worktree_digest(worktree)})

    final = steps[-1]
    result = {
        "contract": T.contract(),
        "run": RUN.name,
        "recorded": {
            "start_tree": leaf["task"]["start_tree"],
            "final_tree": leaf["task"]["final_tree"],
            "qualifying_tree_digest_recorded_live":
                leaf["measured"]["quiescent_stop"]["qualifying_tree_digest"],
            "hidden_verifier_passed": leaf["verifier"]["passed"],
        },
        "edits_applied": applied, "edits_skipped": skipped,
        "steps": steps,
        "answer": {
            "tracked_digest_returns_to_initial_after_the_revert":
                final["tracked"] == initial_tracked,
            "whole_worktree_digest_returns_to_initial_after_the_revert":
                final["whole_worktree"] == steps[0]["whole_worktree"],
            "running_the_tests_moves_the_old_digest_but_not_the_new": (
                final["whole_worktree"] != steps[0]["whole_worktree"]
                and final["tracked"] == initial_tracked),
        },
    }
    result["v2_would_genuinely_reject_this_run"] = \
        result["answer"]["tracked_digest_returns_to_initial_after_the_revert"]
    (OUT / "focal_run_reconstruction.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"edits_applied": applied, "skipped": skipped,
                      "steps": [{k: (v[:12] if isinstance(v, str) and len(v) == 40 else v)
                                 for k, v in s.items()} for s in steps],
                      "answer": result["answer"],
                      "verdict": result["v2_would_genuinely_reject_this_run"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
