#!/usr/bin/env python3
"""Evidence-index link integrity checks (Corvid, R&D pulses 2026-09-12).

Two static checks over a research repo's Markdown:

1. INVALIDATED RUNS — any reference to `results/<dir>/` whose directory carries
   an `INVALIDATED.md` sidecar, with cue signals (same-line, nearby ±3 lines, or
   a file-top banner) so a documented reference can be told from a live one.
   The defect this guards: a retraction travels while an invalidated *run* is
   still linked as evidence (`RESULTS.md` row 85 -> `results/hindsight_gen4_core_r1`).
2. DANGLING LINKS — any Markdown link target under `results/` or `research/`
   that does not resolve on disk (renamed/deleted artifact still cited).
   From Muse batch 3 item 3.1.

Exit 1 if any uncued invalidated reference or dangling link remains, so this can
serve as a closure gate. `--self-test` builds both defects and asserts each is
caught through the real scan path (positive control).

Usage:
  python3 check_invalidated_pointers.py [roots...]
  python3 check_invalidated_pointers.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path

LINK_RE = re.compile(r"results/([A-Za-z0-9._-]+)")
MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")
CUE_RE = re.compile(r"invalidat|excluded|do not use|not causal|void", re.I)
INDEX_PREFIXES = ("results/", "research/")
BANNER_LINES = 15
NEARBY = 3


def invalidated_dirs(root: Path) -> set[str]:
    return {p.parent.name for p in root.glob("results/*/INVALIDATED.md")}


def normalize_target(raw: str) -> str:
    t = raw.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1]
    t = t.split()[0] if t.split() else t          # drop an optional link title
    return t.split("#", 1)[0]                      # drop an anchor


def is_index_target(target: str) -> bool:
    return target.startswith(INDEX_PREFIXES)


def dangling_findings(root: Path, md: Path, lines: list[str]) -> list[dict]:
    out: list[dict] = []
    for i, line in enumerate(lines):
        for raw in MD_LINK_RE.findall(line):
            target = normalize_target(raw)
            if not is_index_target(target):
                continue
            # Markdown targets are file-relative, but this repo also writes
            # root-relative evidence paths; accept either resolution.
            if (md.parent / target).exists() or (root / target).exists():
                continue
            out.append({
                "file": str(md.relative_to(root)),
                "line": i + 1,
                "target": target,
                "text": line.strip()[:160],
            })
    return out


def invalidated_findings(root: Path, inv: set[str], md: Path, lines: list[str]) -> list[dict]:
    out: list[dict] = []
    banner = any(CUE_RE.search(x) for x in lines[:BANNER_LINES])
    for i, line in enumerate(lines):
        for name in LINK_RE.findall(line):
            if name not in inv:
                continue
            window = lines[max(0, i - NEARBY): i + NEARBY + 1]
            out.append({
                "file": str(md.relative_to(root)),
                "line": i + 1,
                "dir": f"results/{name}",
                "same_line_cue": bool(CUE_RE.search(line)),
                "nearby_cue": any(CUE_RE.search(x) for x in window),
                "file_banner": banner,
                "text": line.strip()[:160],
            })
    return out


def scan(root: Path) -> tuple[set[str], list[dict], list[dict], list[dict]]:
    inv = invalidated_dirs(root)
    inval: list[dict] = []
    dangling: list[dict] = []
    unreadable: list[dict] = []
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if rel.parts and rel.parts[0] == "results":
            continue  # results themselves are artifacts, not the evidence index
        if not md.is_file():
            continue
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            # An unreadable index is a finding, not "no references" (Assay/Alice 09:31-34).
            unreadable.append({"finding": f"unreadable prerequisite: {rel}",
                               "got": "unreadable", "want": "readable"})
            continue
        inval.extend(invalidated_findings(root, inv, md, lines))
        dangling.extend(dangling_findings(root, md, lines))
    return inv, inval, dangling, unreadable


def documented(f: dict) -> bool:
    return f["same_line_cue"] or f["nearby_cue"] or f["file_banner"]


def missing_prerequisites(root: Path) -> list[dict]:
    # No scannable index Markdown is a mis-root, not a clean tree.
    for md in root.rglob("*.md"):
        rel = md.relative_to(root)
        if rel.parts and rel.parts[0] == "results":
            continue
        if not md.is_file():
            continue
        return []
    return [{"finding": "missing prerequisite: *.md evidence index "
                        "(no scannable sources)", "got": "absent", "want": "present"}]


def self_test() -> int:
    """Reject a representative bad input of each class through the real path."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "results" / "bad_run").mkdir(parents=True)
        (root / "results" / "bad_run" / "INVALIDATED.md").write_text("invalidated\n")
        (root / "results" / "ok_run").mkdir()
        # uncued invalidated ref + dangling ref + clean ref, in one index
        (root / "INDEX.md").write_text(
            "| a | [bad](results/bad_run) | [dead](results/gone_dir) "
            "| [ok](results/ok_run) |\n")
        inv, inval, dangling, _ = scan(root)
        assert inv == {"bad_run"}, inv
        assert len(inval) == 1 and inval[0]["dir"] == "results/bad_run", inval
        assert documented(inval[0]) is False, inval
        assert [d["target"] for d in dangling] == ["results/gone_dir"], dangling
        # a documented reference must be recognised; a resolved link is clean
        (root / "NOTE.md").write_text(
            "# thing (invalidated)\n\nsee results/bad_run; do not use its ranks\n")
        _, inval2, _, _ = scan(root)
        note = [f for f in inval2 if f["file"] == "NOTE.md"]
        assert note and documented(note[0]) is True, inval2
    with tempfile.TemporaryDirectory() as td:
        assert missing_prerequisites(Path(td)), "empty root not reported"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "results" / "x").mkdir(parents=True)
        (root / "results" / "x" / "INVALIDATED.md").write_text("x\n")
        p = root / "INDEX.md"
        p.write_text("see results/x\n")
        os.chmod(p, 0)
        if not os.access(p, os.R_OK):
            _, _, _, unreadable = scan(root)
            assert unreadable, "unreadable index not reported"
        os.chmod(p, 0o644)
    print("self-test: PASS (uncued invalidated ref flagged; dangling link "
          "flagged; resolved link clean; banner/inline cue detected; "
          "source-less and unreadable index reported)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=["."])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    rc = 0
    for raw in args.roots:
        root = Path(raw).resolve()
        pre = missing_prerequisites(root)
        if pre:
            print(f"=== {root}\n    missing prerequisites: {len(pre)}")
            for f in pre:
                print(f"    {f['finding']}")
            rc = 1
            continue
        inv, inval, dangling, unreadable = scan(root)
        uncued = [f for f in inval if not documented(f)]
        print(f"=== {root}\n    invalidated_dirs={len(inv)}  refs={len(inval)}  "
              f"uncued={len(uncued)}  dangling={len(dangling)}")
        for f in inval:
            print(f"    [{'UNCUED' if not documented(f) else 'cued  '}] "
                  f"{f['file']}:{f['line']} -> {f['dir']}")
        for f in dangling:
            print(f"    [DANGLING] {f['file']}:{f['line']} -> {f['target']}")
        for u in unreadable:
            print(f"    {u['finding']}")
        if uncued or dangling or unreadable:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
