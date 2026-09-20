#!/usr/bin/env python3
"""Pin AGENTS.md's known-failure totals to tests/KNOWN_FAILURES.json.

Why this exists (R&D pulse 2026-09-13): AGENTS.md claimed "Pinned by
tests/test_preregistration_numbers_are_real.py against tests/KNOWN_FAILURES.json
- this line cannot go stale silently again." That test targets the
pilot-ordering preregistration, not the suite baseline, so when Kiln's
c30e8fa pruned KNOWN_FAILURES.json (1557/26/3/5 -> 1621/10/3/0) the governing
instruction file went stale exactly as its own sentence promised it could not.

This checker makes the claim true:
- parse tests/KNOWN_FAILURES.json `_totals` / `_recorded`;
- parse every AGENTS.md known-failure figure block (the reset-policy paragraph
  and the historical whole-suite comment);
- flag any numeric disagreement, and flag a "Pinned by <file> against
  KNOWN_FAILURES.json" claim whose named file does not actually reference the
  JSON.

Usage:
  python3 check_agents_known_failures_consistency.py [root]  # exit 1 on drift
  python3 check_agents_known_failures_consistency.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

# "(measured 2026-09-07, Gen125: 1557 passed, 26 failed, 3 skipped, 5 errors"
PARA_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}),\s*Gen(\d+):\s*"
    r"(\d+)\s+passed,\s*(\d+)\s+failed,\s*(\d+)\s+skipped,\s*(\d+)\s+errors",
    re.I,
)
# "# 1557 passed, 26 failed, 3 skipped, 5 errors"
COMMENT_RE = re.compile(
    r"#\s*(\d+)\s+passed,\s*(\d+)\s+failed,\s*(\d+)\s+skipped,\s*(\d+)\s+errors"
)
# "# Pinned by tests/foo.py against\n# tests/KNOWN_FAILURES.json"
PIN_RE = re.compile(
    r"Pinned by\s+(\S+?\.py)\s+against\s+(?:#\s*)?(?:tests/)?KNOWN_FAILURES\.json",
    re.I | re.S,
)
KEYS = ("passed", "failed", "skipped", "errors")


def _findings(root: Path) -> list[str]:
    out: list[str] = []
    agents = root / "AGENTS.md"
    kf = root / "tests" / "KNOWN_FAILURES.json"
    if not root.exists():
        return [f"root does not exist: {root}"]
    missing = [str(p) for p in (agents, kf) if not p.is_file()]
    if missing:
        # A guard that cannot see its own input must say so, not pass silently
        # (Alice's AGENTS-drift second-seat check, 2026-09-13, boundary finding 2).
        return [f"missing prerequisite: {p}" for p in missing]
    try:
        data = json.loads(kf.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return [f"tests/KNOWN_FAILURES.json unreadable: {exc}"]
    totals = data.get("_totals") or {}
    recorded = data.get("_recorded", "")
    try:
        text = agents.read_text()
    except OSError as exc:
        return [f"unreadable prerequisite: {agents.name}: {exc}"]
    mrec = re.match(r"\s*(\d{4}-\d{2}-\d{2}),\s*Gen(\d+)", recorded)
    rec_date, rec_gen = (mrec.group(1), mrec.group(2)) if mrec else (None, None)

    def check(tag: str, date, gen, nums) -> None:
        if any(totals.get(k) != v for k, v in zip(KEYS, nums)):
            out.append(
                f"{tag}: AGENTS.md says {nums[0]}/{nums[1]}/{nums[2]}/{nums[3]} "
                f"(passed/failed/skipped/errors) but KNOWN_FAILURES.json "
                f"_totals says {totals.get('passed')}/{totals.get('failed')}/"
                f"{totals.get('skipped')}/{totals.get('errors')}"
            )
        if date and rec_date and (date, gen) != (rec_date, rec_gen):
            out.append(
                f"{tag}: AGENTS.md dates it {date}, Gen{gen}; KNOWN_FAILURES.json "
                f"_recorded says {recorded!r}"
            )

    for m in PARA_RE.finditer(text):
        check("reset-policy paragraph", m.group(1), m.group(2),
              tuple(int(x) for x in m.groups()[2:]))
    for m in COMMENT_RE.finditer(text):
        check("historical comment", None, None,
              tuple(int(x) for x in m.groups()))

    pm = PIN_RE.search(text)
    if pm:
        pin_file = pm.group(1)
        target = root / pin_file
        if not target.exists():
            out.append(f"claimed pin {pin_file} does not exist")
        elif "KNOWN_FAILURES" not in target.read_text(errors="replace"):
            out.append(
                f"claimed pin {pin_file} never references KNOWN_FAILURES.json - "
                "the AGENTS.md pin claim is false"
            )
    return out


def _self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "tests").mkdir()
        (root / "tests" / "KNOWN_FAILURES.json").write_text(json.dumps(
            {"_recorded": "2026-09-07, Gen125 (measured, not typed)",
             "_totals": {"passed": 1621, "failed": 10, "skipped": 3, "errors": 0}}))
        (root / "tests" / "pin.py").write_text("# reads KNOWN_FAILURES.json\n")
        good = (
            "reconciled with `tests/KNOWN_FAILURES.json` (measured 2026-09-07, "
            "Gen125: 1621 passed, 10 failed, 3 skipped, 0 errors)\n"
            "# Pinned by tests/pin.py against\n# tests/KNOWN_FAILURES.json\n"
        )
        (root / "AGENTS.md").write_text(good)
        assert _findings(root) == [], _findings(root)

        bad = good.replace("1621 passed, 10 failed, 3 skipped, 0 errors",
                           "1557 passed, 26 failed, 3 skipped, 5 errors")
        (root / "AGENTS.md").write_text(bad)
        f = _findings(root)
        assert any("1557/26/3/5" in x for x in f), f

        (root / "AGENTS.md").write_text(
            good.replace("tests/pin.py", "tests/not_the_pin.py"))
        (root / "tests" / "not_the_pin.py").write_text("# pilot ordering only\n")
        f = _findings(root)
        assert any("pin claim is false" in x for x in f), f

        (root / "AGENTS.md").unlink()
        f = _findings(root)
        assert any("missing prerequisite" in x for x in f), f

        # A directory at a required path is missing, not a crash (Alice 09:11).
        (root / "AGENTS.md").mkdir()
        f = _findings(root)
        assert any("missing prerequisite" in x for x in f), f
    print("self-test: PASS (consistent pair clean; stale totals flagged; "
          "false pin claim flagged; missing/directory prerequisite reported, not silent)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    root = Path(a.root)
    print(f"=== {root.resolve()}")
    findings = _findings(root)
    print(f"    known-failure baseline drift findings: {len(findings)}")
    for f in findings:
        print(f"    [DRIFT] {f}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
