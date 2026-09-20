#!/usr/bin/env python3
"""S8-7 declaration writer. Freezes items.jsonl from the S6-2 frozen corpus,
then writes declaration.json exactly ONCE, before any run exists. Kept as
provenance; re-running it after the run would break every row's hash binding
and the gate would say so."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
CORPUS = TEAM / "S6-SELECTIVITY" / "corpus.jsonl"
CORPUS_SHA256 = "5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be"

# The S6-2 manifest's declared helpful record per retrieve case, declared
# there before any run and verified twice (CORVID-S6-2-VERIFY). The helpful
# evidence STRING is that record's exact text.
HELPFUL = {
    "sel-001": "sel-001-r2",
    "sel-002": "sel-002-r1",
    "sel-003": "sel-003-r2",
    "sel-004": "sel-004-r3",
    "sel-005": "sel-005-r2",
}


def main() -> int:
    if (HERE / "declaration.json").exists() or (HERE / "items.jsonl").exists():
        print("declare.py: declaration or items already on disk; not rewriting")
        return 1
    body = CORPUS.read_bytes()
    if hashlib.sha256(body).hexdigest() != CORPUS_SHA256:
        print(f"declare.py: corpus sha mismatch against the S6-2 pin")
        return 1
    cases = [json.loads(l) for l in body.decode().splitlines() if l.strip()]

    items = []
    for c in cases:
        if c["expect"] != "retrieve":
            continue
        text_of = {r["id"]: r["text"] for r in c["store"]}
        helpful = text_of[HELPFUL[c["case_id"]]]
        items.append({"item_id": c["case_id"], "query": c["query"],
                      "helpful_evidence": [helpful]})
    if len(items) != 5:
        print(f"declare.py: expected 5 retrieve items, got {len(items)}")
        return 1
    (HERE / "items.jsonl").write_text(
        "".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")
    items_sha = hashlib.sha256((HERE / "items.jsonl").read_bytes()).hexdigest()

    declaration = {
        "declared_at": datetime.now(timezone.utc).isoformat(),
        "budget_chars": 600,
        "scoring": {"presence": "all-helpful-substrings",
                    "irrelevant_bytes": "delivered-minus-helpful"},
        "pressure": {"tool_output_bytes": 20000},
        "items_sha256": items_sha,
        "adapters": ["bm25", "pi_lcm_toollevel",
                     "claude_mem_chroma_lsa_no_recency"],
    }
    (HERE / "declaration.json").write_text(
        json.dumps(declaration, indent=1) + "\n", encoding="utf-8")
    print(f"items frozen: 5, sha {items_sha[:12]}...")
    print(f"declared at {declaration['declared_at']}, budget 600 chars, "
          f"load 20000 bytes; nothing has run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
