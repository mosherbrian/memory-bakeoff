#!/usr/bin/env python3
"""Gate for QUEUE row S8-5 (HANDBOOK body pass: two failure classes into the
stale-path probes).

plumb-fable, row S8-5G, 2026-09-17. Written FROM ROW S8-5's TEXT ALONE, while
`team/S8-HANDBOOK-PASS.md` did not exist. Read for this gate: the board row and
the three inputs the row names or feeds - the verified card
(team/CANDIDATE-CARD-HANDBOOK.md), its pin check
(team/CORVID-HANDBOOK-PINCHECK.md) and the stale-path probe design
(team/SPARK-STALE-PATH-PROBE-DESIGN-20260914.md). The paper and the repository
were NOT opened. The interface below is declared by the gate, not fitted to a
document; every finding names what it wants.

It lives at `team/S8-HANDBOOK-PASS-check.py` and checks `team/S8-HANDBOOK-PASS.md`,
the paths the board declares (first written under the S7- name the board carried
that morning; moved when the board was corrected).

The row's point: a DESIGN INPUT, not a press release. The card already holds
the abstract; the pass must show it read the body, extract the rubric schema,
and give the two named failure classes each a transfer verdict that lands as a
concrete change to the stale-path probes - or is recorded as a reference. And
it admits no run.

Declared interface: one markdown file with these lines and sections
  Source: arXiv:<id><version>    the pin, exactly as the pin check confirms it
  Repo: github.com/surge-ai/handbook    License: Apache-2.0
  Status: design-only, no run admitted
  Prior: no design pass exists (and the card and pin check named)
  Feeds: SPARK-STALE-PATH-PROBE-DESIGN-20260914.md
  ## Rubric schema     a table of at least 4 rows, naming both required and
                       prohibited criteria, a `Grading:` line (deterministic or
                       programmatic) and a `Repo path:` line
  ## Transfer verdict  one block per failure class:
      Class: authorized-vs-unauthorized precedence  |  check-performed-then-ignored
      Verdict: transfers | partial | does-not-transfer
      Because: <at least 30 characters>
      then, for transfers or partial, at least one
      Probe change (<probe family or control named in the design>): <text>
      Grader: <how the probe grades it, naming required or prohibited>
      or, for does-not-transfer,
      Recorded as: policy-following design reference

What the row turns on (marker in brackets)
  (a) BODY, not abstract. The paper is pinned as the pin check confirms it
      [SOURCE-UNPINNED] [PIN-MISMATCH]; at least 3 body locations are cited
      (§, Section, Table, Figure, Appendix, page) [BODY-NOT-READ]; the schema
      is drawn from a named repo path [SCHEMA-UNSOURCED].
  (b) RUBRIC SCHEMA extracted, with the distinction the card values: required
      AND prohibited criteria [SCHEMA-SECTION-MISSING] [SCHEMA-THIN]
      [SCHEMA-NO-PROHIBITED] [SCHEMA-GRADING-UNSTATED].
  (c) A TRANSFER VERDICT for each of the two named classes, no more, no less
      [CLASS-MISSING] [CLASS-DUPLICATED] [VERDICT-INVALID] [VERDICT-UNREASONED];
      a verdict that transfers lands in the probes as a change to something the
      design names [NO-PROBE-CHANGE] [PROBE-UNKNOWN], graded the deterministic
      way [GRADER-UNSTATED]; one that does not is recorded as a reference
      [REFERENCE-NOT-RECORDED]; the design it feeds is named [DESIGN-NOT-CITED].
  (d) DESIGN ONLY. Status says so [STATUS-NOT-DESIGN-ONLY]; no run result is
      reported [RUN-SMUGGLED]; the vendor rates the card says never to cite are
      absent [SCORE-IMPORTED]; licence and repo are stated [SOURCE-UNPINNED].
  (e) PRIOR stated: no design pass exists, card and pin check named
      [PRIOR-NOT-STATED] [CARD-NOT-CITED].
  other  [MISSING-FILE] [EMPTY] [PINCHECK-UNREADABLE] [DESIGN-UNREADABLE]

Limits, stated on purpose: the gate cannot read the paper, so it cannot tell
that a cited section says what the pass says it says, or that the schema is
the repository's. Whether a probe change is a GOOD change stays with the named
verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S8-5 gate findings: N`, never a traceback.

Usage:
  python3 S8-HANDBOOK-PASS-check.py [PASS.md] [--pincheck FILE] [--design FILE]
  python3 S8-HANDBOOK-PASS-check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE
DEFAULT = TEAM / "S8-HANDBOOK-PASS.md"
PINCHECK = TEAM / "CORVID-HANDBOOK-PINCHECK.md"
DESIGN = TEAM / "SPARK-STALE-PATH-PROBE-DESIGN-20260914.md"
CARD = "CANDIDATE-CARD-HANDBOOK.md"
REPO = "github.com/surge-ai/handbook"
CLASSES = {  # the card's two named classes, matched by their key words
    "authorized-vs-unauthorized precedence":
        re.compile(r"authori[sz]ed.{0,12}unauthori[sz]ed|precedence", re.I),
    "check-performed-then-ignored":
        re.compile(r"check.{0,20}(performed|then).{0,20}ignored", re.I),
}
VERDICTS = ("transfers", "partial", "does-not-transfer")
ARXIV = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})(v\d+)?", re.I)
BODY_CITE = re.compile(r"§\s*\d|\bSection\s+\d|\bSec\.\s*\d|\bTable\s+\d"
                       r"|\bFigure\s+\d|\bFig\.\s*\d|\bAppendix\s+[A-Z0-9]"
                       r"|\bp\.\s*\d+|\bpage\s+\d+", re.I)
RUN = re.compile(r"\bwe ran\b|\bran the\b|\bpass rate\b|\bpassed \d+ of \d+"
                 r"|\b\d+\s*/\s*\d+\s*(criteria|tasks|items)\s*(passed|met)"
                 r"|^#+\s*results\b|\bmeasured on\b|\bstale-use rate (of|was|=)"
                 r"\s*\d", re.I | re.M)
VENDOR = re.compile(r"\b36\.2\b|<\s*25\s*%", re.I)
MIN_CITES, MIN_ROWS, MIN_WHY = 3, 4, 30


def _section(text: str, title: str) -> str | None:
    m = re.search(rf"^##+\s*{title}[^\n]*\n(.*?)(?=^##+\s|\Z)", text,
                  re.I | re.M | re.S)
    return m.group(1) if m else None


def _line(text: str, key: str) -> str | None:
    m = re.search(rf"^\**{key}\**:\**\s*(.+?)\s*$", text, re.I | re.M)
    return m.group(1) if m else None


def _table_rows(text: str) -> int:
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    return max(0, len(rows) - 2) if len(rows) >= 2 else 0


def _blocks(section: str) -> list[str]:
    parts = re.split(r"(?=^\**Class\**:)", section, flags=re.M)
    return [p for p in parts if re.match(r"^\**Class\**:", p)]


def check(path: Path, pincheck: Path, design: Path) -> tuple[list, str]:
    f: list[tuple[str, str]] = []
    try:
        pin = ARXIV.search(pincheck.read_text(encoding="utf-8", errors="replace"))
        if not pin:
            raise ValueError("no arXiv id in the pin check")
        pin_id = pin.group(1) + (pin.group(2) or "")
    except (OSError, ValueError) as e:
        return [("PINCHECK-UNREADABLE", f"{pincheck}: {e}")], ""
    try:
        design_text = design.read_text(encoding="utf-8", errors="replace").lower()
        if not design_text.strip():
            raise ValueError("empty")
    except (OSError, ValueError) as e:
        return [("DESIGN-UNREADABLE", f"{design}: {e}")], ""
    if not path.is_file():
        return [("MISSING-FILE", str(path))], ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 200:
        return [("EMPTY", f"{path.name} holds {len(text.strip())} characters")], ""

    # (a) body, not abstract; pinned
    cited = ARXIV.search(text)
    if not cited or REPO not in text or not re.search(r"Apache-2\.0", text):
        f.append(("SOURCE-UNPINNED", f"needs Source: arXiv:<id><version>, "
                  f"Repo: {REPO} and License: Apache-2.0"))
    elif cited.group(1) + (cited.group(2) or "") != pin_id:
        f.append(("PIN-MISMATCH", f"cites arXiv:{cited.group(0)[6:].strip()}; "
                  f"the pin check confirms arXiv:{pin_id}. Cite the pinned "
                  f"version"))
    cites = len(BODY_CITE.findall(text))
    if cites < MIN_CITES:
        f.append(("BODY-NOT-READ", f"{cites} body locations cited (§, Section, "
                  f"Table, Figure, Appendix, page); a body pass cites at least "
                  f"{MIN_CITES}. The abstract is already in the card"))

    # (d) design only
    status = _line(text, "Status") or ""
    if not (re.search(r"design[- ]only", status, re.I)
            and re.search(r"no run", status, re.I)):
        f.append(("STATUS-NOT-DESIGN-ONLY", "needs a line `Status: design-only, "
                  "no run admitted`"))
    hit = RUN.search(text)
    if hit:
        f.append(("RUN-SMUGGLED", f"reports a run ({hit.group(0)!r}); this "
                  f"candidate admits no run"))
    hit = VENDOR.search(text)
    if hit:
        f.append(("SCORE-IMPORTED", f"cites the vendor rate {hit.group(0)!r} "
                  f"the card says not to cite"))

    # (e) prior
    prior = _line(text, "Prior") or ""
    if not re.search(r"no design pass|none exists|no prior", prior, re.I):
        f.append(("PRIOR-NOT-STATED", "needs a line `Prior: no design pass "
                  "exists`, per the re-measurement rule"))
    if CARD not in text or pincheck.name not in text:
        f.append(("CARD-NOT-CITED", f"must name {CARD} and {pincheck.name}"))
    if design.name not in text:
        f.append(("DESIGN-NOT-CITED", f"must name the design it feeds: "
                  f"{design.name}"))

    # (b) rubric schema
    schema = _section(text, "Rubric schema")
    if schema is None:
        f.append(("SCHEMA-SECTION-MISSING", "needs a `## Rubric schema` section"))
    else:
        if _table_rows(schema) < MIN_ROWS:
            f.append(("SCHEMA-THIN", f"the schema section needs a table of at "
                      f"least {MIN_ROWS} rows (the criterion fields)"))
        if not (re.search(r"\brequired\b", schema, re.I)
                and re.search(r"\bprohibited\b", schema, re.I)):
            f.append(("SCHEMA-NO-PROHIBITED", "the schema must carry both "
                      "criterion kinds: required actions occurred AND "
                      "prohibited actions did not"))
        grading = _line(schema, "Grading") or ""
        if not re.search(r"deterministic|programmatic", grading, re.I):
            f.append(("SCHEMA-GRADING-UNSTATED", "the schema section needs "
                      "`Grading: deterministic ...` (or programmatic), "
                      "the property the row is for"))
        if not re.search(r"^\**Repo path\**:\**\s*\S+/\S+", schema, re.I | re.M):
            f.append(("SCHEMA-UNSOURCED", "the schema section needs "
                      "`Repo path: <path in surge-ai/handbook>` it was read "
                      "from"))

    # (c) transfer verdicts
    section = _section(text, "Transfer verdict")
    if section is None:
        f.append(("CLASS-MISSING", "needs a `## Transfer verdict` section with "
                  f"a Class: block for each of: {', '.join(CLASSES)}"))
        return f, ""
    blocks = _blocks(section)
    seen: dict[str, list[str]] = {name: [] for name in CLASSES}
    for b in blocks:
        head = b.splitlines()[0]
        for name, rx in CLASSES.items():
            if rx.search(head):
                seen[name].append(b)
    for name, found in seen.items():
        if not found:
            f.append(("CLASS-MISSING", f"no `Class: {name}` block"))
            continue
        if len(found) > 1:
            f.append(("CLASS-DUPLICATED", f"{len(found)} blocks for {name}"))
        b = found[0]
        verdict = (_line(b, "Verdict") or "").strip().lower().strip("*. ")
        if verdict not in VERDICTS:
            f.append(("VERDICT-INVALID", f"{name}: needs `Verdict: "
                      f"{' | '.join(VERDICTS)}`"))
            continue
        why = _line(b, "Because") or ""
        if len(why.strip()) < MIN_WHY:
            f.append(("VERDICT-UNREASONED", f"{name}: needs `Because: ...`, "
                      f"at least {MIN_WHY} characters"))
        if verdict == "does-not-transfer":
            if not re.search(r"^\**Recorded as\**:.*design reference", b,
                             re.I | re.M):
                f.append(("REFERENCE-NOT-RECORDED", f"{name}: does not "
                          f"transfer, so needs `Recorded as: policy-following "
                          f"design reference` (the card's step 2)"))
            continue
        changes = re.findall(r"^\**Probe change\**\s*\(([^)]+)\)\**:\s*(\S.*)$",
                             b, re.I | re.M)
        if not changes:
            f.append(("NO-PROBE-CHANGE", f"{name}: verdict {verdict} must land "
                      f"as `Probe change (<family or control>): <what changes "
                      f"in the stale-path probes>`"))
        unknown = [t for t, _ in changes if t.strip().lower() not in design_text]
        if unknown:
            f.append(("PROBE-UNKNOWN", f"{name}: probe change targets not "
                      f"named in {design.name}: {', '.join(unknown)}"))
        grader = _line(b, "Grader") or ""
        if len(grader.strip()) < MIN_WHY or not re.search(
                r"required|prohibited", grader, re.I):
            f.append(("GRADER-UNSTATED", f"{name}: needs `Grader: ...` "
                      f"(at least {MIN_WHY} characters) stating how the probe "
                      f"grades it as a required or prohibited observable"))
    return f, (f"{len(blocks)} class blocks, {cites} body citations, "
               f"schema table {_table_rows(schema or '')} rows")


def run(path: Path, pincheck: Path, design: Path) -> int:
    findings, summary = check(path, pincheck, design)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S8-5 gate findings: {len(findings)}")
        return 1
    print(f"S8-5 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_PINCHECK = ("# pin check\n\nChecked against `arXiv:2607.25398v3` and the code "
             "repo.\n\n## Verdict\n\nClean pass.\n")
_DESIGN = ("# stale-path probe design\n\nTwo item families:\n- **stale path**\n"
           "- **stale premise**\n\n## Controls\n\n- A **near-miss positive "
           "control**\n- An **OFF arm**\n")
_GOOD = f"""# HANDBOOK body pass: two failure classes into the stale-path probes

Source: arXiv:2607.25398v3
Repo: {REPO}
License: Apache-2.0
Status: design-only, no run admitted
Prior: no design pass exists; card {CARD}, pin CORVID-HANDBOOK-PINCHECK.md
Feeds: SPARK-STALE-PATH-PROBE-DESIGN-20260914.md

## Rubric schema

Read from §3.2 and Appendix B; field names from the harness.

| field | type | meaning |
|---|---|---|
| criterion_id | string | one of the 824 |
| kind | required or prohibited | action must occur, or must not |
| check | predicate | evaluated on the environment log |
| weight | int | strict grading needs all |

Grading: deterministic, one predicate per criterion (Table 2).
Repo path: handbook/grading/criteria.py

## Transfer verdict

Class: check-performed-then-ignored
Verdict: transfers
Because: §5.1 defines it as a required check whose result the agent then
contradicts, which is our stale premise shape with the check made explicit.
Probe change (stale premise): add an item where the agent reads the current
value and then uses the superseded one.
Grader: required action = the read occurred; prohibited action = the
superseded value appears in the answer.

Class: authorized-vs-unauthorized precedence
Verdict: partial
Because: §5.2 is a policy precedence conflict; only the distractor shape
carries over to a memory probe.
Probe change (near-miss positive control): the distractor is an unauthorized
in-context instruction that must not override the stored current value.
Grader: prohibited action = following the in-context instruction over the
stored value.
"""


def _swap(old: str, new: str, count: int = 1):
    def m(t):
        assert t.count(old) >= count, old
        return t.replace(old, new, count)
    return m


_PRESS = f"""# HANDBOOK is a strong benchmark

Source: arXiv:2607.25398v3, Repo: {REPO}, License: Apache-2.0

HANDBOOK offers 65 agentic tasks in self-contained company environments with
fully deterministic grading over 824 criteria. The strongest model reaches
36.2% under strict grading. This is exactly the shape we need and we should
adopt it for the stale-path probes. Its failure patterns are compelling and
map well onto our goals. See {CARD}.
"""

# name -> (mutation of the good text, markers that must be EXACTLY raised)
_MUTANTS = {
    "press release": (lambda t: _PRESS, lambda got: {
        "BODY-NOT-READ", "SCORE-IMPORTED", "STATUS-NOT-DESIGN-ONLY",
        "SCHEMA-SECTION-MISSING", "CLASS-MISSING"} <= got),
    "wrong version cited": (_swap("2607.25398v3", "2607.25398v1"),
                            {"PIN-MISMATCH"}),
    "no repo or licence": (_swap(f"Repo: {REPO}\nLicense: Apache-2.0\n", ""),
                           {"SOURCE-UNPINNED"}),
    "abstract only": (lambda t: re.sub(r"§\s*\d\.\d|Appendix B|Table 2", "the "
                                       "paper", t), {"BODY-NOT-READ"}),
    "status not design-only": (_swap("Status: design-only, no run admitted",
                                     "Status: ready"),
                               {"STATUS-NOT-DESIGN-ONLY"}),
    "run smuggled": (_swap("## Transfer verdict", "## Results\n\nWe ran the "
                          "probe: 7/10 items passed.\n\n## Transfer verdict"),
                     {"RUN-SMUGGLED"}),
    "vendor rate cited": (_swap("Because: §5.1", "Because: at 36.2% strict, "
                                "§5.1"), {"SCORE-IMPORTED"}),
    "prior not stated": (_swap("Prior: no design pass exists;", "Prior:"),
                         {"PRIOR-NOT-STATED"}),
    "pin check not named": (_swap(", pin CORVID-HANDBOOK-PINCHECK.md", ""),
                            {"CARD-NOT-CITED"}),
    "design not named": (_swap("Feeds: SPARK-STALE-PATH-PROBE-DESIGN-20260914"
                               ".md", "Feeds: the probes"),
                         {"DESIGN-NOT-CITED"}),
    "schema section missing": (_swap("## Rubric schema", "## Notes"),
                               {"SCHEMA-SECTION-MISSING"}),
    "schema is one row": (lambda t: re.sub(r"\| kind \|.*\n\| check \|.*\n"
                                           r"\| weight \|.*\n", "", t),
                          {"SCHEMA-THIN", "SCHEMA-NO-PROHIBITED"}),
    "schema without prohibited": (_swap("required or prohibited", "required"),
                                  {"SCHEMA-NO-PROHIBITED"}),
    "grading unstated": (_swap("Grading: deterministic, one predicate per "
                               "criterion (Table 2).", "Grading: see Table 2."),
                         {"SCHEMA-GRADING-UNSTATED"}),
    "schema unsourced": (_swap("Repo path: handbook/grading/criteria.py",
                               "Repo path: the harness"), {"SCHEMA-UNSOURCED"}),
    "one class missing": (lambda t: t[:t.index("Class: authorized")],
                          {"CLASS-MISSING"}),
    "class duplicated": (lambda t: t + "\nClass: check-performed-then-ignored\n"
                         "Verdict: transfers\nBecause: repeated with a "
                         "different verdict later on.\n", {"CLASS-DUPLICATED"}),
    "verdict outside vocabulary": (_swap("Verdict: partial", "Verdict: "
                                         "promising"), {"VERDICT-INVALID"}),
    "verdict unreasoned": (_swap("Because: §5.2 is a policy precedence "
                                 "conflict; only the distractor shape\ncarries "
                                 "over to a memory probe.", "Because: it fits."),
                           {"VERDICT-UNREASONED"}),
    "transfers with no probe change": (_swap("Probe change (stale premise): ",
                                             "Idea: "), {"NO-PROBE-CHANGE"}),
    "probe target not in the design": (_swap("Probe change (stale premise)",
                                             "Probe change (policy lane)"),
                                       {"PROBE-UNKNOWN"}),
    "grader unstated": (_swap("Grader: required action = the read occurred; "
                              "prohibited action = the\nsuperseded value "
                              "appears in the answer.", "Grader: by a judge."),
                        {"GRADER-UNSTATED"}),
    "does-not-transfer without a record": (_swap("Verdict: partial",
                                                 "Verdict: does-not-transfer"),
                                           {"REFERENCE-NOT-RECORDED"}),
    "near-empty file": (lambda t: "# HANDBOOK pass\n\nTBD\n", {"EMPTY"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "CORVID-HANDBOOK-PINCHECK.md").write_text(_PINCHECK)
        (d / "SPARK-STALE-PATH-PROBE-DESIGN-20260914.md").write_text(_DESIGN)

        def case(name, text, want, extra=()):
            p = d / f"{re.sub(r'[^a-z]+', '-', name)}.md"
            if text is not None:
                p.write_text(text)
            r = subprocess.run(
                [sys.executable, __file__, str(p), "--pincheck",
                 str(d / "CORVID-HANDBOOK-PINCHECK.md"), "--design",
                 str(d / "SPARK-STALE-PATH-PROBE-DESIGN-20260914.md"), *extra],
                capture_output=True, text=True, timeout=60)
            out = r.stdout + r.stderr
            got = set(marker.findall(out))
            ok = want(got) if callable(want) else got == want
            if "Traceback (most recent call last)" in out:
                bad.append(f"{name}: traceback")
            elif want is None and (r.returncode != 0 or got):
                bad.append(f"{name}: should be ACCEPTED, got exit "
                           f"{r.returncode} {sorted(got)}")
            elif want is not None and (r.returncode != 1 or not ok
                                       or "S8-5 gate findings: " not in out):
                bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                           f"{sorted(got)}")

        case("conforming", _GOOD, None)
        case("conforming, one class recorded as reference", _GOOD.replace(
            "Verdict: partial", "Verdict: does-not-transfer\nRecorded as: "
            "policy-following design reference"), None)
        for name, (mutate, want) in _MUTANTS.items():
            case(name, mutate(_GOOD), want)
        case("file missing", None, {"MISSING-FILE"})
        case("pin check unreadable", _GOOD, {"PINCHECK-UNREADABLE"},
             ("--pincheck", str(d / "absent.md")))
        case("design unreadable", _GOOD, {"DESIGN-UNREADABLE"},
             ("--design", str(d / "absent.md")))
        case("hostile bytes", "\x00\xff" * 200, lambda got: bool(got))

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming passes accepted; a press release, "
          f"{len(_MUTANTS) - 1} single-defect mutants, a missing file, "
          f"unreadable inputs and hostile bytes each rejected by their own "
          f"markers, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S8-5")
    ap.add_argument("path", nargs="?", default=str(DEFAULT))
    ap.add_argument("--pincheck", default=str(PINCHECK))
    ap.add_argument("--design", default=str(DESIGN))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.path), Path(a.pincheck), Path(a.design))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S8-5 gate findings: 1")
        raise SystemExit(1)
