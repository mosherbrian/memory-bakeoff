#!/usr/bin/env python3
"""Alice second-driver: re-derive the consolidated full-corpus mining numbers
from Kiln's committed local outputs. Prints aggregate counts ONLY — the
`excerpt` field is never read into memory or printed. Local, $0, no writes.

Run: python3 alice_full_corpus_rederive.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path.home() / ".local/share/memory-bakeoff/transcript-mining/full-20260913"


def main() -> int:
    s = json.loads((OUT / "stats.json").read_text())
    corr = [json.loads(l) for l in (OUT / "correction-events.jsonl").read_text().splitlines() if l.strip()]
    fact = [json.loads(l) for l in (OUT / "durable-facts.jsonl").read_text().splitlines() if l.strip()]

    per_event = Counter(d.get("class") for d in corr if d.get("class") != "repeated_instruction")
    rep = [d for d in corr if d.get("class") == "repeated_instruction"]
    facts = Counter(d.get("class") for d in fact)

    def digest_line(name: str) -> str:
        for ln in (OUT / name).read_text().splitlines():
            if ln.startswith("- candidates:"):
                return ln.strip()
        return "?"

    print("=== stats.json ===")
    print("files_scanned            :", s["files_scanned"])
    print("scan_by_file length      :", len(s["scan_by_file"]))
    print("sum by_project files     :", sum(v["files"] for v in s["by_project"].values()))
    print("files_excluded_open      :", s["files_excluded_open"], "/ names", len(s["excluded_open_names"]))
    print("turns_before_dedupe      :", s["turns_before_dedupe"])
    print("duplicates_removed       :", s["duplicates_removed"])
    print("user_text_turns          :", s["user_text_turns"])
    print("personal_turns_excluded  :", s["personal_turns_excluded"])
    print("observer by_project      :", s["by_project"].get("-var-home-bmosher--claude-mem-observer-sessions"))
    print("=== correction-events.jsonl ===")
    print("total rows               :", len(corr))
    print("per-event by class       :", dict(sorted(per_event.items())), "sum", sum(per_event.values()))
    print("repeated_instruction rows:", len(rep))
    print("repeated occurrences sum :", sum(int(d.get("occurrences") or 0) for d in rep))
    print("=== durable-facts.jsonl ===")
    print("total rows               :", len(fact), "by class", dict(sorted(facts.items())))
    print("=== digests ===")
    print("digest.md                :", digest_line("digest.md"))
    print("corrections-digest.md    :", digest_line("corrections-digest.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
