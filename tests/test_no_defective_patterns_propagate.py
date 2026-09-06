"""Stop known-defective patterns from spreading by being read.

On 2026-09-06 both rival reviewers flagged that `run_gen114_reader.py` treated a
tree with untracked files as clean. The finding was recorded and the code was
left alone - so the pattern stayed in the repository as a template, and over the
next nine hours it was copied into `ring-doorbell` (where it let a drill fire a
live doorbell PR), into `propose-generation`, and finally into a Gen117 runner
written by an ENTIRELY DIFFERENT MODEL that had never seen those mistakes.

Three independent reproductions from one source. The defect was not
implementer-shaped; it was repository-shaped. A review finding does not edit the
code it is about, so a defective pattern left in tracked source keeps teaching
itself to whoever reads it next.

These tests are the cheap mechanism that would have stopped all three.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SEARCH = ("scripts", "src", "tests")

# Exemptions are PER PATTERN, never per file. A blanket file exemption would
# excuse a file from every future rule as well as the one it was granted for.
#
# Note the third entry. Twice today a guard fired on text that FORBIDS a pattern
# rather than text that commits it - once on a runner's own docstring, once here.
# A checker that cannot tell an assertion from a violation is the same bug it is
# hunting, so the distinction is made explicit rather than hand-waved.
ALLOWLIST = {
    "untracked_files_treated_as_clean": {
        "scripts/run_gen114_reader.py": (
            "Gen114's runner, preserved as the record of how Gen114 ran. Its "
            "clean-tree check filtered untracked files, which is why Gen114 "
            "shipped a runner absent from its own pinned commit. Left intact "
            "deliberately: correcting it would falsify the historical record."
        ),
    },
    "seed_acceptance_authored": {
        "scripts/run_gen114_reader.py": (
            "Gen114 authored `\"seed_accepted\": True` at line 101 without ever "
            "reading it back from the server. The control plane named this defect "
            "in the Gen117 brief. Preserved intact: it is the record of what "
            "Gen114 actually claimed, and correcting it would hide the claim."
        ),
        "tests/test_gen117_execution.py": (
            "Contains the literal only inside an assertion that FORBIDS it. The "
            "line is the guard against the defect, not an instance of it."
        ),
        "tests/test_gen119_run_apparatus.py": (
            "Same reason: the literal appears only inside the assertion that "
            "forbids authoring seed acceptance. The v6 apparatus tests inherit "
            "that guard from the v5 ones, so they inherit the exemption too."
        ),
    },
}

PATTERNS = {
    "untracked_files_treated_as_clean": (
        re.compile(r"""startswith\(\s*["']\?\?["']\s*\)|grep\s+-v\s+["']\^\?\?["']"""),
        "A tree with untracked files is NOT clean. Filtering '??' hid a runner "
        "that did not exist at its pinned commit, and later fired a live PR.",
    ),
    "seed_acceptance_authored": (
        re.compile(r"""seed_accepted["']?\s*[:=]\s*True"""),
        "Seed acceptance must be read from server evidence, never authored. "
        "Gen114 hardcoded it and the control plane called it out by name.",
    ),
}


def _sources():
    for d in SEARCH:
        for p in (ROOT / d).rglob("*.py"):
            yield p
        for p in (ROOT / d).rglob("*.sh"):
            yield p
    for p in (ROOT / "scripts").iterdir():
        if p.is_file() and p.suffix == "" and p.read_bytes()[:2] == b"#!":
            yield p


@pytest.mark.parametrize("name", sorted(PATTERNS))
def test_defective_pattern_does_not_spread(name):
    pattern, why = PATTERNS[name]
    offenders = []
    for path in set(_sources()):
        rel = str(path.relative_to(ROOT))
        if rel in ALLOWLIST.get(name, {}):
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        # Skip this file: it necessarily contains the patterns it forbids.
        if rel == f"tests/{Path(__file__).name}":
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{rel}:{i}: {line.strip()}")
    assert not offenders, f"{why}\n" + "\n".join("  " + o for o in offenders)


def test_allowlist_entries_still_exist_and_are_explained():
    """An allowlist that names vanished files quietly stops protecting anything."""
    for pattern_name, entries in ALLOWLIST.items():
        assert pattern_name in PATTERNS, f"allowlist names unknown pattern {pattern_name}"
        for rel, reason in entries.items():
            assert (ROOT / rel).exists(), f"allowlisted {rel} no longer exists"
            assert len(reason) > 60, f"{rel} needs a real reason, not a shrug"


def test_the_allowlisted_file_really_does_contain_the_pattern():
    """If it no longer does, the exemption is dead weight and must be removed."""
    for pattern_name, entries in ALLOWLIST.items():
        pattern, _ = PATTERNS[pattern_name]
        for rel in entries:
            assert pattern.search((ROOT / rel).read_text()), \
                f"{rel} no longer matches {pattern_name}; drop the exemption"
