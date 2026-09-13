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


def _parse_observed(stdout: str) -> set[str]:
    out = set()
    for ln in stdout.splitlines():
        for prefix in ("FAILED ", "ERROR "):
            if ln.startswith(prefix):
                out.add(ln[len(prefix):].split(" - ")[0].strip())
    return out


def _require_run_evidence(stdout: str, stderr: str, returncode: int) -> None:
    """Fail LOUDLY if the subprocess shows no evidence pytest ever ran.

    An empty observed set is ambiguous between "the suite is green" and
    "the subprocess died before pytest started". In a redirected-HOME lane
    the old hardcoded PYTHONPATH replace made the subprocess die with
    "No module named pytest", which made this guard pass vacuously (the
    regression sentinel saw nothing, ever) while flagging the whole
    baseline as stale. Found by Kiln 2026-09-12,
    team/KILN-KNOWN-FAILURES-GUARD-20260912.md.
    """
    ran = any(
        marker in stdout for marker in (" passed", " failed", " error", "no tests ran")
    )
    if not ran:
        pytest.fail(
            "the baseline subprocess produced no pytest run evidence - this guard "
            "refuses to pass vacuously on an empty observed set. "
            f"returncode={returncode}\nstdout tail:\n{stdout[-1500:]}\n"
            f"stderr tail:\n{stderr[-1500:]}"
        )


@pytest.fixture(scope="module")
def observed() -> set[str]:
    """Run the whole suite once, excluding this file, and collect failures.

    Excluding itself is not cosmetic: a run that included this test would recurse.
    """
    # Merge, never replace: the historical replace dropped the REAL-home user
    # site-packages in redirected-HOME lanes, so the subprocess died before
    # pytest imported (see _require_run_evidence).
    existing_pp = os.environ.get("PYTHONPATH", "")
    env_pp = os.pathsep.join(
        p for p in ("src", "vendor/membukkit/src", existing_pp) if p
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--continue-on-collection-errors",
         "--deselect", f"tests/{Path(__file__).name}",
         "--ignore", f"tests/{Path(__file__).name}"],
        cwd=ROOT, capture_output=True, text=True,
        # Inherit the real environment. A hardcoded PATH=/usr/bin:/bin is exactly
        # the host-brittleness LEDGER #50 removed from the reader runner, and this
        # guard reproduced it. Found by glm-5.3 at Gen120 r4.
        env={**os.environ, "PYTHONPATH": env_pp},
        timeout=1800)
    # BOTH classes. The first version read only FAILED lines, so the five
    # collection errors were invisible to a guard whose docstring promised to
    # catch "any unlisted failure" - a claim exceeding its mechanism, which is the
    # disease this repository keeps diagnosing. Found by glm-5.3 at Gen120 r4.
    _require_run_evidence(r.stdout, r.stderr, r.returncode)
    return _parse_observed(r.stdout)


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


def test_the_guard_fails_loud_when_the_subprocess_never_ran():
    """The Gen120-era failure mode, frozen as a test: a subprocess that dies
    before pytest imports must LOUDEN this guard, never pass it vacuously."""
    with pytest.raises(pytest.fail.Exception, match="no pytest run evidence"):
        _require_run_evidence("", "No module named pytest\n", 1)


def test_the_guard_accepts_a_real_run_with_zero_failures():
    # A genuinely green suite always prints its stats line - that is the
    # evidence the loud check requires.
    _require_run_evidence("=========== 1625 passed in 12.34s ===========\n", "", 0)
