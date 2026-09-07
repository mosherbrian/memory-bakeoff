"""A claim marked FIXED in the ledger must not still stand somewhere else.

This class has now bitten twice in one generation:

  LEDGER 138  I fixed the recap, marked the row FIXED, and left the instance
              round 3 had NAMED standing in handoff/GEN124_TECHNICAL.md. The
              recap then cited the technical record as its authority for not
              drawing a conclusion the technical record drew.
  LEDGER 140  I reported a phrase deleted from four places; one edit silently
              did not apply because the pattern did not match across a line
              break.

Both were caught by a reviewer or by a grep, not by anything standing. This is
the standing thing. Every retracted claim is listed here with the places it is
ALLOWED to appear - which is only where it is quoted in order to be retracted.
A new retraction that is not added here will not be enforced, so the list is
part of retracting something, not an optional extra.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# phrase -> files where the phrase may appear because it is being retracted there
RETRACTED = {
    "cannot manufacture a direction": {
        "PILOT_ORDERING_RESULT.md", "GEN124_TECHNICAL.md", "LEDGER.md",
        "ordering_scorer.py", "GEN124_RECAP.md",
    },
    "the part nobody has published": {
        "BENCHMARK_HARVEST_CHECK.md", "LEDGER.md",
    },
    "largely following position": {
        "GEN124_TECHNICAL.md", "LEDGER.md",
    },
    "vendored and pinned": {
        "BENCHMARK_HARVEST_CHECK.md", "LEDGER.md",
    },
}

# A line is a retraction, not a live claim, if it carries one of these nearby.
_RETRACTION_MARKERS = re.compile(
    r"retract|withdraw|is false|was false|was wrong|NOT\b|no longer|must not|"
    r"deleted|corrected|an earlier version|first answer|is dead|WRONG", re.I)


# Verbatim third-party material is EVIDENCE, not a claim this project makes.
# On 2026-09-07 this guard flagged an independent auditor's transcript for the
# sentence "the Gen124 'crude scorers cannot manufacture a direction' principle
# retracted as false" - a line that exists precisely to record the retraction.
#
# The only ways to make that pass are to edit an external audit transcript, or
# to exempt it. Editing it is tampering with a review record, so the guard is
# scoped instead. A guard whose green state requires altering someone else's
# testimony is a dangerous guard, and that is worth more than the coverage.
_EVIDENCE_DIRS = ("reviews",)


def _docs():
    for pattern in ("**/*.md", "src/**/*.py", "scripts/**/*.py"):
        for f in ROOT.glob(pattern):
            if ".git" in f.parts or "node_modules" in f.parts:
                continue
            if f.relative_to(ROOT).parts[0] in _EVIDENCE_DIRS and f.name != "LEDGER.md":
                continue
            yield f


@pytest.mark.parametrize("phrase", sorted(RETRACTED))
def test_a_retracted_claim_appears_only_where_it_is_being_retracted(phrase):
    live = []
    for f in _docs():
        try:
            lines = f.read_text().splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines):
            if phrase.lower() not in line.lower():
                continue
            if f.name in RETRACTED[phrase]:
                window = " ".join(lines[max(0, i - 4):i + 5])
                if _RETRACTION_MARKERS.search(window):
                    continue
            live.append(f"{f.relative_to(ROOT)}:{i + 1}: {line.strip()[:110]}")
    assert not live, (
        f"the retracted claim {phrase!r} still stands as a live claim:\n  "
        + "\n  ".join(live))


def test_the_guard_can_actually_fail(tmp_path):
    """The control this guard needs. If a retracted phrase in a file with no
    retraction language nearby does NOT trip it, everything above is theatre."""
    probe = ROOT / "docs" / "_retraction_guard_probe.md"
    probe.parent.mkdir(exist_ok=True)
    probe.write_text("The scorer cannot manufacture a direction, so we are fine.\n")
    try:
        with pytest.raises(AssertionError):
            test_a_retracted_claim_appears_only_where_it_is_being_retracted(
                "cannot manufacture a direction")
    finally:
        probe.unlink()


def test_every_retracted_phrase_is_actually_in_the_ledger():
    """A phrase listed here but never retracted in the ledger means the list has
    drifted from the record it enforces."""
    ledger = (ROOT / "reviews/LEDGER.md").read_text().lower()
    missing = [p for p in RETRACTED if p.lower() not in ledger]
    assert not missing, f"listed as retracted but absent from the ledger: {missing}"
