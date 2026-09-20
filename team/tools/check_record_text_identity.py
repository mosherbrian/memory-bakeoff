#!/usr/bin/env python3
"""Record-text identity (U3) — same `M###` id, different record text.

Corvid, R&D pulse 2026-09-13 (coverage-map Layer C class **U3** = the open half
of Muse 3.2; adopted from Assay's validated prototype `5ae37253…`,
`team/ASSAY-U3-RECORD-TEXT-IDENTITY.md`). Layer C had recorded U3 as blocked on
artifacts carrying record-content hashes. Two current sources make it checkable
now:

  * `src/memory_bakeoff/corpus.py` is a canonical `M### -> text` table;
  * reader fixtures carry `- [M###] <text>` context lines.

Findings:
  * `record-text fork: <id>`  — the same id carries >1 distinct text (U3 proper);
  * `record-text drift: <id>` — a text disagrees with the canonical table;
  * `unindexed record text: <id> (advisory)` — id with text but no canonical row
    (generated distractors); suppress with `--no-unindexed`.

Fork/drift exit 1; unindexed is advisory. Missing/unreadable/non-directory
prerequisites are structured, not crashes.

Usage:
  python3 check_record_text_identity.py [roots...] [--canonical SRC]
                                       [--no-unindexed]
  python3 check_record_text_identity.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
DEFAULT_CANONICAL = _REPO / "src" / "memory_bakeoff" / "corpus.py"
DEFAULT_ROOTS = (_REPO,)

LINE_RE = re.compile(r"\s*(?:-\s*)?\[(M\d{3,4})\]\s*(.+)")
CANON_RE = re.compile(r'R\("(M\d{3,4})",\s*"((?:[^"\\]|\\.)*)"')
SCAN_EXT = (".json", ".jsonl", ".csv", ".md", ".txt")
DRIFT_MARKER = "record-text"
TRACEBACK = "Traceback (most recent call last)"


def norm(text: str) -> str:
    return " ".join(text.replace("\\", "").split()).strip().casefold()


def canonical_table(path: Path):
    """Return (id -> normalised text, findings). Structured prerequisites."""
    if not path.is_file():
        return {}, [{"finding": f"missing prerequisite: {path} (canonical table)",
                     "got": "absent"}]
    if not os.access(path, os.R_OK):
        return {}, [{"finding": f"unreadable prerequisite: {path} (canonical table)",
                     "got": "unreadable"}]
    text = path.read_text(encoding="utf-8", errors="replace")
    return {i: norm(t) for i, t in CANON_RE.findall(text)}, []


def _texts_from_string(s: str):
    for line in s.splitlines():
        m = LINE_RE.match(line)
        if m:
            t = " ".join(m.group(2).split()).strip()
            if t:
                yield m.group(1), t


def _walk(obj):
    if isinstance(obj, str):
        yield from _texts_from_string(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def pairs_from_file(path: Path) -> set[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".jsonl":
        out = set()
        for line in raw.splitlines():
            try:
                out |= set(_walk(json.loads(line)))
            except Exception:  # noqa: BLE001
                pass
        return out
    if path.suffix == ".json":
        try:
            return set(_walk(json.loads(raw)))
        except Exception:  # noqa: BLE001
            return set(_texts_from_string(raw))
    return set(_texts_from_string(raw))


def scan(roots: list[Path]):
    """Return (id -> {normalised text: [files]}), unreadable findings."""
    found: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    unreadable: list[dict] = []
    for root in roots:
        for dirpath, _dirs, names in os.walk(root):
            for n in names:
                if not n.endswith(SCAN_EXT):
                    continue
                p = Path(dirpath) / n
                try:
                    for ident, text in pairs_from_file(p):
                        nt = norm(text)
                        rel = str(p)
                        if rel not in found[ident][nt]:
                            found[ident][nt].append(rel)
                except OSError:
                    unreadable.append({"finding": f"unreadable prerequisite: {p}",
                                       "got": "unreadable"})
    return found, unreadable


def check(roots: list[Path], canonical: dict[str, str], report_unindexed: bool = True):
    found, unreadable = scan(roots)
    findings: list[dict] = []
    for ident, texts in sorted(found.items()):
        if len(texts) > 1:
            findings.append({"finding": f"record-text fork: {ident}", "id": ident,
                             "variants": {t: sorted(f)[:4] for t, f in texts.items()}})
            continue
        text = next(iter(texts))
        if ident in canonical:
            if text != canonical[ident]:
                findings.append({
                    "finding": f"record-text drift: {ident}",
                    "id": ident, "file": sorted(texts[text])[0], "got": text[:80],
                    "canonical": canonical[ident][:80]})
        elif report_unindexed:
            findings.append({"finding": f"unindexed record text: {ident} (advisory)",
                             "id": ident, "file": sorted(texts[text])[0]})
    return findings, found, unreadable


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        corpus = root / "corpus.py"
        corpus.write_text('R("M005", "The staging Redis database number is 6.", x)\n'
                          'R("M011", "The build coordinator is strix03.", x)\n')
        canon, pre = canonical_table(corpus)
        assert not pre and set(canon) == {"M005", "M011"}, (pre, canon)

        good = root / "good"
        good.mkdir()
        (good / "a.json").write_text('{"ctx": "- [M005] The staging Redis database number is 6."}')
        assert check([good], canon, True)[0] == [], check([good], canon, True)[0]

        bad = root / "bad"
        bad.mkdir()
        (bad / "a.json").write_text('{"ctx": "- [M005] The staging Redis database number is 6."}')
        (bad / "b.json").write_text('{"ctx": "- [M005] The staging Redis database number is 7."}')
        assert any("record-text fork: M005" in x["finding"]
                   for x in check([bad], canon, True)[0])

        (bad / "b.json").unlink()
        (bad / "a.json").write_text('{"ctx": "- [M005] The staging Redis database number is 9."}')
        assert any("record-text drift: M005" in x["finding"]
                   for x in check([bad], canon, True)[0])

        (bad / "a.json").write_text('{"ctx": "- [M441] distractors are generated elsewhere."}')
        f = check([bad], canon, True)[0]
        assert len(f) == 1 and "unindexed record text: M441" in f[0]["finding"], f
        assert check([bad], canon, False)[0] == []

        # structured prerequisites: missing and directory-at-path canonical
        _, pre = canonical_table(root / "absent.py")
        assert pre and "missing prerequisite" in pre[0]["finding"], pre
        d = root / "adir"
        d.mkdir()
        _, pre = canonical_table(d)
        assert pre and "missing prerequisite" in pre[0]["finding"], pre

        # real CLI on a clean root and a drifted root (the meta-guard's contract)
        cli = root / "cli"
        cli.mkdir()
        (cli / "CLI.json").write_text('{"ctx": "- [M005] The staging Redis database number is 9."}')
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            str(cli), "--canonical", str(corpus)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 1 and TRACEBACK not in r.stdout + r.stderr, \
            (r.returncode, r.stdout[-200:])
        assert "record-text drift: M005" in r.stdout, r.stdout[-300:]
    print("self-test: PASS (clean; fork flagged; table drift flagged; "
          "non-table id advisory and suppressible; missing/directory canonical "
          "structured; real CLI rejects a drift without a traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=[str(r) for r in DEFAULT_ROOTS])
    ap.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    ap.add_argument("--no-unindexed", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    canon, pre = canonical_table(args.canonical.resolve())
    if pre:
        for f in pre:
            print(f"    {f['finding']}")
        return 1
    roots = [Path(r).resolve() for r in args.roots]
    for r in roots:
        if not r.is_dir():
            print(f"    missing prerequisite: {r} (scan root)")
            return 1
    findings, found, unreadable = check(roots, canon,
                                        report_unindexed=not args.no_unindexed)
    hard = [f for f in findings
            if "fork" in f["finding"] or "drift" in f["finding"]]
    checked = sum(1 for ident in found if ident in canon)
    print(f"=== record-text identity: {len(found)} ids with text, "
          f"{checked} checked against {len(canon)} canonical rows")
    for f in findings:
        print(f"    {f['finding']}")
    for u in unreadable:
        print(f"    {u['finding']}")
    print(f"    forks/drifts: {len(hard)}, unindexed: "
          f"{len([f for f in findings if 'unindexed' in f['finding']])}, "
          f"unreadable: {len(unreadable)}")
    return 1 if (hard or unreadable) else 0


if __name__ == "__main__":
    raise SystemExit(main())
