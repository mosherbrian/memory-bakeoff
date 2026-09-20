#!/usr/bin/env python3
"""Identifier lifecycle — a superseded/withdrawn id must not be cited as current.

Corvid, R&D pulse 2026-09-13 (coverage-map Layer C gap **U4** = Muse batch 3 item
3.4). Guards 4/5 check ID shape and query referents; guard 1 checks invalidated
*run* directories. None checks whether a document cites an identifier the record
has since superseded or withdrawn, so a reader can act on a stale ID.

The lifecycle is **declared**, never inferred: `team/IDENTIFIER-LIFECYCLE.txt`
lists each `superseded: <old> -> <new...>` / `withdrawn: <id>` move and names
the authoritative source for it. For every citation of a tracked id in a scanned
Markdown file, the guard requires a supersession cue on the same line or within
3 lines; otherwise it is a finding. Append-only operation records (`log:`) and
the guards' own mechanism docs (`skip:`) are declared out. The index file is the
only source of truth — the guard does not read the ledger.

Exit 1 when an uncued citation remains, so it can serve as a closure gate;
`--advisory` reports without failing. Missing / unreadable / malformed index is a
structured prerequisite, not a clean tree, per the suite dialect.

Two declared-list hygiene checks (Muse batch 6, coverage-map U6/U7) guard the
list itself, not just the citations: a scan with **zero non-exempt Markdown
files** is a `vacuous scan` instrument failure (U6), and a `log:`/`skip:` entry
matching **no scanned file** is an `inert declared-list entry` (U7). Neither is
suppressed by `--advisory`. With `--ledger FILE`, an optional cross-check (U9)
reads the claims ledger's `SUPERSEDED` table rows and fails if one of their id
moves is absent from the index; the default run stays hermetic and never reads
the ledger for citations.

Usage:
  python3 check_identifier_lifecycle.py [roots...] [--index FILE]
                                        [--ledger CLAIMS-LEDGER.md] [--advisory]
  python3 check_identifier_lifecycle.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
_IMPL = _REPO.parent
DEFAULT_INDEX = _IMPL.parent / "team" / "IDENTIFIER-LIFECYCLE.txt"
DEFAULT_ROOTS = (_REPO, _IMPL.parent / "team")

# A cue that the citation itself is about the lifecycle move. `superseded` /
# `withdrawn` / `replaced by` are unambiguous wherever they appear in the window.
# A bare `split` is not: it is the corpus's dominant benchmark term ("split
# unspecified", "oracle split"), so it cues only when the same line also names
# the lifecycle subject -- otherwise a stale citation sitting inside a
# LongMemEval split discussion would be silently regarded as cued (Alice's
# controlled pair, 2026-09-13). There is deliberately no whole-file banner rule:
# the audit's own thread title says "retracted-figure", which would cue every
# citation in the file.
STRONG_CUE_RE = re.compile(r"supersed|withdraw|no longer current|replaced by", re.I)
WEAK_CUE_RE = re.compile(r"\bsplit", re.I)
# A genuine lifecycle-split phrase, or `split` next to a ledger/lifecycle subject.
# The cited id, its `L-HS` prefix, and the generic `row`/`id`/`identifier` words
# are NOT subjects -- the citation's own context supplies them, which would make
# the cue self-satisfiable (Alice's rev-3 residual, 2026-09-13). A named
# replacement id on the line does count.
_SPLIT_PHRASE_RE = re.compile(r"L-HS\s+split", re.I)
_SPLIT_SUBJECT_RE = re.compile(r"ledger|lifecycle", re.I)
NEARBY = 3


def load_index(path: Path):
    """Return (superseded, withdrawn, logs, skips, findings)."""
    if not path.is_file():
        return {}, set(), set(), set(), [
            {"finding": f"missing prerequisite: {path}", "got": "absent"}]
    if not os.access(path, os.R_OK):
        return {}, set(), set(), set(), [
            {"finding": f"unreadable prerequisite: {path}", "got": "unreadable"}]
    sup: dict[str, list[str]] = {}
    wd: set[str] = set()
    logs: set[str] = set()
    skips: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("superseded:"):
            body = s[len("superseded:"):].strip()
            if "->" not in body:
                return {}, set(), set(), set(), [
                    {"finding": f"malformed lifecycle row: {s}", "got": "malformed"}]
            old, new = body.split("->", 1)
            repl = [x.strip() for x in new.split(",") if x.strip()]
            if not old.strip() or not repl:
                return {}, set(), set(), set(), [
                    {"finding": f"malformed lifecycle row: {s}", "got": "malformed"}]
            sup[old.strip()] = repl
        elif s.startswith("withdrawn:"):
            ident = s[len("withdrawn:"):].strip()
            if not ident:
                return {}, set(), set(), set(), [
                    {"finding": f"malformed lifecycle row: {s}", "got": "malformed"}]
            wd.add(ident)
        elif s.startswith("log:"):
            logs.add(Path(s[len("log:"):].strip()).name)
        elif s.startswith("skip:"):
            skips.add(Path(s[len("skip:"):].strip()).name)
        else:
            return {}, set(), set(), set(), [
                {"finding": f"malformed lifecycle row: {s}", "got": "malformed"}]
    if not sup and not wd:
        return {}, set(), set(), set(), [
            {"finding": f"malformed lifecycle index: {path} (no lifecycle rows)",
             "got": "malformed"}]
    return sup, wd, logs, skips, []


def _pattern(ident: str) -> re.Pattern:
    # Word/path boundaries so `L-HS-02` does not match inside `L-HS-02a`.
    return re.compile(r"(?<![\w-])" + re.escape(ident) + r"(?![\w-])")


def _cued_line(line: str, ident: str, replacements=()) -> bool:
    """True if this line declares the tracked id's lifecycle move."""
    if STRONG_CUE_RE.search(line):
        return True
    if not WEAK_CUE_RE.search(line):
        return False
    # `split` is the corpus's benchmark word too. Accept the anchored lifecycle
    # phrase, a named replacement id, or `split` near a ledger/lifecycle subject
    # -- but never the cited id or the generic row/id words, or a same-line
    # "L-HS-02 row ... (split unspecified)" would cue itself (Alice's residuals).
    if _SPLIT_PHRASE_RE.search(line):
        return True
    stripped = _pattern(ident).sub(" ", line)
    stripped = re.sub(r"\bL-HS\b", " ", stripped, flags=re.I)
    if _SPLIT_SUBJECT_RE.search(stripped):
        return True
    return any(_pattern(r).search(line) for r in replacements)


def ledger_superseded(path: Path):
    """Return (superseded_ids, findings) from a claims-ledger Markdown table.

    U9 (Muse 6.5c): only table rows whose cells carry `SUPERSEDED` are read; the
    row's first cell is the old id. Prose back-references, class labels and
    process notes are ignored (Alice's U9 parse constraint: the ledger's
    `supersed` surface is mostly not an id move).
    """
    if not path.is_file():
        return set(), [{"finding": f"missing prerequisite: {path} (ledger)", "got": "absent"}]
    if not os.access(path, os.R_OK):
        return set(), [{"finding": f"unreadable prerequisite: {path} (ledger)", "got": "unreadable"}]
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not any("SUPERSEDED" in c for c in cells):
            continue
        old = re.sub(r"[`*~]", "", cells[0]).strip()
        if old:
            ids.add(old)
    return ids, []


def scan(root: Path, sup: dict, wd: set, logs: set, skips: set, index: Path):
    """Return (citations, findings, unreadable, seen).

    `seen` is the set of scanned `*.md` basenames across the root; the caller
    uses it for the declared-list hygiene checks (Muse 6.2/6.3, U6/U7).
    """
    tracked = {i: ("superseded", sup[i]) for i in sup}
    tracked.update({i: ("withdrawn", []) for i in wd if i not in tracked})
    pats = {i: _pattern(i) for i in tracked}
    citations: list[dict] = []
    unreadable: list[dict] = []
    seen: set[str] = set()
    if not root.is_dir():
        return citations, [
            {"finding": f"missing prerequisite: {root} (scan root)", "got": "absent"}], unreadable, seen
    for md in sorted(root.rglob("*.md")):
        if not md.is_file():
            continue
        if md.resolve() == index.resolve():
            continue
        seen.add(md.name)
        if md.name in skips:
            continue
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            unreadable.append({"finding": f"unreadable prerequisite: {md}", "got": "unreadable"})
            continue
        for i, line in enumerate(lines):
            for ident, (kind, repl) in tracked.items():
                if not pats[ident].search(line):
                    continue
                window = lines[max(0, i - NEARBY): i + NEARBY + 1]
                cued = any(_cued_line(x, ident, repl) for x in window)
                citations.append({
                    "file": str(md.relative_to(root)),
                    "line": i + 1,
                    "id": ident,
                    "kind": kind,
                    "replacements": repl,
                    "cued": cued or (md.name in logs),
                    "text": line.strip()[:160],
                })
    return citations, [], unreadable, seen


def self_test() -> int:
    """Reject a representative bad input of each class through the real path."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        index = root / "INDEX.txt"
        index.write_text(
            "superseded: L-HS-02 -> L-HS-02a, L-HS-02b\n"
            "withdrawn: L-OLD-01\n"
            "log: LOG.md\n")
        (root / "DOC.md").write_text(
            "The class for L-HS-02 is contradicted.\n")
        (root / "CUED.md").write_text(
            "L-HS-02 was superseded and split into L-HS-02a / L-HS-02b.\n")
        (root / "LOG.md").write_text("L-HS-02 stays contradicted.\n")
        (root / "WD.md").write_text("See L-OLD-01 for the old table.\n")
        (root / "OK.md").write_text("L-HS-02a and L-HS-02b are current.\n")
        # Alice's controlled pair (2026-09-13): a benchmark "split" line two lines
        # above a stale citation must NOT cue it, while a genuine lifecycle split
        # phrase must. Only the cue line differs between the two.
        (root / "NEAR_SPLIT.md").write_text(
            "LongMemEval (split unspecified) results follow.\n"
            "\n"
            "The class for L-HS-02 is contradicted.\n")
        (root / "GENUINE_SPLIT.md").write_text(
            "See the L-HS split below.\n"
            "\n"
            "The class for L-HS-02 is the old one.\n")
        # Alice's rev-2 residual: a benchmark `split` on the citation's OWN line
        # must not cue it via the cited id.
        (root / "SAME_LINE.md").write_text(
            "The class for L-HS-02 (LongMemEval split unspecified) is contradicted.\n")
        # Alice's rev-3 residual: a generic row/id word must not make the cue
        # self-satisfiable. A named replacement id on the cue line still does.
        (root / "SELF_SUBJECT.md").write_text(
            "The L-HS-02 row gives LongMemEval (split unspecified) as current.\n")
        (root / "REPL_CUE.md").write_text(
            "Split into L-HS-02a / L-HS-02b.\n"
            "\n"
            "The class for L-HS-02 is the old one.\n")

        sup, wd, logs, skips, pre = load_index(index)
        assert not pre, pre
        assert sup == {"L-HS-02": ["L-HS-02a", "L-HS-02b"]}, sup
        assert wd == {"L-OLD-01"}, wd

        citations, findings, unreadable, seen = scan(root, sup, wd, logs, skips, index)
        uncued = sorted({(c["file"], c["id"]) for c in citations if not c["cued"]})
        assert uncued == [("DOC.md", "L-HS-02"),
                          ("NEAR_SPLIT.md", "L-HS-02"),
                          ("SAME_LINE.md", "L-HS-02"),
                          ("SELF_SUBJECT.md", "L-HS-02"),
                          ("WD.md", "L-OLD-01")], uncued
        # The cued citations, the log-declared citation, the genuine split phrase
        # and the suffixed replacements must not be findings.
        cited = {(c["file"], c["id"]) for c in citations}
        assert ("OK.md", "L-HS-02") not in cited
        assert any(c["file"] == "GENUINE_SPLIT.md" and c["id"] == "L-HS-02"
                   and c["cued"] for c in citations), citations
        assert any(c["file"] == "REPL_CUE.md" and c["id"] == "L-HS-02"
                   and c["cued"] for c in citations), citations
        assert not findings and not unreadable, (findings, unreadable)
        # U7 (Muse 6.2): every declared log/skip basename resolves to a file.
        assert not ((logs | skips) - seen), (logs, skips, seen)
        # U6 (Muse 6.1): a root whose only file is skipped has an empty
        # non-exempt denominator -- the vacuous pass.
        with tempfile.TemporaryDirectory() as td2:
            r2 = Path(td2)
            (r2 / "ONLY.md").write_text("x\n", encoding="utf-8")
            idx2 = r2 / "I.txt"
            idx2.write_text("superseded: A -> B\nskip: ONLY.md\n", encoding="utf-8")
            s2, w2, l2, k2, pre2 = load_index(idx2)
            assert not pre2, pre2
            _, _, _, seen2 = scan(r2, s2, w2, l2, k2, idx2)
            assert not {n for n in seen2 if n not in k2}, seen2
        # U6 + U7 through the real CLI: vacuous scan + inert entry -> rc 1.
        with tempfile.TemporaryDirectory() as td3:
            r3 = Path(td3)
            (r3 / "ONLY.md").write_text("x\n", encoding="utf-8")
            idx3 = r3 / "I.txt"
            idx3.write_text("superseded: A -> B\nskip: ONLY.md\nlog: GONE.md\n",
                            encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), str(r3),
                 "--index", str(idx3)],
                capture_output=True, text=True, timeout=120)
            assert r.returncode == 1, (r.returncode, r.stdout[-200:])
            assert "vacuous scan" in r.stdout, r.stdout[-300:]
            assert "inert declared-list entry: GONE.md" in r.stdout, r.stdout[-300:]

    # U9: ledger SUPERSEDED table rows cross-checked against the index.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ledger = root / "LG.md"
        ledger.write_text(
            "| id | claim | evidence | class |\n|---|---|---|---|\n"
            "| L-NEW-01 | a claim | source | ~~old~~ **SUPERSEDED — see split: L-NEW-01a** |\n"
            "| L-NEW-02 | a label | source | `vendor-only` (supersedes a label) |\n"
            "Prose: this superseded the old value.\n", encoding="utf-8")
        ids, pre = ledger_superseded(ledger)
        assert ids == {"L-NEW-01"}, ids  # table-row id move only, not label/prose
        assert not pre, pre
        _, pre2 = ledger_superseded(root / "absent.md")
        assert pre2 and "missing prerequisite" in pre2[0]["finding"], pre2
        idx = root / "I.txt"
        idx.write_text("superseded: A -> B\n", encoding="utf-8")
        (root / "DOC.md").write_text("nothing tracked here\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), str(root),
             "--index", str(idx), "--ledger", str(ledger)],
            capture_output=True, text=True, timeout=120)
        assert r.returncode == 1 and \
            "ledger supersession missing from index: L-NEW-01" in r.stdout, \
            (r.returncode, r.stdout[-300:])
        idx.write_text("superseded: L-NEW-01 -> L-NEW-01a\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), str(root),
             "--index", str(idx), "--ledger", str(ledger)],
            capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, (r.returncode, r.stdout[-300:])

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _, _, _, _, pre = load_index(root / "absent.txt")
        assert pre and "missing prerequisite" in pre[0]["finding"], pre
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bad = root / "INDEX.txt"
        bad.write_text("garbage row\n")
        _, _, _, _, pre = load_index(bad)
        assert pre and "malformed" in pre[0]["finding"], pre
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "INDEX.txt"
        p.write_text("superseded: A -> B\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            _, _, _, _, pre = load_index(p)
            assert pre and "unreadable prerequisite" in pre[0]["finding"], pre
        os.chmod(p, 0o644)
    print("self-test: PASS (uncued superseded + withdrawn citations flagged; a "
          "benchmark `split` does not cue a stale citation -- separate line, the "
          "citation's own line, or a generic row/id context -- while the anchored "
          "`L-HS split` phrase and a named replacement id do; cue, log and "
          "suffixed replacement clean; a vacuous zero-denominator scan and an "
          "inert declared-list entry are flagged through the real CLI; a ledger "
          "SUPERSEDED row absent from the index is flagged via --ledger; "
          "malformed, missing and unreadable index reported)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=[str(r) for r in DEFAULT_ROOTS])
    ap.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    ap.add_argument("--ledger", type=Path, default=None,
                    help="cross-check the index against a claims-ledger table "
                         "(U9): a SUPERSEDED row id absent from the index fails")
    ap.add_argument("--advisory", action="store_true",
                    help="report findings but exit 0 (non-gating census)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    index = args.index.resolve()
    sup, wd, logs, skips, pre = load_index(index)
    if pre:
        for f in pre:
            print(f"    {f['finding']}")
        return 1

    rc = 0
    hard_fail = False
    seen_all: set[str] = set()
    for raw in args.roots:
        root = Path(raw).resolve()
        citations, pre, unreadable, seen = scan(root, sup, wd, logs, skips, index)
        if pre:
            for f in pre:
                print(f"    {f['finding']}")
            hard_fail = True
            continue
        seen_all |= seen
        uncued = [c for c in citations if not c["cued"]]
        print(f"=== {root}\n    tracked_ids={len(sup) + len(wd)}  "
              f"citations={len(citations)}  uncued={len(uncued)}")
        for c in citations:
            tag = "cued    " if c["cued"] else "UNCUED-ID"
            repl = f" -> {', '.join(c['replacements'])}" if c["replacements"] else ""
            print(f"    [{tag}] {c['file']}:{c['line']}  {c['id']} "
                  f"({c['kind']}{repl})")
        for u in unreadable:
            print(f"    {u['finding']}")
        if uncued or unreadable:
            rc = 1

    # U6 (Muse 6.1): a declared-list guard that scanned zero non-exempt inputs
    # cannot support a clean report -- a vacuous pass is an instrument failure.
    non_exempt = {n for n in seen_all if n not in skips}
    if not non_exempt:
        print(f"    vacuous scan: 0 non-exempt Markdown files scanned "
              f"({len(seen_all)} seen, {len(skips)} declared skip basenames)")
        hard_fail = True
    # U7 (Muse 6.2): a declared log/skip entry matching no scanned file is a
    # silent hole (or a stale false positive) -- report it by name.
    inert = sorted({n for n in (logs | skips)} - seen_all)
    for name in inert:
        print(f"    inert declared-list entry: {name} (no scanned file)")
    if inert:
        rc = 1

    # U9 (Muse 6.5c): a `SUPERSEDED` id move recorded in the claims ledger but
    # absent from the index is a completeness hole -- an unlisted old id stays
    # citable as current. Only run when a ledger is declared (the guard's
    # default stays hermetic and does not read the ledger for citations).
    if args.ledger is not None:
        ledger = args.ledger.resolve()
        ledger_ids, ledger_pre = ledger_superseded(ledger)
        if ledger_pre:
            for f in ledger_pre:
                print(f"    {f['finding']}")
            hard_fail = True
        else:
            absent = sorted(ledger_ids - set(sup) - wd)
            for ident in absent:
                print(f"    ledger supersession missing from index: {ident}")
            if absent:
                rc = 1

    if hard_fail:
        return 1  # an instrument failure is never suppressed by --advisory
    return 0 if args.advisory else rc


if __name__ == "__main__":
    raise SystemExit(main())
