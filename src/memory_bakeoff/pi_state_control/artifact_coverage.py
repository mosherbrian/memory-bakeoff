"""`artifact-coverage-diagnostics-v1`: does the test suite actually touch the change?

Gen56 settled that running a *broader* test command catches nothing: on every one
of 72 recorded trees the project's whole suite passed, including the fourteen
that were wrong. The gap is not how much of the suite runs. It is whether the
suite exercises and constrains the change at all.

Two deterministic diagnostics, both built from visible artifacts only. Neither
is a correctness oracle and neither may be read as one.

  changed-line-execution-v1
      Did the visible suite ever execute the changed production lines? A line
      being executed says the test reached it. It says nothing about whether the
      behaviour was checked.

  change-reversion-sensitivity-v1
      Undo one hunk of the change and run the suite again. If it still passes,
      the visible tests do not establish that the hunk was needed. A surviving
      reversion is evidence of test insensitivity, not proof the hunk is
      required by the task; killing every reversion proves no semantic
      sufficiency either.

The hidden verifier is not an input anywhere in this file.
"""
from __future__ import annotations

import ast
import hashlib
import re
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "artifact-coverage-diagnostics-v1"

# Same exclusions as the tracked digest: build output is not project state.
ARTIFACT_DIRS = {"__pycache__", ".pytest_cache", ".git"}

# Written to a temporary file and executed in a child process so that tracing
# cannot leak into this one.
TRACE_RUNNER = '''
import json, os, sys, threading
# `python -m pytest` puts the working directory on sys.path; running through a
# script does not, so the project would not import and every line would look
# unexecuted. Restore the invocation the frozen command actually has.
sys.path.insert(0, os.getcwd())
hits = set()
targets = set(json.load(open(sys.argv[1])))
def tracer(frame, event, arg):
    if event == "line":
        name = frame.f_code.co_filename
        if name in targets:
            hits.add((name, frame.f_lineno))
    return tracer
threading.settrace(tracer)
sys.settrace(tracer)
import pytest
code = pytest.main(["tests/", "-q", "-p", "no:cacheprovider"])
sys.settrace(None)
threading.settrace(None)
json.dump({"exit": int(code), "hits": sorted(list(h) for h in hits)}, open(sys.argv[2], "w"))
'''


def production_paths(tree: Path) -> list[Path]:
    """Tracked project source, excluding tests and build output."""
    found = []
    for path in sorted(tree.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(tree).parts)
        if parts & ARTIFACT_DIRS or "tests" in parts:
            continue
        found.append(path)
    return found


def executable_lines(source_file: Path) -> set[int]:
    """Statement and expression lines, from the AST. Comments never count."""
    try:
        tree = ast.parse(source_file.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return set()
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt) or isinstance(node, ast.expr):
            if getattr(node, "lineno", None):
                lines.add(node.lineno)
    return lines


def changed_lines(initial: Path, final: Path, relative: str) -> dict[str, Any]:
    """Added or modified line numbers on the final side, from a real diff."""
    old = initial / relative
    new = final / relative
    if not new.exists():
        return {"status": "deleted_only", "lines": []}
    if not old.exists():
        return {"status": "added_file", "lines": sorted(executable_lines(new))}
    done = subprocess.run(["diff", "-u", "-U0", str(old), str(new)],
                          capture_output=True, text=True)
    lines: set[int] = set()
    for row in done.stdout.splitlines():
        if not row.startswith("@@"):
            continue
        try:
            after = row.split("+")[1].split("@@")[0].strip()
            start, _, count = after.partition(",")
            start_line, span = int(start), int(count or 1)
        except (IndexError, ValueError):
            continue
        lines.update(range(start_line, start_line + span))
    return {"status": "modified", "lines": sorted(lines)}


def run_traced_broad_check(tree: Path, targets: list[Path], timeout: int = 300) -> dict[str, Any]:
    """The frozen broad visible command, under line tracing, in a child process."""
    workdir = Path(tempfile.mkdtemp(prefix="gen57-trace-"))
    runner = workdir / "runner.py"
    runner.write_text(TRACE_RUNNER)
    targets_file = workdir / "targets.json"
    targets_file.write_text(json.dumps([str(p.resolve()) for p in targets]))
    out_file = workdir / "hits.json"
    import time
    started = time.time()
    done = subprocess.run([sys.executable, str(runner), str(targets_file), str(out_file)],
                          cwd=tree, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    elapsed = round(time.time() - started, 2)
    result = {"traced": True, "seconds": elapsed, "stderr_tail": done.stderr.strip()[-200:]}
    if out_file.exists():
        payload = json.loads(out_file.read_text())
        result["exit"] = payload["exit"]
        result["passed"] = payload["exit"] == 0
        result["hits"] = {(h[0], h[1]) for h in payload["hits"]}
    else:
        result.update({"exit": None, "passed": None, "hits": set(),
                       "error": "trace runner produced no output"})
    shutil.rmtree(workdir, ignore_errors=True)
    return result


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "diagnostics": {
            "changed-line-execution-v1": {
                "question": "did the frozen broad visible test execute the changed production lines?",
                "method": "sys.settrace line events in a child process running the frozen command",
                "changed_executable_lines": ("AST statement/expression lines intersected with added "
                                             "or modified diff lines; comments and blank lines never count"),
                "binary_signal": "any changed executable line not hit",
                "explicitly_not": ["assertion coverage", "proof of correctness",
                                   "evidence the behaviour was checked"],
                "unsupported_categories": ["deleted_only", "non_python", "no_production_change"],
            },
            "change-reversion-sensitivity-v1": {
                "question": "can one hunk of the change be undone with the visible suite still passing?",
                "method": ("reverse exactly one production diff hunk toward the shipped initial tree "
                           "in an isolated copy, rerun the frozen broad visible command, restore"),
                "killed_reversion": "the broad visible check fails, so the suite notices the loss",
                "survived_reversion": "the broad visible check passes, so the suite does not establish the hunk was needed",
                "binary_signal": "any applicable production hunk reversion survives",
                "explicitly_not": ["proof the hunk is required by the task",
                                   "semantic sufficiency when every reversion is killed"],
                "no_operator_zoo": ("probes are grounded in the run's own diff, not synthetic mutation "
                                    "operators, so there is no operator selection or equivalent-mutant "
                                    "tuning problem"),
            },
        },
        "requirement_traceability": {
            "instantiated": False,
            "why": ("the IP fixtures carry prose requirements but no machine-readable requirement IDs "
                    "or author-supplied requirement-to-test mapping; inferring one would need a model "
                    "or heuristic semantics, which this generation excludes"),
            "status": "structurally unavailable from current visible metadata, not a negative result",
        },
        "production_paths": "tracked source outside tests/, VCS metadata and build artifacts",
        "tests_are_not_production_targets_but_test_changes_are_recorded": True,
        "hidden_verifier_is_never_an_input": True,
        "frozen_screening_thresholds": {
            "flags_at_least": "50% of the known coverage-gap runs",
            "flags_at_most": "25% of reconstructable hidden-correct runs",
            "note": "screening only; not statistical power, and not permission to gate completion",
        },
        "contract_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


# --- change-reversion-sensitivity-v1 -----------------------------------------

def _git(tree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=tree, capture_output=True, text=True)


def production_hunks(initial: Path, final: Path) -> list[dict[str, Any]]:
    """One patch per production diff hunk, initial -> final.

    Built with a throwaway repository so the diff is git's own, and split so a
    single hunk can be reversed while every other change stays in place.
    """
    work = Path(tempfile.mkdtemp(prefix="gen57-hunks-"))
    base = work / "tree"
    shutil.copytree(initial, base)
    shutil.rmtree(base / ".git", ignore_errors=True)
    _git(base, "init", "-q")
    _git(base, "add", "-A")
    _git(base, "-c", "user.email=p@x.invalid", "-c", "user.name=p", "commit", "-qm", "initial")
    for path in list(base.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            path.unlink()
    for source in production_paths(final):
        target = base / source.relative_to(final)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for source in (final / "tests").rglob("*") if (final / "tests").exists() else []:
        if source.is_file() and "__pycache__" not in source.parts:
            target = base / source.relative_to(final)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    # Stage first: a newly added file is untracked, and untracked files do not
    # appear in `git diff` at all. Zero context so two adjacent changes stay two
    # hunks rather than being merged into one.
    _git(base, "add", "-A")
    diff = _git(base, "diff", "--cached", "--no-color", "-U0",
                "--", ".", ":(exclude)tests/**").stdout
    hunks, current, header = [], [], []
    for line in diff.splitlines(keepends=True):
        if line.startswith("diff --git"):
            if current:
                hunks.append("".join(header + current))
                current = []
            header = [line]
        elif line.startswith(("index ", "--- ", "+++ ", "new file mode", "deleted file mode",
                              "similarity index", "rename from", "rename to")):
            if current:
                hunks.append("".join(header + current))
                current = []
            header.append(line)
        elif line.startswith("@@"):
            if current:
                hunks.append("".join(header + current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        hunks.append("".join(header + current))
    shutil.rmtree(work, ignore_errors=True)
    return [{"index": i, "patch": h,
             "paths": sorted({m for m in re.findall(r"^\+\+\+ b/(.+)$", h, re.M)})}
            for i, h in enumerate(hunks) if h.strip()]


def reverse_probe(final: Path, patch: str) -> dict[str, Any]:
    """Undo one hunk in an isolated copy. Never touches the reconstruction."""
    work = Path(tempfile.mkdtemp(prefix="gen57-probe-"))
    copy = work / "tree"
    shutil.copytree(final, copy)
    shutil.rmtree(copy / ".git", ignore_errors=True)
    _git(copy, "init", "-q")
    _git(copy, "add", "-A")
    _git(copy, "-c", "user.email=p@x.invalid", "-c", "user.name=p", "commit", "-qm", "final")
    patch_file = work / "hunk.patch"
    patch_file.write_text(patch)
    applied = _git(copy, "apply", "-R", "--unidiff-zero", "--whitespace=nowarn", str(patch_file))
    return {"work": work, "tree": copy, "applied": applied.returncode == 0,
            "apply_error": applied.stderr.strip()[-200:] if applied.returncode else ""}
