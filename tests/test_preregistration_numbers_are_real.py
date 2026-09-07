"""Every count in the preregistration must be what the code actually produces.

Third recurrence tonight of "the edit reported success and changed nothing": a
replace whose pattern did not match left `11 unspent items` standing in three
places after the set had become 14, while the commit message said otherwise.
LEDGER 140 covers the same class for a retracted phrase.

Prose cannot be trusted to track a number. This makes the document's numbers
executable.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "research/pilot_ordering/PREREGISTRATION.md"


def _runner_unspent_count() -> int:
    r = subprocess.run([sys.executable, str(ROOT / "scripts/run_preregistered_ordering.py"),
                        "--dry-run"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    m = re.search(r"unspent and eligible:\s*(\d+)\s*items", r.stdout)
    assert m, r.stdout
    return int(m.group(1))


def test_the_adopted_membership_matches_the_runner():
    n = _runner_unspent_count()
    txt = PREREG.read_text()
    assert f"§4 hit, session scope, {n} unspent items" in txt, (
        f"the runner produces {n} unspent items; the preregistration's adopted-rule "
        "sentence does not say so")
    assert f"leaves **{n} items**" in txt, (
        f"section 3a does not state {n}")


def test_the_power_floor_p_values_are_correct():
    """The stated p-values must be the ones the runner's own test computes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prr", ROOT / "scripts/run_preregistered_ordering.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    n = _runner_unspent_count()
    txt = PREREG.read_text()
    all_one_way = m.mcnemar_exact_two_sided(n, 0)
    floor = m.mcnemar_exact_two_sided(6, 0)
    assert f"p = {all_one_way:.5f}".rstrip("0") in txt or f"{all_one_way:.5f}" in txt, (
        f"all-{n}-one-way is p={all_one_way:.5f}; the document does not say so")
    assert f"{floor:.5f}" in txt, f"the 6-pair floor is p={floor:.5f}"


def test_no_superseded_membership_count_stands_as_current():
    """A stale count may appear in the amendment log, which is history, but never
    in the sentences that state what the run IS."""
    n = _runner_unspent_count()
    txt = PREREG.read_text().splitlines()
    live = []
    for i, line in enumerate(txt, 1):
        if re.search(r"(adopted|leaves|section 3a).*\b(\d+)\s*(unspent )?items", line, re.I):
            for num in re.findall(r"\b(\d+)\s*(?:unspent )?items", line, re.I):
                if int(num) != n and int(num) not in (28,):
                    live.append(f"{i}: {line.strip()[:100]}")
    assert not live, "a superseded membership count is stated as current:\n  " + "\n  ".join(live)


def test_the_handoff_states_the_same_membership():
    """Round-6 N2: the technical handoff said 28 where the answer was 14. The
    executable check covered PREREGISTRATION.md and not the handoff, which is
    exactly how it survived. A number that matters is checked wherever it is
    written, not only where it was first written."""
    n = _runner_unspent_count()
    tech = (ROOT / "handoff/GEN124_TECHNICAL.md").read_text()
    assert f"{n} unspent" in tech, f"the handoff does not state {n} unspent items"
    for stale in ("28 unspent", "11 unspent"):
        assert stale not in tech, f"the handoff still states {stale!r}"


def test_the_substrate_partition_in_prose_matches_the_committed_artifact():
    """Round-6 N3: two documents reported 47/8/2/11 while the script and its own
    artifact said 31/8/18/11. Prose describing a measurement must agree with the
    measurement's committed output."""
    import json
    sv = json.loads((ROOT / "research/pilot_ordering/SUBSTRATE_VERIFY.json").read_text())
    later, earlier = len(sv["gold_only_later"]), len(sv["gold_only_earlier"])
    both, blind = len(sv["gold_both"]), len(sv["gold_unlocatable_by_matcher"])
    for name in ("handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md"):
        txt = (ROOT / name).read_text()
        assert str(later) in txt and str(both) in txt, (
            f"{name} does not carry the committed partition "
            f"{later}/{earlier}/{both}/{blind}")
