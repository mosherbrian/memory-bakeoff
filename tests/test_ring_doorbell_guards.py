"""The doorbell has an outward effect, so its refusals must be tested, not assumed.

Drilling this script on 2026-09-06 opened a live PR because the clean-tree check
filtered out untracked files and there was no dry-run mode. These tests pin both
fixes. They never pass --fire, so they cannot create anything.
"""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ring-doorbell"


def run(args, cwd=ROOT):
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd,
                          capture_output=True, text=True,
                          env={**os.environ, "PATH": os.environ.get("PATH", "/usr/bin:/bin")})


def test_script_exists_and_parses():
    assert SCRIPT.exists()
    r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_no_arguments_refuses():
    assert run([]).returncode != 0


def test_unreadable_body_refuses():
    r = run(["116", "x", "/nonexistent/body.md"])
    assert r.returncode == 1
    assert "REFUSING" in r.stdout + r.stderr


def test_title_prefix_is_constructed_not_accepted():
    """The caller supplies only a suffix; the prefix cannot be overridden.

    The Gen115 doorbell was titled "Doorbell: ..." and the control-plane webhook,
    which filters on BAKEOFF_HANDOFF, never fired.
    """
    body = SCRIPT.read_text()
    assert 'REQUIRED_PREFIX="BAKEOFF_HANDOFF"' in body
    assert 'TITLE="$REQUIRED_PREFIX Gen$SRC_GEN - $SUFFIX"' in body


def test_pins_origin_main_not_head():
    body = SCRIPT.read_text()
    assert "COMMIT=$(git rev-parse origin/main)" in body
    assert "git rev-parse HEAD" not in body


def test_untracked_files_count_as_dirty():
    """`git status --porcelain | grep -v '^??'` was the hole that fired PR #17."""
    body = SCRIPT.read_text()
    assert "grep -v '^??'" not in body, "untracked files must not be filtered out"
    assert 'DIRT=$(git status --porcelain)' in body


def test_firing_requires_an_explicit_flag():
    body = SCRIPT.read_text()
    assert 'if [ "${1:-}" = "--fire" ]' in body
    assert 'if [ "$FIRE" != "1" ]' in body
    assert "DRY RUN" in body


def test_dry_run_creates_nothing(tmp_path):
    """Whatever the guards decide, a run without --fire must not push or open a PR."""
    body = tmp_path / "body.md"
    body.write_text("drill\n")
    before = subprocess.run(["git", "branch", "-a"], cwd=ROOT,
                            capture_output=True, text=True).stdout
    r = run(["116", "guard-drill", str(body)])
    after = subprocess.run(["git", "branch", "-a"], cwd=ROOT,
                           capture_output=True, text=True).stdout
    assert before == after, "a dry run must not create a branch"
    assert "gh pr create" not in r.stdout
    # It either refused a guard, or reported a dry run. Never a real ring.
    assert ("REFUSING" in r.stdout) or ("DRY RUN" in r.stdout), r.stdout + r.stderr
