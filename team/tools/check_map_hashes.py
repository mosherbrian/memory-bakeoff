#!/usr/bin/env python3
"""Coverage-map guard-hash drift checker — adopted from Assay's prototype.

Prototype author: Assay (`worker-glm-dsh2`), 2026-09-13, sha `439dd1e1…`
(`team/ASSAY-MAP-HASH-AUDIT.md`). Adopted into Corvid's suite with
host-independent default paths and an extended self-test.

Alice's hash-drift audit (`team/ALICE-CHECKER-HASH-DRIFT-AUDIT.md`) named two
things: a naive "first hash after the guard name" audit false-positives on
transition prose (`c6e2f38b… → 3ae6cf05…`), and the coverage map duplicates guard
hashes so it drifts on every guard change. This checks **table cells only** (the
parsed Layer B row), so a transition sentence cannot fool it.

Usage:
  python3 check_map_hashes.py [--map MAP] [--scripts DIR]
  python3 check_map_hashes.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
DEFAULT_SCRIPTS = _HERE.parent
DEFAULT_MAP = _HERE.parents[3] / "team" / "CORVID-CHECKER-COVERAGE-MAP.md"

# A guard row names a `check_*.py`; the hash cell may carry an 8–64 hex prefix,
# with or without the typographic ellipsis (Alice 2026-09-13: requiring exactly
# `<8hex>…` silently skipped a drifted row in another format).
ROW_RE = re.compile(r"^\|\s*(?:\d+|—)\s*\|[^|]*\|\s*`(check_[A-Za-z0-9_]+\.py)`[^|]*"
                    r"\|\s*`([0-9a-f]{8,64})(?:…)?`\s*\|", re.M)
GUARD_ROW_RE = re.compile(r"^\|\s*(?:\d+|—)\s*\|[^|]*\|\s*`(check_[A-Za-z0-9_]+\.py)`", re.M)


def check(map_path: Path, scripts: Path):
    if not map_path.is_file():
        return [{"finding": f"missing prerequisite: {map_path}", "got": "absent"}]
    if not os.access(map_path, os.R_OK):
        return [{"finding": f"unreadable prerequisite: {map_path}", "got": "unreadable"}]
    if not scripts.is_dir():
        return [{"finding": f"missing prerequisite: {scripts} (scripts dir)", "got": "absent"}]
    text = map_path.read_text(encoding="utf-8", errors="replace")
    pairs = ROW_RE.findall(text)
    named = GUARD_ROW_RE.findall(text)
    if not named:
        return [{"finding": "missing prerequisite: no coverage-map table rows", "got": "absent"}]
    findings = []
    # Every live guard must have a map row, or the inverse coverage view is
    # silently incomplete (Assay second-seat, 2026-09-13).
    for name in sorted({p.name for p in scripts.glob("check_*.py")} - set(named)):
        findings.append({"finding": f"missing guard row: {name}", "got": "absent",
                         "want": "a coverage-map table row"})
    # A row that names a guard but whose hash cell did not parse must be loud,
    # not silently dropped (mixed-format map).
    named_c, parsed_c = Counter(named), Counter(g for g, _ in pairs)
    for guard, n in named_c.items():
        if parsed_c.get(guard, 0) < n:
            findings.append({"finding": f"unparsed hash row: {guard} "
                                        f"({parsed_c.get(guard, 0)}/{n} parsed)",
                             "got": "unparseable", "want": "`<8-64 hex>[…]`"})
    for guard, prefix in pairs:
        p = scripts / guard
        if not p.is_file():
            findings.append({"finding": f"map names a missing guard: {guard}", "got": "absent"})
            continue
        live = hashlib.sha256(p.read_bytes()).hexdigest()
        if not live.startswith(prefix.lower()):
            findings.append({"finding": f"hash drift: {guard} map={prefix[:8]} live={live[:8]}",
                             "guard": guard, "map": prefix[:8], "live": live[:8]})
    return findings


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        scripts = root / "scripts"; scripts.mkdir()
        guards = {"check_a.py": b"aaa", "check_b.py": b"bbb"}
        rows = ["| # | class | guard | sha |", "|---|---|---|---|"]
        for name, data in guards.items():
            (scripts / name).write_bytes(data)
            rows.append(f"| 1 | x | `{name}` | `{hashlib.sha256(data).hexdigest()[:8]}…` |")
        m = root / "MAP.md"
        m.write_text("\n".join(rows) + "\n")
        assert check(m, scripts) == [], check(m, scripts)
        # prose transition mention must be ignored (table cell wins)
        m.write_text(m.read_text() + "\nHistorical: `deadbeef…` → current.\n")
        assert check(m, scripts) == [], check(m, scripts)
        # a real table-cell drift is caught
        bad = m.read_text().replace(hashlib.sha256(b"aaa").hexdigest()[:8], "00000000", 1)
        m.write_text(bad)
        f = check(m, scripts)
        assert len(f) == 1 and "hash drift" in f[0]["finding"], f

        # no-ellipsis and full-hash drift are still caught (Alice's format gap)
        a8, b8 = hashlib.sha256(b"aaa").hexdigest(), hashlib.sha256(b"bbb").hexdigest()
        m.write_text("\n".join(rows).replace(f"`{a8[:8]}…`", f"`{a8[:8]}`")
                     .replace(f"`{b8[:8]}…`", f"`{'0' * 64}`") + "\n")
        f = {x["finding"] for x in check(m, scripts)}
        assert any("hash drift" in x for x in f), f

        # a guard row whose hash cell does not parse is a finding, not a skip
        m.write_text("\n".join(rows) + "\n| 9 | x | `check_a.py` | `DEADBEEF` |\n")
        f = check(m, scripts)
        assert any("unparsed hash row" in x["finding"] for x in f), f

        # a live guard with no map row is a finding, not silently uncovered
        (scripts / "check_c.py").write_bytes(b"ccc")
        f = check(m, scripts)
        assert any("missing guard row: check_c.py" in x["finding"] for x in f), f
        (scripts / "check_c.py").unlink()

        # structured prerequisites
        assert any("missing prerequisite" in x["finding"] for x in check(root / "nope.md", scripts))
        empty = root / "EMPTY.md"; empty.write_text("no table here\n")
        assert any("no coverage-map table rows" in x["finding"] for x in check(empty, scripts))
    print("self-test: PASS (cells checked; prose transition ignored; drift caught in "
          "8/64/no-ellipsis forms; unparsed row structured; missing guard row flagged; "
          "missing map structured)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", type=Path, default=DEFAULT_MAP)
    ap.add_argument("--scripts", type=Path, default=DEFAULT_SCRIPTS)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    findings = check(args.map.resolve(), args.scripts.resolve())
    print(f"=== {args.map}\n    coverage-map hash findings: {len(findings)}")
    for f in findings:
        print(f"    {f}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
