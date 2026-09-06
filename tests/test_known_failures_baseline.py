"""The suite is red, and that is exactly how a real regression hides.

Twice in this project I reported a red suite as normal because the count looked
familiar. A count is not an identity: 24 failures can become a different 24 while
the number stays put. This compares the actual failing node ids against a
recorded baseline, so a new failure is a NEW failure no matter what the total is.

It works in both directions on purpose. An unlisted failure is a regression. A
listed failure that now passes is a stale baseline entry, and must be removed -
a list that only ever grows is a place to hide things.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "KNOWN_FAILURES.json"


def _baseline() -> set[str]:
    d = json.loads(BASELINE.read_text())
    return {n for c in d["clusters"].values() for n in c["node_ids"]}


@pytest.fixture(scope="module")
def observed() -> set[str]:
    """Run the whole suite once, excluding this file, and collect failures.

    Excluding itself is not cosmetic: a run that included this test would recurse.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--continue-on-collection-errors",
         "--deselect", f"tests/{Path(__file__).name}",
         "--ignore", f"tests/{Path(__file__).name}"],
        cwd=ROOT, capture_output=True, text=True,
        # Inherit the real environment. A hardcoded PATH=/usr/bin:/bin is exactly
        # the host-brittleness LEDGER #50 removed from the reader runner, and this
        # guard reproduced it. Found by glm-5.3 at Gen120 r4.
        env={**os.environ, "PYTHONPATH": "src:vendor/membukkit/src"},
        timeout=1800)
    # BOTH classes. The first version read only FAILED lines, so the five
    # collection errors were invisible to a guard whose docstring promised to
    # catch "any unlisted failure" - a claim exceeding its mechanism, which is the
    # disease this repository keeps diagnosing. Found by glm-5.3 at Gen120 r4.
    out = set()
    for ln in r.stdout.splitlines():
        for prefix in ("FAILED ", "ERROR "):
            if ln.startswith(prefix):
                out.add(ln[len(prefix):].split(" - ")[0].strip())
    return out


def test_no_unlisted_failures(observed):
    new = sorted(observed - _baseline())
    assert not new, (
        "NEW failures not in tests/KNOWN_FAILURES.json - these are regressions, "
        f"not the usual red:\n  " + "\n  ".join(new))


def test_no_stale_baseline_entries(observed):
    fixed = sorted(_baseline() - observed)
    assert not fixed, (
        "these are listed as known failures but now PASS; remove them from "
        "tests/KNOWN_FAILURES.json so the baseline cannot drift upward:\n  "
        + "\n  ".join(fixed))


def test_every_known_failure_carries_a_reason():
    d = json.loads(BASELINE.read_text())
    for name, cluster in d["clusters"].items():
        assert cluster.get("why", "").strip(), f"{name} has no stated cause"
        assert len(cluster["node_ids"]) == cluster["count"], (
            f"{name}: count disagrees with the listed ids")
