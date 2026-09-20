#!/usr/bin/env python3
"""Orphan-evidence census: completed runs that no Markdown cites.

Corvid, R&D pulse 2026-09-13 (instantiates coverage-map gap U1 and Muse batch-4
ACCEPT 4.3). The three link/value checkers go citation -> artifact; this is the
inverse: a `results/<dir>` that holds a completed measurement
(`summary.csv` or `run.json`) but is named by **no** Markdown in the declared
citation roots. An uncited run is where a contradicting or invalidated result
can sit unnoticed.

Self-citation is excluded: Markdown **inside** a `results/` subtree does not
count as a citation of the run it describes. Citations may be links or plain
mentions of the directory name.

This is a **census / advisory** by default (exit 0) because prototype and probe
directories are legitimately uncited; `--fail` turns it into a gate, and an
allowlist file (one directory name per line, `#` comments) records intentional
exceptions.

Usage:
  python3 check_orphan_evidence.py <results-root> [--cite DIR ...]
        [--allowlist FILE] [--since-days N] [--fail]
  python3 check_orphan_evidence.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

COMPLETED = ("summary.csv", "run.json")


def _say(*a) -> None:
    print(*a)


def _md_text_outside_results(cite_roots: list[Path]) -> str:
    chunks: list[str] = []
    for root in cite_roots:
        if not root.exists():
            continue
        for md in root.rglob("*.md"):
            rel = md.relative_to(root)
            if "results" in rel.parts[:1]:  # skip the results subtree (self-citation)
                continue
            if md.is_file():
                try:
                    chunks.append(md.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue
    return "\n".join(chunks)


def completed_runs(results_root: Path, since_days: float = 0) -> list[Path]:
    results = results_root / "results"
    if not results.is_dir():
        return []
    now = time.time()
    out = []
    for d in sorted(results.iterdir()):
        if not d.is_dir():
            continue
        if not any((d / f).is_file() for f in COMPLETED):
            continue
        if since_days and (now - d.stat().st_mtime) < since_days * 86400:
            continue  # inside the grace window
        out.append(d)
    return out


FAMILY_RE = re.compile(r"[-_]r\d+$", re.I)


def _family(name: str) -> str:
    """Base name with a trailing replicate suffix removed (`x-r2` -> `x`)."""
    return FAMILY_RE.sub("", name)


def _cited(corpus: str, name: str) -> bool:
    # Boundary match, not a substring: `core4` must not be "cited" by
    # "core40" or "hardcore4fun" (Alice's false-negative finding), while a
    # path link `results/core4` and a bare `` `core4` `` mention both count.
    return re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", corpus) is not None


def classify(results_root: Path, cite_roots: list[Path], allow: set[str],
             since_days: float = 0) -> list[dict]:
    """Return `[{name, family, kind}]` for every uncited completed run.

    `kind` is `replica_of_cited` when another directory in the same replicate
    family (or the family base) is cited, else `distinct`. This is reporting
    only: nothing is suppressed, so a reviewer sees which orphans are
    replicates of a cited run and which are entirely uncited families.
    """
    corpus = _md_text_outside_results(cite_roots)
    dirs = completed_runs(results_root, since_days)
    status = {d.name: _cited(corpus, d.name) for d in dirs}
    out: list[dict] = []
    for d in dirs:
        if d.name in allow or status[d.name]:
            continue
        fam = _family(d.name)
        siblings = [n for n, cited in status.items() if n != d.name and _family(n) == fam]
        replica = bool(siblings) and any(status[s] for s in siblings)
        out.append({"name": d.name, "family": fam,
                    "kind": "replica_of_cited" if replica else "distinct"})
    return out


def orphans(results_root: Path, cite_roots: list[Path], allow: set[str],
            since_days: float = 0) -> list[str]:
    return [r["name"] for r in classify(results_root, cite_roots, allow, since_days)]


def _allowlist(path: Path | None) -> set[str]:
    if path is None or not path.is_file():
        return set()
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name in ("cited_run", "orphan_run", "probe_only", "core4"):
            (root / "results" / name).mkdir(parents=True)
        (root / "results" / "cited_run" / "summary.csv").write_text("provider,hit@5\ne,0.5\n")
        (root / "results" / "orphan_run" / "summary.csv").write_text("provider,hit@5\ne,0.4\n")
        (root / "results" / "orphan_run" / "summary.md").write_text("self summary only\n")
        (root / "results" / "probe_only" / "notes.txt").write_text("no completed artifact\n")
        (root / "results" / "core4" / "summary.csv").write_text("provider,hit@5\ne,0.3\n")
        (root / "INDEX.md").write_text("see results/cited_run for the number\n"
                                       "and core40 and hardcore4fun are unrelated\n")

        got = orphans(root, [root], set())
        assert set(got) == {"orphan_run", "core4"}, got  # core4 not "cited" by core40

        # An allowlist records intentional exceptions.
        assert set(orphans(root, [root], {"orphan_run", "core4"})) == set()
        # A name cited as a plain mention counts.
        (root / "EXTRA.md").write_text("orphan_run is discussed here\n")
        assert set(orphans(root, [root], set())) == {"core4"}, orphans(root, [root], set())

        # Missing results dir -> caller reports it.
        with tempfile.TemporaryDirectory() as td2:
            assert completed_runs(Path(td2)) == []

    # An explicit --allowlist path that does not exist is structured, not silent.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "results" / "r").mkdir(parents=True)
        (root / "results" / "r" / "summary.csv").write_text("provider,hit@5\ne,0.5\n")
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(root),
                            "--allowlist", str(root / "nope.txt")],
                           capture_output=True, text=True)
        blob = r.stdout + r.stderr
        assert r.returncode == 1 and "missing prerequisite" in blob, (r.returncode, blob[-200:])

    # Replica-of-cited is distinguished from a fully-uncited family.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name in ("fam-r1", "fam-r2", "lonely"):
            (root / "results" / name).mkdir(parents=True)
            (root / "results" / name / "summary.csv").write_text("provider,hit@5\ne,0.5\n")
        (root / "NOTE.md").write_text("see results/fam-r1\n")
        kinds = {r["name"]: r["kind"] for r in classify(root, [root], set())}
        assert kinds == {"fam-r2": "replica_of_cited", "lonely": "distinct"}, kinds
    print("self-test: PASS (uncited run found; self-citation excluded; boundary match "
          "rejects core40/hardcore4; allowlist/mention suppress; replica-of-cited vs "
          "distinct; missing allowlist structured; non-completed dirs ignored)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_root", nargs="?", default=".")
    ap.add_argument("--cite", action="append", default=[],
                    help="citation roots to scan for mentions (repeatable)")
    ap.add_argument("--allowlist", default=None,
                    help="file of intentionally-uncited dir names (one per line)")
    ap.add_argument("--since-days", type=float, default=0.0,
                    help="ignore completed runs modified within N days (grace)")
    ap.add_argument("--fail", action="store_true", help="exit 1 if any orphan")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    root = Path(args.results_root).resolve()
    if not (root / "results").is_dir():
        print(f"missing prerequisite: {root / 'results'}")
        return 1
    cite = [Path(c).resolve() for c in args.cite] or [root]
    allow_path = Path(args.allowlist).resolve() if args.allowlist else None
    if allow_path is not None:
        if not allow_path.is_file():
            print(f"missing prerequisite: {allow_path}")
            return 1
        if not os.access(allow_path, os.R_OK):
            print(f"unreadable prerequisite: {allow_path}")
            return 1
    allow = _allowlist(allow_path)
    try:
        rows = classify(root, cite, allow, args.since_days)
    except OSError as exc:
        print(f"unreadable prerequisite: {exc}")
        return 1
    n_replica = sum(1 for r in rows if r["kind"] == "replica_of_cited")
    n_distinct = len(rows) - n_replica
    print(f"=== {root}\n    completed runs scanned: {len(completed_runs(root, args.since_days))}"
          f"  orphan (uncited): {len(rows)}  [replica_of_cited {n_replica}, distinct {n_distinct}]")
    for r in rows:
        tag = "ORPHAN-REPLICA" if r["kind"] == "replica_of_cited" else "ORPHAN"
        print(f"    [{tag}] results/{r['name']}")
    return 1 if (args.fail and rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
