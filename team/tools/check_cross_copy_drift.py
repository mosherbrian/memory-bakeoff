#!/usr/bin/env python3
"""Cross-copy policy drift — duplicated-canonical drift across repo checkouts.

Corvid, R&D pulse 2026-09-13 (coverage-map gap U5 / Muse 4.2, following Alice's
`ALICE-U5-CANONICAL-DRIFT-AUDIT.md`). The same policy/index file exists in
several repo checkouts; when they drift, a guard run in one tree can report a
different state than the same guard in another. This is the general class behind
the AGENTS/`KNOWN_FAILURES` mismatch.

It compares a declared file list across the known checkouts. Drift is reported
per file with each tree's hash; a file missing from a tree is a finding too.
The tree set comes from the declaration's `tree:` lines, and every `repo*`
checkout under `implementer/` missing from that list is an `undeclared tree:`
finding (U8 / Muse 6.5a), so a new fork cannot silently go uncompared; a declared
tree that has gone is a `declared tree missing:` finding.
Advisory by default (live drift exists and is owned by Kiln/GiLMore), `--fail`
turns it into a gate; the canonical tree and the shared list are declared in
`team/REPO-CANONICAL.txt`.

Usage:
  python3 check_cross_copy_drift.py                 # census, advisory rc 0
  python3 check_cross_copy_drift.py --fail          # rc 1 on any drift/gap
  python3 check_cross_copy_drift.py --trees A B --files X Y --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
_IMPL = _REPO.parent
DEFAULT_TREES = (_REPO, _IMPL / "repo", _IMPL / "repo-glm-dsh2")
DEFAULT_FILES = ("AGENTS.md", "tests/KNOWN_FAILURES.json", "RESULTS.md",
                 "README.md", "DECISION_MEMO.md", "STATUS_AND_FINDINGS.md")
DEFAULT_DECLARATION = _IMPL.parent / "team" / "REPO-CANONICAL.txt"


def _hash(path: Path):
    if not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    except OSError:
        return "UNREADABLE"


def _read_declaration(path: Path):
    """Return (shared_files, known_drift, trees, canonical_only, canonical_rel,
    findings) from REPO-CANONICAL.txt.

    The declaration is the guard's source of truth for which files are shared
    across copies, which drifts are already owned (Assay second-seat,
    2026-09-13), which checkout trees are in scope (`tree:` lines; Corvid, U8),
    and which files are present in the canonical tree **by design** and expected
    absent elsewhere (`canonical-only:`; Muse batch-9 ACCEPT 4, so expected
    absence is not permanently reported as drift).
    """
    if not path.is_file():
        return None, set(), [], [], None, [{"finding": f"missing prerequisite: {path}", "got": "absent"}]
    if not os.access(path, os.R_OK):
        return None, set(), [], [], None, [{"finding": f"unreadable prerequisite: {path}", "got": "unreadable"}]
    files, known, trees, canonical_only = [], set(), [], []
    canonical_rel = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("shared:"):
            rel = s.split(":", 1)[1].strip()
            if rel:
                files.append(rel)
        elif s.startswith("canonical-only:"):
            rel = s.split(":", 1)[1].strip()
            if rel:
                canonical_only.append(rel.split()[0])
        elif s.startswith("known-drift:"):
            rest = s.split(":", 1)[1].strip()
            if rest:
                known.add(rest.split()[0])
        elif s.startswith("tree:"):
            rest = s.split(":", 1)[1].strip()
            if rest:
                trees.append(rest.split()[0])  # drop the inline role note
                if "[canonical]" in rest:
                    canonical_rel = rest.split()[0]
    return files, known, trees, canonical_only, canonical_rel, []


def canonical_only_findings(trees: list[Path], canonical: Path | None,
                            files: list[str]) -> list[dict]:
    """Muse batch-9 ACCEPT 4: a `canonical-only:` path is present in the
    canonical tree by design and expected **absent** in every other tree, so its
    absence is not drift. Findings are the two violation modes: missing from the
    canonical tree, or present in a non-canonical tree. If `canonical-only:`
    lines exist with no `[canonical]` tree marker, that is a declaration error.
    """
    out: list[dict] = []
    if files and canonical is None:
        return [{"finding": "canonical-only declared but no [canonical] tree marker",
                 "trees": [t.name for t in trees]}]
    for rel in files:
        for t in trees:
            present = (t / rel).is_file()
            if canonical is not None and t.resolve() == canonical.resolve():
                if not present:
                    out.append({"finding": f"canonical-only path missing from the canonical tree: {rel}",
                                "trees": [t.name]})
            elif present:
                out.append({"finding": f"canonical-only path present in a non-canonical tree: {rel}",
                            "trees": [t.name]})
    return out


def tree_gaps(declared: list[Path], impl_dir: Path):
    """U8 (Muse 6.5a): checkouts on disk vs the declared tree list.

    Returns (discovered, undeclared, missing). Discovery is `implementer/repo*`
    directories, so a new fork cannot silently go uncompared just because it is
    absent from a hardcoded tuple.
    """
    discovered = sorted(p.resolve() for p in impl_dir.glob("repo*") if p.is_dir())
    declared_set = {p.resolve() for p in declared}
    undeclared = [p for p in discovered if p not in declared_set]
    missing = [p for p in declared if not p.is_dir()]
    return discovered, undeclared, missing


def check(trees: list[Path], files: list[str]) -> list[dict]:
    out: list[dict] = []
    for rel in files:
        hashes = {t.name: _hash(t / rel) for t in trees}
        unreadable = [n for n, h in hashes.items() if h == "UNREADABLE"]
        if unreadable:
            out.append({"finding": f"unreadable in a tree: {rel}", "trees": unreadable})
        distinct = {h for h in hashes.values() if h not in (None, "UNREADABLE")}
        missing = [n for n, h in hashes.items() if h is None]
        if missing:
            out.append({"finding": f"missing in a tree: {rel}", "trees": missing})
        if len(distinct) > 1:
            detail = ", ".join(f"{n}={h}" for n, h in sorted(hashes.items()))
            out.append({"finding": f"cross-copy drift: {rel}", "hashes": detail})
    return out


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        a, b = root / "a", root / "b"
        for t in (a, b):
            (t / "tests").mkdir(parents=True)
        (a / "AGENTS.md").write_text("same\n")
        (b / "AGENTS.md").write_text("same\n")
        (a / "tests" / "K.json").write_text("{}\n")
        (b / "tests" / "K.json").write_text("{}\n")
        assert check([a, b], ["AGENTS.md", "tests/K.json"]) == [], check([a, b], ["AGENTS.md", "tests/K.json"])
        (b / "tests" / "K.json").write_text('{"x":1}\n')
        f = check([a, b], ["AGENTS.md", "tests/K.json"])
        assert len(f) == 1 and "cross-copy drift" in f[0]["finding"], f
        # a file missing from one tree is a finding
        f = check([a, b], ["NOPE.md"])
        assert any("missing in a tree" in x["finding"] for x in f), f
        # U8: checkout discovery against the declared tree list
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            impl = base / "implementer"
            impl.mkdir()
            for n in ("repo-a", "repo-b", "repo-new"):
                (impl / n).mkdir()
            declared = [(impl / "repo-a").resolve(), (impl / "repo-b").resolve()]
            disc, undeclared, missing = tree_gaps(declared, impl)
            assert [p.name for p in disc] == ["repo-a", "repo-b", "repo-new"], disc
            assert [p.name for p in undeclared] == ["repo-new"], undeclared
            assert missing == [], missing
            _, _, missing = tree_gaps(declared + [(impl / "repo-gone").resolve()], impl)
            assert [p.name for p in missing] == ["repo-gone"], missing
        # Muse batch-9 ACCEPT 4: canonical-only presence (expected absence)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            can, fork = root / "repo", root / "repo-dsh"
            can.mkdir(); fork.mkdir()
            (can / "P2.py").write_text("x\n")
            assert canonical_only_findings([can, fork], can, ["P2.py"]) == [], \
                "expected absence of a canonical-only file false-alarmed"
            (fork / "P2.py").write_text("x\n")
            f = canonical_only_findings([can, fork], can, ["P2.py"])
            assert len(f) == 1 and "non-canonical" in f[0]["finding"], f
            (can / "P2.py").unlink()
            f = canonical_only_findings([can, fork], can, ["P2.py"])
            assert any("missing from the canonical" in x["finding"] for x in f), f
            assert canonical_only_findings([can], None, ["P2.py"]), \
                "declared canonical-only with no [canonical] marker not flagged"
    print("self-test: PASS (identical trees clean; drift flagged; missing file "
          "flagged; an undeclared checkout and a declared-but-absent tree are "
          "flagged; canonical-only presence/absence and declaration errors are "
          "flagged)")
    return 0


def _disp(base: Path, p: Path) -> str:
    try:
        return str(p.relative_to(base))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trees", nargs="*", default=None,
                    help="explicit trees; default: the declaration's `tree:` lines")
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--declaration", type=Path, default=DEFAULT_DECLARATION)
    ap.add_argument("--fail", action="store_true", help="exit 1 on any drift")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    base = _IMPL.parent
    known = set()
    discovery: list[dict] = []
    co_only: list[str] = []
    canonical_tree = None
    if args.trees:
        trees = [Path(t).resolve() for t in args.trees]
        files = args.files or list(DEFAULT_FILES)
        for t in trees:
            if not t.is_dir():
                print(f"missing prerequisite: {t} (tree)")
                return 1
    else:
        shared, known, trees_rel, co_only, canonical_rel, pre = _read_declaration(args.declaration)
        if pre:
            print(pre[0]["finding"])
            return 1
        if not trees_rel:
            # U8 (Muse 6.5a / Alice second-seat; v2 closes the applied-check
            # residual): a declaration with no `tree:` lines is a misconfigured
            # scope, not a default. v1 only caught a `shared:`-only declaration,
            # so an empty/comment-only one still fell back to
            # DEFAULT_TREES+DEFAULT_FILES with discovery skipped, rc 0. Fail
            # loud, like U6's vacuous scan, not an advisory.
            print("no declared tree set: declaration has no `tree:` lines; "
                  "refusing to fall back to DEFAULT_TREES")
            return 1
        files = args.files or shared or list(DEFAULT_FILES)
        declared = [(_IMPL.parent / rel).resolve() if not Path(rel).is_absolute()
                    else Path(rel).resolve() for rel in trees_rel]
        trees = declared or [Path(t).resolve() for t in DEFAULT_TREES]
        if canonical_rel:
            canonical_tree = (_IMPL.parent / canonical_rel).resolve()
        if declared:
            # U8 (Muse 6.5a): a checkout on disk absent from the declaration
            # would silently go uncompared; a declared tree that is gone is a
            # stale scope entry.
            _, undeclared, gone = tree_gaps(declared, _IMPL)
            for p in undeclared:
                discovery.append({"finding": f"undeclared tree: {_disp(base, p)}"})
            for p in gone:
                discovery.append({"finding": f"declared tree missing: {_disp(base, p)}"})

    findings = check(trees, files)
    for f in findings:
        if f["finding"].startswith("cross-copy drift: "):
            rel = f["finding"].split(": ", 1)[1]
            f["finding"] += " (known-drift)" if rel in known else " (NEW)"
    findings = discovery + canonical_only_findings(trees, canonical_tree, co_only) + findings
    print(f"=== cross-copy drift over {len(trees)} trees, {len(files)} files"
          f"\n    findings: {len(findings)}")
    for f in findings:
        print(f"    {f['finding']} :: {f.get('hashes') or f.get('trees') or 'tree set'}")
    return 1 if (args.fail and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
