"""The runner's refusals must actually fire. A gate that cannot refuse is worse
than no gate: it reads as protection and provides none. This repo has shipped
that four times in one afternoon, so every gate below is drilled with a case
that MUST be rejected, not only one that passes.

No test here calls a reader.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_preregistered_ordering.py"


def run(*args):
    return subprocess.run([sys.executable, str(RUNNER), *args],
                          capture_output=True, text=True, cwd=ROOT)


def test_dry_run_calls_no_reader_and_reports_the_hash():
    r = run("--dry-run")
    assert r.returncode == 0, r.stderr
    assert "DRY RUN. No reader was called." in r.stdout
    assert "preregistration sha256" in r.stdout


def test_it_refuses_without_authorisation():
    r = run()
    assert r.returncode != 0
    assert "REFUSED" in r.stderr and "--authorised-by" in r.stderr


def test_it_refuses_authorisation_without_the_preregistration_hash():
    r = run("--authorised-by", "somebody")
    assert r.returncode != 0
    assert "REFUSED" in r.stderr


def test_it_refuses_a_stale_preregistration_hash():
    """The document that constrains the run is pinned BY the run. Amend it after
    authorisation and the authorisation dies with it."""
    r = run("--authorised-by", "somebody", "--prereg-sha256", "0" * 64)
    assert r.returncode != 0
    assert "the preregistration has changed" in r.stderr


def test_the_eligible_set_is_the_size_the_preregistration_claims():
    """Two independent implementations - scripts/verify_substrate.py and the
    runner - must agree, or section 2 admits more than one reading again."""
    r = run("--dry-run")
    assert "unspent and eligible: 14 items" in r.stdout, r.stdout


def test_mcnemar_is_exact_and_two_sided():
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("prr", RUNNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    f = m.mcnemar_exact_two_sided
    assert f(0, 0) == 1.0                     # no discordance decides nothing
    assert f(8, 0) == 2 * (0.5 ** 8)          # all one way, the pilot's shape
    assert f(5, 5) == 1.0                     # symmetric is maximally unsurprising
    assert f(6, 0) < 0.05 and f(5, 0) > 0.05  # the stated power floor is real
    assert f(3, 1) == f(1, 3)                 # two-sided is symmetric


def test_the_power_floor_matches_the_preregistration():
    """Section 2 promises the run declares itself underpowered below 6 discordant
    pairs. That number must be the one where the test can still reach alpha."""
    txt = (ROOT / "research/pilot_ordering/PREREGISTRATION.md").read_text()
    assert "fewer than 6 discordant pairs" in txt
    assert "underpowered" in txt.lower()
