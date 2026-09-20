#!/usr/bin/env python3
"""Gate for QUEUE row S6-1 (the publishable correction to the S4-12 zeros).

plumb-fable, row S6-1G, 2026-09-17. Written FROM ROW S6-1's TEXT ALONE, before
any S6-1 artifact existed (`team/S6-CORRECTION/` was absent). The interface below
is therefore declared by the gate, not fitted to a document; every finding names
what it wants, so the author can conform without reading this source.

What it requires (marker in brackets):
  files       note.md, numeric-claims.json, review.json, publication.json
              [MISSING-FILE] [BAD-JSON]
  defect (a)  the scenario counts AGREE with each other. numeric-claims.json
              carries claims `scenarios_total`, `scenarios_nonempty`,
              `scenarios_empty` (each: id, numeric value, source); total is 60 and
              nonempty + empty = total [NUMERIC-CLAIMS] [PARTITION-SUM]. note.md
              states both counts [SCENARIO-COUNT-MISSING], and every scenario
              count it asserts next to an emptiness word is one of those three
              numbers, unless the sentence marks the number as the retracted one
              ("said 37 ... wrong") [SCENARIO-COUNT-DISAGREES].
  defect (b)  the fixture dating relative to eval_now is EXPLAINED, not merely
              present: one paragraph names eval_now, names the future dating, and
              gives a cause [DATING-ABSENT] [DATING-UNEXPLAINED]; the note also
              addresses the 90-day window claim [TEMPORAL-CLAIM-UNADDRESSED].
  no ranking  no rank/leaderboard/outperforms/winner language unless a negation
              precedes it [ENGINE-RANKING], and the note says so explicitly
              [NO-RANKING-STATEMENT-MISSING].
  correction  cause = retrieval configuration, not measurement error
              [CAUSE-MISSING]; "verifying the arithmetic did not validate the
              experiment" [TRANSFERABLE-FINDING-MISSING]; FirePrecision, if
              named, is distinguished from retrieval precision
              [FIREPRECISION-CONFLATED].
  review      reviewer, author, verdict; reviewer is not the author
              [REVIEW-INCOMPLETE] [REVIEW-NOT-INDEPENDENT].
  publication receipt names revision and destination, no placeholders
              [PUBLICATION-RECEIPT].

Limit, stated on purpose: this proves the document agrees WITH ITSELF and makes
the row's distinctions. It cannot prove the explanation is true or the counts
match the pinned results; that stays with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S6-1 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT]      # ROOT defaults to this directory
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = ("note.md", "numeric-claims.json", "review.json", "publication.json")
TOTAL = 60
PART_IDS = ("scenarios_total", "scenarios_nonempty", "scenarios_empty")

NEG = re.compile(r"\b(?:no|not|never|without|neither|nor|cannot)\b|n['’]t", re.I)
RANK = re.compile(r"\b(?:rank(?:s|ed|ing|ings)?|leaderboard|league table)\b", re.I)
COMPARE = re.compile(
    r"\b(?:outperform\w*|beats?|winner|wins|superior to|1st|2nd|3rd"
    r"|best[- ](?:engine|system|performer|performing)"
    r"|top[- ](?:engine|performer|performing|ranked)"
    r"|(?:first|second|third|last) place)\b|\w+\s*>\s*\w+\s*>\s*\w+", re.I)
EMPTY_KW = re.compile(r"non-?\s?empty|\bempty\b|\bnone\b|\bno (?:retriev|result)", re.I)
RETRACT = re.compile(
    r"wrong|incorrect|contradict|erron|mistak|original|previous|earlier"
    r"|\bsaid\b|\bstated\b|\bclaimed\b|should (?:be|have)|supersed|retract", re.I)
NUM = re.compile(r"(?<![\w.\-/@≥>])(\d+)(?!\.\d|[\w\-%])")
FUTURE = re.compile(r"future[- ]dat|2026-09-01|(?:after|later than|ahead of)\s+`?eval_now", re.I)
CAUSE = re.compile(
    r"\b(?:because|due to|caused by|so that|by design|deliberately|intentionally"
    r"|as a result of|the reason|stems? from|in order to)\b", re.I)
UNEXPLAINED = re.compile(
    r"unexplained|not (?:yet )?(?:been )?explained|no explanation|unknown|unclear"
    r"|\btbd\b|\btodo\b", re.I)
PLACEHOLDER = re.compile(r"^(?:|tbd|todo|pending|n/?a|none|unknown|\?+|x+)$", re.I)


def _units(text: str) -> list[str]:
    """Sentences, with hard-wrapped prose rejoined; table rows and list items
    stay whole so a number is judged with its own label."""
    blocks, cur = [], []

    def flush():
        if cur:
            blocks.append(" ".join(cur))
            cur.clear()

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if re.match(r"(?:\||#|[-*+]\s|\d+[.)]\s)", s):
            flush()
        cur.append(s)
        if s.startswith(("|", "#")):
            flush()
    flush()
    return [u for b in blocks for u in re.split(r"(?<=[.!?])\s+", b) if u]


def _neg_before(unit: str, m: re.Match) -> bool:
    return NEG.search(unit[:m.start()]) is not None


def _scenario_numbers(unit: str) -> list[int]:
    out = []
    for m in NUM.finditer(unit):
        before, after = unit[:m.start()], unit[m.end():]
        if re.search(r"(?:at least|>=)\s*$", before, re.I):
            continue  # "at least 1 non-empty turn" counts turns, not scenarios
        if re.match(r"\s*\+?\s*(?:non-?\s?empty|turns?\b|or more)", after, re.I):
            continue
        out.append(int(m.group(1)))
    return out


def _load_json(root: Path, name: str, findings: list):
    try:
        return json.loads((root / name).read_text(encoding="utf-8", errors="replace"))
    except ValueError as e:
        findings.append(("BAD-JSON", f"{name}: {e}"))
        return None


def _field(obj, *keys):
    if isinstance(obj, dict):
        for k in keys:
            v = obj.get(k)
            if isinstance(v, str) and not PLACEHOLDER.match(v.strip()):
                return v.strip()
    return None


def _check_claims(obj, findings: list):
    claims = obj.get("claims") if isinstance(obj, dict) else obj
    if not isinstance(claims, list) or not claims:
        findings.append(("NUMERIC-CLAIMS", "numeric-claims.json needs a non-empty "
                         "`claims` list of {id, value, source}"))
        return None
    vals = {}
    for i, c in enumerate(claims):
        ok = (isinstance(c, dict) and isinstance(c.get("id"), str)
              and isinstance(c.get("value"), (int, float))
              and not isinstance(c.get("value"), bool)
              and _field(c, "source") is not None)
        if not ok:
            findings.append(("NUMERIC-CLAIMS", f"claim #{i} lacks a string id, a "
                             "numeric value, or a non-placeholder source"))
            continue
        vals[c["id"]] = c["value"]
    absent = [k for k in PART_IDS if k not in vals]
    if absent:
        findings.append(("NUMERIC-CLAIMS", "missing scenario partition claim(s): "
                         + ", ".join(absent)))
        return None
    total, non, emp = (vals[k] for k in PART_IDS)
    if total != TOTAL or non + emp != total:
        findings.append(("PARTITION-SUM", f"nonempty {non} + empty {emp} = "
                         f"{non + emp}, total claimed {total}, row says {TOTAL}"))
        return None
    return total, non, emp


def _check_note(text: str, part, findings: list) -> None:
    units = _units(text)

    # defect (a): the document agrees with itself on the scenario counts
    if part:
        seen = set()
        for u in units:
            if not (re.search(r"scenario", u, re.I) and EMPTY_KW.search(u)):
                continue
            nums = _scenario_numbers(u)
            seen.update(nums)
            stray = [n for n in nums if n not in part]
            if stray and not RETRACT.search(u):
                findings.append(("SCENARIO-COUNT-DISAGREES",
                                 f"{stray} is not one of total/nonempty/empty "
                                 f"{part} and is not marked retracted :: {u[:110]}"))
        for label, n in (("nonempty", part[1]), ("empty", part[2])):
            if n not in seen:
                findings.append(("SCENARIO-COUNT-MISSING",
                                 f"note.md never states the {label} count {n} in a "
                                 "sentence about scenarios and empty/non-empty turns"))

    # defect (b): fixture dating vs eval_now is explained, not merely present
    paras = [p for p in re.split(r"\n\s*\n", text) if re.search(r"eval_now", p)]
    if not paras:
        findings.append(("DATING-ABSENT", "note.md never mentions eval_now"))
    elif not any(FUTURE.search(p) and CAUSE.search(p) and not UNEXPLAINED.search(p)
                 for p in paras):
        findings.append(("DATING-UNEXPLAINED",
                         "no paragraph names eval_now, names the future dating, AND "
                         "gives a cause (because / due to / by design ...)"))
    if not re.search(r"\b(?:90|ninety)[- ]day", text, re.I):
        findings.append(("TEMPORAL-CLAIM-UNADDRESSED",
                         "note.md does not say what the dating means for the "
                         "90-day window result"))

    # the row forbids an engine ranking, and wants that said explicitly
    stated = False
    for u in units:
        hits = list(RANK.finditer(u)) + list(COMPARE.finditer(u))
        bad = [m.group(0) for m in hits if not _neg_before(u, m)]
        if bad:
            findings.append(("ENGINE-RANKING", f"{bad} :: {u[:110]}"))
        stated |= any(_neg_before(u, m) for m in RANK.finditer(u))
    if not stated:
        findings.append(("NO-RANKING-STATEMENT-MISSING",
                         "note.md must state explicitly that it gives no engine ranking"))

    # the correction itself
    if not (re.search(r"configur", text, re.I)
            and re.search(r"measurement error", text, re.I)):
        findings.append(("CAUSE-MISSING", "note.md must attribute the zeros to the "
                         "retrieval configuration, not measurement error"))
    if not any(re.search(r"arithmetic", u, re.I) and re.search(r"experiment", u, re.I)
               and NEG.search(u) for u in units):
        findings.append(("TRANSFERABLE-FINDING-MISSING", "no sentence says that "
                         "verifying the arithmetic did not validate the experiment"))
    fire = re.compile(r"fire\s?precision", re.I)
    if fire.search(text) and not any(
            fire.search(u) and re.search(r"retrieval precision", u, re.I)
            and (NEG.search(u) or re.search(r"differ|distinct|separate", u, re.I))
            for u in units):
        findings.append(("FIREPRECISION-CONFLATED", "FirePrecision is named but never "
                         "distinguished from retrieval precision"))


def check(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    missing = [f for f in FILES
               if not (root / f).is_file() or not (root / f).stat().st_size]
    for f in missing:
        findings.append(("MISSING-FILE", f"{f} (absent or empty)"))

    part = None
    if "numeric-claims.json" not in missing:
        obj = _load_json(root, "numeric-claims.json", findings)
        if obj is not None:
            part = _check_claims(obj, findings)
    if "note.md" not in missing:
        _check_note((root / "note.md").read_text(encoding="utf-8", errors="replace"),
                    part, findings)
    if "review.json" not in missing:
        obj = _load_json(root, "review.json", findings)
        if obj is not None:
            who = _field(obj, "reviewer", "verifier", "reviewed_by")
            author = _field(obj, "author")
            if not (who and author and _field(obj, "verdict", "status", "result")):
                findings.append(("REVIEW-INCOMPLETE",
                                 "review.json needs reviewer, author and verdict"))
            elif who.lower() == author.lower():
                findings.append(("REVIEW-NOT-INDEPENDENT",
                                 f"reviewer and author are both {who!r}"))
    if "publication.json" not in missing:
        obj = _load_json(root, "publication.json", findings)
        if obj is not None and not (
                _field(obj, "revision", "commit", "rev")
                and _field(obj, "destination", "url", "published_to")):
            findings.append(("PUBLICATION-RECEIPT", "publication.json must name the "
                             "revision and the destination, no placeholders"))
    return findings


# ---- selftest: the gate must be able to fail, and able to pass ----

_GOOD_NOTE = """# Correction to the S4-12 zeros

## What was reported
S4-12 reported zero retrieval for every engine.

## Why it was wrong
The zeros came from the retrieval configuration, not measurement error.

## What the corrected settings produce
19/60 scenarios had at least one non-empty turn.
41 of 60 scenarios had no non-empty turn.
The re-run document said 37 scenarios had no non-empty turn in F4; that was
wrong.

## Fixture dating
Fixture records are stamped 2026-09-01 while eval_now is pinned at 2026-08-30.
The fixtures are future-dated because the generator stamped records with its
wall-clock build date. No temporal claim, the 90-day window result included, is
quoted here.

## Scope
This note gives no engine ranking.
Verifying the arithmetic did not validate the experiment.
Trigger FirePrecision is not retrieval precision; they are different measures.
"""
_SRC = "results/pinned/summary.csv"
_GOOD_JSON = {
    "numeric-claims.json": {"claims": [
        {"id": "scenarios_total", "value": 60, "source": _SRC},
        {"id": "scenarios_nonempty", "value": 19, "source": _SRC},
        {"id": "scenarios_empty", "value": 41, "source": _SRC}]},
    "review.json": {"reviewer": "corvid-dsh", "author": "kiln-flash",
                    "verdict": "pass"},
    "publication.json": {"revision": "8bdf517", "destination": "team/PUBLISHED.md"},
}


def _build(root: Path, note: str = _GOOD_NOTE, **json_overrides) -> None:
    (root / "note.md").write_text(note, encoding="utf-8")
    for name, obj in _GOOD_JSON.items():
        obj = json_overrides.get(name.split(".")[0].replace("-", "_"), obj)
        (root / name).write_text(obj if isinstance(obj, str) else json.dumps(obj),
                                 encoding="utf-8")


def _claims(empty: int):
    return {"claims": [dict(c, value=empty) if c["id"] == "scenarios_empty" else c
                       for c in _GOOD_JSON["numeric-claims.json"]["claims"]]}


_DATING_GOOD = _GOOD_NOTE.split("## Fixture dating\n")[1].split("\n\n## Scope")[0]

# one defect each, so every check is shown to fail on its own
_MUTANTS = {
    "SCENARIO-COUNT-DISAGREES": dict(note=_GOOD_NOTE.replace(
        "The re-run document said 37 scenarios had no non-empty turn in F4; that was\n"
        "wrong.", "F4: 37 scenarios had no non-empty turn.")),
    "SCENARIO-COUNT-MISSING": dict(note=_GOOD_NOTE.replace(
        "41 of 60 scenarios had no non-empty turn.\n", "")),
    "PARTITION-SUM": dict(numeric_claims=_claims(37)),
    "NUMERIC-CLAIMS": dict(numeric_claims={}),
    "BAD-JSON": dict(review="{not json"),
    "DATING-UNEXPLAINED": dict(note=_GOOD_NOTE.replace(
        _DATING_GOOD, "Fixture records are stamped 2026-09-01; eval_now is "
        "2026-08-30. The 90-day window result stands.")),
    "DATING-ABSENT": dict(note=_GOOD_NOTE.replace(
        _DATING_GOOD, "The 90-day window result stands.")),
    "TEMPORAL-CLAIM-UNADDRESSED": dict(note=_GOOD_NOTE.replace("90-day", "long")),
    "ENGINE-RANKING": dict(note=_GOOD_NOTE + "\nEngine A outperforms Engine B.\n"),
    "NO-RANKING-STATEMENT-MISSING": dict(note=_GOOD_NOTE.replace(
        "This note gives no engine ranking.\n", "")),
    "CAUSE-MISSING": dict(note=_GOOD_NOTE.replace(
        "The zeros came from the retrieval configuration, not measurement error.",
        "The zeros were wrong.")),
    "TRANSFERABLE-FINDING-MISSING": dict(note=_GOOD_NOTE.replace(
        "Verifying the arithmetic did not validate the experiment.\n", "")),
    "FIREPRECISION-CONFLATED": dict(note=_GOOD_NOTE.replace(
        "Trigger FirePrecision is not retrieval precision; they are different "
        "measures.", "Retrieval precision (FirePrecision) was 0.8.")),
    "REVIEW-NOT-INDEPENDENT": dict(review={"reviewer": "kiln-flash",
                                           "author": "kiln-flash", "verdict": "pass"}),
    "REVIEW-INCOMPLETE": dict(review={"verdict": "pass"}),
    "PUBLICATION-RECEIPT": dict(publication={"revision": "TBD",
                                             "destination": "team/PUBLISHED.md"}),
}
_RANK_TABLE = "\n| Rank | Engine | Score |\n|---|---|---|\n| 1 | A | 0.9 |\n"
_MARKER = re.compile(r"S6-1 gate findings: [1-9]")


def _selftest() -> int:
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good"
        good.mkdir()
        _build(good)
        got = check(good)
        if got:
            fails.append(f"conforming fixture REJECTED: {got}")

        for marker, kw in _MUTANTS.items():
            d = Path(td) / marker
            d.mkdir()
            _build(d, **kw)
            if marker not in {m for m, _ in check(d)}:
                fails.append(f"mutant for [{marker}] was ACCEPTED or mis-named: "
                             f"{check(d)}")

        table = Path(td) / "ranktable"
        table.mkdir()
        _build(table, note=_GOOD_NOTE + _RANK_TABLE)
        if "ENGINE-RANKING" not in {m for m, _ in check(table)}:
            fails.append("a Rank-column table was ACCEPTED")

        for f in FILES:  # every declared file is required, one at a time
            d = Path(td) / f"no-{f}"
            d.mkdir()
            _build(d)
            (d / f).unlink()
            if ("MISSING-FILE", f"{f} (absent or empty)") not in check(d):
                fails.append(f"fixture without {f} was ACCEPTED")

        # the real command line, both ways, plus a root that tries to crash it
        bad = Path(td) / "bad"
        bad.mkdir()
        _build(bad, note="F4: 37 scenarios had no non-empty turn. 19/60 had one.\n"
                         "Ranking: A beats B.\n", numeric_claims=_claims(37))
        crash = Path(td) / "crash"
        crash.mkdir()
        _build(crash, numeric_claims="[1, 2]", review="[]", publication='"x"')
        (crash / "note.md").unlink()
        (crash / "note.md").mkdir()
        for label, root, want in (("clean", good, 0), ("dirty", bad, 1),
                                  ("hostile", crash, 1)):
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                str(root)], capture_output=True, text=True, timeout=60)
            text = p.stdout + p.stderr
            if p.returncode != want:
                fails.append(f"CLI [{label}]: exit {p.returncode}, expected {want}")
            if "Traceback (most recent call last)" in text:
                fails.append(f"CLI [{label}]: traceback instead of a verdict")
            if bool(_MARKER.search(text)) != bool(want):
                fails.append(f"CLI [{label}]: finding marker "
                             f"{'absent' if want else 'printed on a clean root'}")
    for f in fails:
        print(f"[SELFTEST-FAIL] {f}")
    if fails:
        print(f"S6-1 gate selftest findings: {len(fails)}")
        return 1
    print(f"selftest: PASS (conforming fixture accepted; {len(_MUTANTS)} single-defect "
          f"mutants, a rank table, {len(FILES)} missing-file roots, and the dirty and "
          "hostile CLI roots all rejected by name, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S6-1")
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    findings = check(Path(a.root))
    for marker, detail in findings:
        print(f"[{marker}] {detail}")
    if findings:
        print(f"S6-1 gate findings: {len(findings)}")
        return 1
    print("S6-1 gate: clean")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as e:  # a crash must still read as a finding, not a trace
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S6-1 gate findings: 1")
        raise SystemExit(1)
