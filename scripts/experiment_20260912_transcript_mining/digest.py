#!/usr/bin/env python3
"""Curation digest for mined durable-fact candidates.

Reads durable-facts.jsonl (post privacy-filter), dedupes by normalized
text, groups by class, ranks by cross-source repetition (a fact stated
in multiple sessions/files is a stronger candidate), and writes a
readable digest to the LOCAL output dir. Content never leaves the
machine; team/ receives aggregate counts only.

Usage: digest.py --facts <durable-facts.jsonl> --out <digest.md>
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", "", text.lower())).strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    rows = [json.loads(l) for l in args.facts.read_text(encoding="utf-8").splitlines() if l.strip()]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        # repeated-instruction groups carry their occurrences in `spots`
        # (one per source turn) rather than top-level file/line
        members = [{"class": r["class"], "file": s["file"], "line": s["line"],
                    "session": s.get("session"), "excerpt": r["excerpt"]}
                   for s in r.get("spots", [])] if "spots" in r else [r]
        for member in members:
            groups[(r["class"], norm(r["excerpt"])[:120])].append(member)

    def strength(group):
        sources = {x["file"] for x in group}
        sessions = {x.get("session") for x in group}
        return (len(sessions), len(sources), len(group))

    ranked = sorted(groups.values(), key=strength, reverse=True)
    lines = ["# Durable-fact candidates — curation digest", "",
             f"- candidates: {len(rows)} | unique (normalized): {len(ranked)}",
             "- sorted by strength: distinct sessions, then distinct files, then repeats", ""]
    for n, group in enumerate(ranked, 1):
        rep = group[0]
        sessions = sorted({x.get("session", "?")[:8] for x in group})
        lines.append(f"## {n}. [{rep['class']}] seen {len(group)}x in {len(sessions)} session(s)")
        lines.append(f"- text: {rep['excerpt'][:300]}")
        src = "; ".join(f"{x['file']}:{x['line']}" for x in group[:3])
        lines.append(f"- sources: {src}")
        lines.append("")
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"digest: {len(rows)} candidates -> {len(ranked)} unique groups -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
