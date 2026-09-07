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
    # Round-7 NEW-3: this used to assert `str(31) in txt and str(18) in txt`,
    # which any document containing an unrelated 31 and 18 would satisfy, and
    # which never checked 8 or 11 at all. A guard that cannot fail is theatre -
    # this repo's own doctrine, LEDGER 145 - so it now locates the partition as
    # a group of four numbers in order, not four digits anywhere.
    import re
    pattern = re.compile(
        r"later session\D{0,40}" + str(later) + r"\D{1,80}" + str(earlier)
        + r"\D{1,60}" + str(both) + r"\D{1,80}" + str(blind), re.S)
    for name in ("handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md"):
        txt = (ROOT / name).read_text()
        assert pattern.search(txt), (
            f"{name} does not carry the committed partition "
            f"{later}/{earlier}/{both}/{blind} as a located group")


def test_the_pilot_headline_in_prose_is_what_the_code_computes():
    """Round-8 defect 1: the first version of this asserted only that each file
    contained "of {n}" or "n={n}". In PILOT_ORDERING_RESULT.md the only "of 17"
    was in the DATE-WORD CAVEAT, not the headline - and that caveat's number was
    itself wrong, so the guard passed on a borrowed error and would have FAILED
    once the caveat was corrected. Review demonstrated both by mutation. A guard
    sustained by a number known to be wrong is worse than none.

    So: every figure of the cleaned block, in every document, located as a group.
    """
    import json
    import re
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts/recompute_pilot.py")],
                   capture_output=True, cwd=ROOT, check=True)
    h = json.loads((ROOT / "research/pilot_ordering/PILOT_HEADLINE.json").read_text())
    d, st = h["dated"]["cleaned"], h["dates_stripped"]["cleaned"]
    assert d["n"] == st["n"]
    n = d["n"]

    def block(txt):
        """The two cleaned rows must appear together: dated hits, then stripped
        hits, then both discordances - within one span, not scattered."""
        sep = rf"\s*(?:/|of)\s*{n}"      # documents write both "15/17" and "15 of 17"
        pat = (rf"{d['chronological_hits']}{sep}\D{{1,60}}"
               rf"{d['reversed_hits']}{sep}"
               rf"[\s\S]{{0,200}}"
               rf"{st['chronological_hits']}{sep}\D{{1,60}}"
               rf"{st['reversed_hits']}{sep}")
        return re.search(pat, txt)

    for name in ("handoff/GEN124_RECAP.md",
                 "handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md"):
        txt = (ROOT / name).read_text()
        assert block(txt), (
            f"{name} does not carry the cleaned block as a located group: "
            f"dated {d['chronological_hits']}/{n} vs {d['reversed_hits']}/{n}, "
            f"stripped {st['chronological_hits']}/{n} vs {st['reversed_hits']}/{n}")

    for name in ("handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md"):
        txt = (ROOT / name).read_text()
        for v in (d["discordant_chronological_only"], st["discordant_chronological_only"]):
            assert f"{v} vs 0" in txt, f"{name} does not state the {v} vs 0 discordance"


def test_the_date_word_caveats_are_computed_not_counted():
    """Round-8 defect 2 / LEDGER 154. The caveat said 29 and 17; no rule produced
    either, and one of them was propping up the guard above."""
    import json
    h = json.loads((ROOT / "research/pilot_ordering/PILOT_HEADLINE.json").read_text())
    dw = h["date_words"]
    for name in ("handoff/GEN124_RECAP.md",
                 "handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md"):
        txt = (ROOT / name).read_text()
        assert f"{dw['month_or_year']} of the {dw['n_pilot']}" in txt, (
            f"{name} does not state the computed month-or-year count "
            f"{dw['month_or_year']} of {dw['n_pilot']}")
        for dead in ("29 of 34", "17 of 34 items"):
            assert dead not in txt, f"{name} still states the uncomputed {dead!r}"


def test_no_document_still_claims_the_superseded_cleaned_headline():
    """The specific dead numbers, named. They may appear only where retracted."""
    import re
    for name in ("handoff/GEN124_RECAP.md",
                 "handoff/GEN124_TECHNICAL.md",
                 "research/pilot_ordering/PILOT_ORDERING_RESULT.md",
                 "research/pilot_ordering/PREREGISTRATION.md"):
        txt = (ROOT / name).read_text()
        for i, line in enumerate(txt.splitlines(), 1):
            if re.search(r"\b(22|21)\s*/\s*30\b|\bchronological 22/30\b", line):
                window = " ".join(txt.splitlines()[max(0, i - 6):i + 4])
                assert re.search(r"earlier version|no committed rule|An earlier|superseded",
                                 window, re.I), f"{name}:{i} states a dead headline: {line[:90]}"
