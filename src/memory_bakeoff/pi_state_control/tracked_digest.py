"""`tracked-tree-digest-v1`: fingerprint the project, not the build output.

Gen52's stop rule was supposed to refuse to stop a run whose tree was back where
it started. Gen53 measured that the refusal never fired, and found why: the
fingerprint was `git add -A` over the whole worktree, so it counted `__pycache__`
and `.pytest_cache`. Running the visible tests moved the fingerprint on its own,
which meant "the tree changed" was satisfied by bytecode.

This computes the same digest with a frozen list of build artifacts excluded. It
still sees a newly added source file - a naive tracked-files-only digest would
not, and an agent adding a module is real progress.

Nothing here touches the real index: the tree is built in a temporary one seeded
from HEAD and thrown away.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "tracked-tree-digest-v1"

# Frozen. Incidental output of running the project's own checks, and nothing else.
ARTIFACT_EXCLUSIONS = (
    ":(exclude)**/__pycache__/**",
    ":(exclude)__pycache__/**",
    ":(exclude)**/*.pyc",
    ":(exclude)**/.pytest_cache/**",
    ":(exclude).pytest_cache/**",
)


def _write_tree(worktree: Path, pathspecs: tuple[str, ...]) -> str:
    handle, index = tempfile.mkstemp(prefix=".tree-index-", dir=str(worktree.parent))
    os.close(handle)
    env = {**os.environ, "GIT_INDEX_FILE": index}
    try:
        subprocess.run(["git", "read-tree", "HEAD"], cwd=worktree, env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "-A", "--", *pathspecs], cwd=worktree, env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        done = subprocess.run(["git", "write-tree"], cwd=worktree, env=env,
                              capture_output=True, text=True, check=True)
        return done.stdout.strip()
    except subprocess.CalledProcessError:
        return ""
    finally:
        Path(index).unlink(missing_ok=True)


def tracked_digest(worktree: Path) -> str:
    """The project's state, ignoring what running the checks leaves behind."""
    return _write_tree(worktree, (".", *ARTIFACT_EXCLUSIONS))


def whole_worktree_digest(worktree: Path) -> str:
    """What Gen52 and Gen53 actually recorded, kept for comparison only."""
    return _write_tree(worktree, (".",))


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "replaces": "whole-worktree `git add -A` digest used through Gen53",
        "why": ("running the project's visible checks creates __pycache__ and .pytest_cache, which "
                "changed the old digest on its own, so a rule asking 'did the tree change' was "
                "satisfied by bytecode alone"),
        "excludes": list(ARTIFACT_EXCLUSIONS),
        "still_sees": ["edits to tracked files", "newly added source files", "deletions"],
        "never_touches_the_real_index": True,
        "contract_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
