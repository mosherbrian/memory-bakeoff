#!/usr/bin/env python3
"""S8-7 door runner (kiln-flash, 2026-09-18). Reads the frozen declaration,
measures what each memory adapter actually delivers into the prompt, and
writes results.jsonl (run order, every row sha-bound to the declaration) and
verdict.json (both numbers, computed here and recomputed by the gate).

Pre-run hard assertions (the run writes nothing if any fails):
  - the declaration on disk is the one being executed (sha carried per row);
  - the S6-2 corpus matches the pin declare.py froze items from;
  - no pressure chunk contains any item's helpful evidence string.
Deterministic: seeded pressure generation, fixed record timestamps, no
wall-clock in any decision (row ts is bookkeeping only)."""
import sys

sys.dont_write_bytecode = True  # import-time pycache would write into lanes

import hashlib
import json
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM = HERE.parent
REPO = (TEAM / ".." / "implementer" / "repo").resolve()
for p in (str(TEAM / "s4-14-crossengine-rerun"), str(TEAM / "s4-12-crossengine"),
          str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_crossengine import RECORD_TS  # the S4-12/S4-14 fixed stamp, reused
from run_s4_14 import PiLcmToolLevelProvider  # noqa: E402
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.bm25 import BM25Provider  # noqa: E402
from memory_bakeoff.providers.claude_mem_core import (  # noqa: E402
    ClaudeMemChromaLSANoRecencyProvider)

CORPUS = TEAM / "S6-SELECTIVITY" / "corpus.jsonl"
CORPUS_SHA256 = "5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be"
BUDGET = 600                      # declared in declaration.json; mirrored here
CHUNK_FAMILIES = 10               # tool-output template families per item
CHUNK_MIN_CHARS = 2050            # per chunk; 10 chunks >= the 20000-byte load
PRESENCE, BYTES = "helpful_evidence_presence", "irrelevant_delivered_bytes"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def score_one(delivered: str, helpful: list) -> tuple:
    """The declared scoring, implemented from design.md's two rules."""
    d = norm(delivered)
    matched = [h for h in helpful if norm(h) in d]
    irr = len(delivered.encode("utf-8")) - sum(
        len(h.encode("utf-8")) for h in matched)
    return int(len(matched) == len(helpful)), max(irr, 0)


def compose(texts: list, budget: int) -> str:
    """The declared composition: whole records in return order, joined with
    "\\n", stopping at the first record that would not fit whole; an
    oversized FIRST record is hard-truncated to the budget."""
    out = ""
    for t in texts:
        if len(out) + (1 if out else 0) + len(t) <= budget:
            out += ("\n" if out else "") + t
        elif not out:
            return t[:budget]
        else:
            break
    return out


# ---- competing tool-output generation (deterministic, per design.md) ----

HOSTS = ["web-01", "web-02", "web-03", "db-01", "db-02", "cache-01",
         "cache-02", "queue-01", "build-04", "nfs-02"]
DIRS = ["/var/log", "/srv/releases", "/opt/tools", "/etc/nginx", "/home/ci",
        "/mnt/archive", "/srv/backup"]
USERS = ["amara", "viktor", "josie", "ren", "talia", "marcus", "ines", "devon"]
PKGS = ["libzip", "nghttp2", "sqlite", "imagemagick", "protobuf", "curl",
        "ripgrep", "jq", "openssl", "zstd"]
STATUS = ["open", "in-progress", "waiting-on-field", "resolved", "reopened"]
ROUTES = ["/api/v2/health", "/static/app.js", "/api/v2/ingest",
          "/assets/logo.svg", "/api/v2/reports", "/healthz", "/metrics"]


def _rng(item_id: str, family: int) -> random.Random:
    seed = int(sha_bytes(f"door-press|{item_id}|{family}".encode())[:16], 16)
    return random.Random(seed)


def _fill(lines: list) -> str:
    body = "\n".join(lines)
    i = 0
    while len(body) < CHUNK_MIN_CHARS:
        body += "\n" + lines[i % len(lines)]
        i += 1
    return body


def gen_chunk(item_id: str, family: int) -> str:
    r = _rng(item_id, family)
    host = lambda: r.choice(HOSTS)
    if family == 0:   # fs tree listing
        lines = ['{"tool":"fs_tree","path":"%s","entries":[' % r.choice(DIRS)]
        entries = ["%s.%s" % ("".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(r.randint(4, 9))), r.choice(["log", "json", "yaml", "tmp", "gz"])) for _ in range(30)]
        lines[0] += ", ".join('"%s"' % e for e in entries) + "]}"
        return _fill(lines)
    if family == 1:   # backup log tail
        return _fill(["%s %s backup: incremental %d files, %d MB, ok" % (
            "2026-09-1%dT02:%02d:%02d" % (r.randint(1, 7), r.randint(0, 59), r.randint(0, 59)),
            host(), r.randint(100, 9000), r.randint(10, 900)) for _ in range(8)])
    if family == 2:   # dns lookup table
        return _fill(["%s.internal  A  10.%d.%d.%d" % (
            host(), r.randint(0, 9), r.randint(0, 40), r.randint(1, 250))
            for _ in range(12)])
    if family == 3:   # CI matrix
        rows_ = [{"os": r.choice(["ubuntu-24.04", "debian-13", "fedora-43"]),
                  "runtime": "3.%d" % r.randint(10, 13),
                  "suite": r.choice(["unit", "lint", "integration", "docs"])}
                 for _ in range(r.randint(3, 8))]
        return _fill(['{"include": %s}' % json.dumps(rows_, separators=(",", ":"))
                      for _ in range(4)])
    if family == 4:   # metrics samples
        return _fill(["%s cpu=%d%% mem=%d%% disk=%d%%" % (
            host(), r.randint(2, 95), r.randint(20, 90), r.randint(10, 85))
            for _ in range(12)])
    if family == 5:   # ticket export
        return _fill(["OPS-%d [%s] %s task on %s (%s)" % (
            r.randint(4100, 4999), r.choice(STATUS),
            r.choice(["rotate", "patch", "reimage", "audit", "decommission",
                      "provision", "drain"]),
            host(), r.choice(USERS)) for _ in range(10)])
    if family == 6:   # cache stats
        return _fill(["%s hit_rate=0.%02d entries=%d evictions=%d" % (
            host(), r.randint(50, 99), r.randint(1000, 90000), r.randint(0, 60))
            for _ in range(8)])
    if family == 7:   # http access log
        return _fill(['10.%d.%d.%d - - [18/Sep/2026:0%d:%02d:%02d +0000] '
                      '"GET %s HTTP/1.1" 200 %d' % (
                          r.randint(0, 9), r.randint(0, 40), r.randint(1, 250),
                          r.randint(0, 9), r.randint(0, 59), r.randint(0, 59),
                          r.choice(ROUTES), r.randint(200, 60000))
                      for _ in range(14)])
    if family == 8:   # config dump
        return _fill(["%s = %s" % (k, v) for k, v in [(
            r.choice(["connect_timeout_s", "retry_max", "pool_size",
                     "read_timeout_s", "flush_interval_s", "max_backoff_s",
                     "keepalive_count", "drain_grace_s"]),
            str(r.choice([1, 2, 5, 10, 30, 60, 120, 256, 512]))) for _ in range(14)]])
    return _fill(["queue build-jobs depth=%d oldest=%ds workers=%d busy=%d" % (
        r.randint(0, 40), r.randint(5, 900), r.randint(2, 16), r.randint(0, 15))
        for _ in range(8)])  # family 9: queue snapshot


def pressure_load(item_id: str, helpful_all: list) -> tuple:
    """(records, exact byte total). Aborts the run if any chunk carries any
    item's helpful evidence string."""
    chunks = [gen_chunk(item_id, f) for f in range(CHUNK_FAMILIES)]
    joined = norm("\n".join(chunks))
    for h in helpful_all:
        if norm(h) in joined:
            print(f"ABORT: pressure load for {item_id} contains helpful "
                  f"evidence {h!r}; the run would be corrupt by construction")
            sys.exit(1)
    total = sum(len(c.encode("utf-8")) for c in chunks)
    if total < 20000:
        print(f"ABORT: pressure load for {item_id} is {total} bytes, below "
              f"the declared 20000")
        sys.exit(1)
    recs = [MemoryRecord(id=f"{item_id}-tool-{i:02d}", text=c,
                         timestamp=RECORD_TS, session_id=f"sess-{item_id}")
            for i, c in enumerate(chunks)]
    return recs, total


def records_for(case, extra: list) -> list:
    base = [MemoryRecord(id=r["id"], text=r["text"], timestamp=RECORD_TS,
                         session_id=f"sess-{case['case_id']}")
            for r in case["store"]]
    return base + extra


def query_for(item: dict) -> QueryCase:
    return QueryCase(id=item["item_id"], category="retrieve",
                     query=item["query"], relevant_ids=(), prohibited_ids=())


def main() -> int:
    decl_bytes = (HERE / "declaration.json").read_bytes()
    decl = json.loads(decl_bytes)
    decl_sha = sha_bytes(decl_bytes)
    items = [json.loads(l) for l in
             (HERE / "items.jsonl").read_text().splitlines() if l.strip()]
    if sha_bytes((HERE / "items.jsonl").read_bytes()) != decl["items_sha256"]:
        print("ABORT: items.jsonl does not match the declaration's pin")
        return 1
    if sha_bytes(CORPUS.read_bytes()) != CORPUS_SHA256:
        print("ABORT: S6-2 corpus does not match the pin declare.py froze from")
        return 1
    budget, load = decl["budget_chars"], decl["pressure"]["tool_output_bytes"]
    adapters = decl["adapters"]
    corpus = {c["case_id"]: c for c in
              (json.loads(l) for l in CORPUS.read_text().splitlines() if l.strip())}
    helpful_all = [h for i in items for h in i["helpful_evidence"]]

    pressure_cache = {}
    for item in items:
        pressure_cache[item["item_id"]] = pressure_load(item["item_id"],
                                                        helpful_all)
    print("pressure loads built and asserted clean "
          f"(all >= {load} bytes, no helpful evidence inside)")

    rows, delivered_index = [], {}

    def run_cell(adapter, condition, item):
        extra, comp_bytes = (pressure_cache[item["item_id"]]
                             if condition == "pressure" else ([], 0))
        store = records_for(corpus[item["item_id"]], extra)
        q = query_for(item)
        if adapter == "bm25":
            eng = BM25Provider()
            eng.ingest(store)
            res = eng.retrieve(q, top_k=1)
        elif adapter == "pi_lcm_toollevel":
            eng = PiLcmToolLevelProvider()
            eng.reset()
            eng.ingest(store)
            res = eng.retrieve(q, top_k=5)
            eng.close()
        elif adapter == "claude_mem_chroma_lsa_no_recency":
            eng = ClaudeMemChromaLSANoRecencyProvider()
            eng.ingest(store)
            res = eng.retrieve(q, top_k=3)
        else:
            print(f"ABORT: unknown adapter {adapter}")
            sys.exit(1)
        text = compose([it.text for it in res.items], budget)
        rows.append({"ts": now(), "adapter": adapter, "condition": condition,
                     "item_id": item["item_id"], "delivered_text": text,
                     "competing_bytes": comp_bytes,
                     "declaration_sha256": decl_sha})
        delivered_index[(adapter, condition, item["item_id"])] = text
        print(f"  {adapter:>34} {condition:>8} {item['item_id']}: "
              f"{len(res.items)} rec(s), {len(text)} chars")

    t0 = time.perf_counter()
    for adapter in adapters:
        for condition in ("normal", "pressure"):
            for item in items:
                run_cell(adapter, condition, item)
    print(f"ran {len(rows)} cells in {time.perf_counter() - t0:.1f}s")

    over = [r for r in rows if len(r["delivered_text"]) > budget]
    if over:
        print(f"ABORT: {len(over)} delivered texts exceed the budget; "
              f"composition rule violated")
        return 1
    (HERE / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    per = {}
    for adapter in adapters:
        per[adapter] = {}
        for condition in ("normal", "pressure"):
            cells = [score_one(delivered_index[(adapter, condition, i["item_id"])],
                               i["helpful_evidence"]) for i in items]
            per[adapter][condition] = {
                PRESENCE: sum(p for p, _ in cells) / len(cells),
                BYTES: sum(b for _, b in cells) / len(cells),
            }

    def clause(a):
        n, p = per[a]["normal"], per[a]["pressure"]
        return (f"{a} presence {n[PRESENCE]:.2f} -> {p[PRESENCE]:.2f}, "
                f"irrelevant bytes {n[BYTES]:.0f} -> {p[BYTES]:.0f}")

    verdict = {
        "finding": (
            "At the declared 600-char door on 5 frozen evidence items, normal "
            "vs competing tool-output pressure: " + "; ".join(
                clause(a) for a in adapters) + ". The two numbers stay "
            "separate: evidence presence says was-it-handed, irrelevant "
            "delivered bytes says how much came with it."),
        "prior": (
            "none exists: no prior measurement of delivered-text evidence "
            "presence or irrelevant delivered bytes at a declared budget has "
            "been made in this project; S6-2 scored retrieved-id set-F1 and "
            "S7-4 scored upstream family pass rates, neither measured the "
            "door"),
        "card": "team/EXTERNAL-ADEBENCH-20260917.md",
        "budget_chars": budget,
        "per_adapter": per,
    }
    (HERE / "verdict.json").write_text(
        json.dumps(verdict, indent=1) + "\n", encoding="utf-8")
    for a in adapters:
        print(f"{a}: " + clause(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
