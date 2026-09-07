#!/usr/bin/env python3
"""The run fixed by research/pilot_ordering/PREREGISTRATION.md.

Implements sections 1-8 and nothing else. It REFUSES to run without an explicit
authorisation string, and it refuses if the preregistration on disk has changed
since the hash recorded in the authorisation - so the document that constrains
the run is itself pinned by the run.

Usage:
  scripts/run_preregistered_ordering.py --dry-run
  scripts/run_preregistered_ordering.py --authorised-by "<who, verbatim>" --prereg-sha256 <hash>
"""
from __future__ import annotations

import argparse, datetime, hashlib, json, os, random, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.ordering_scorer import hit  # noqa: E402

PREREG = ROOT / "research/pilot_ordering/PREREGISTRATION.md"
SUBSTRATE_SHA = "821a2034d219ab45846873dd14c14f12cfe7776e73527a483f9dac095d38620c"
SRC = Path("/home/bmosher/.cache/huggingface/hub/datasets--xiaowu0162--longmemeval-cleaned/"
           "snapshots/98d7416c24c778c2fee6e6f3006e7a073259d48f/longmemeval_oracle.json")
SPLIT_SEED = 20260907                      # section 3, NOT re-drawn
READER = "qwen3.6-35b-vulkan-nothink"      # section 7
ENDPOINT = "http://strix-halo.local:8080/v1/chat/completions"
OUT = ROOT / "results/preregistered_ordering"


def eligible(items):
    """Section 2, verbatim: hit(gold, ALL text of later) and not hit(gold, ALL text of earlier)."""
    out = []
    for x in items:
        if x["question_type"] != "knowledge-update" or x["question_id"].endswith("_abs"):
            continue
        S = x["haystack_sessions"]
        if len(S) != 2 or [sum(1 for t in s if t.get("has_answer")) for s in S] != [1, 1]:
            continue
        early, later = (" ".join(t["content"] for t in s) for s in S)
        if hit(x["answer"], later) and not hit(x["answer"], early):
            out.append(x)
    return out


def unspent(items):
    """Section 3: the ORIGINAL seed over the ORIGINAL sorted id list, then section 2."""
    all_clean = [x for x in items
                 if x["question_type"] == "knowledge-update"
                 and not x["question_id"].endswith("_abs")
                 and [sum(1 for t in s if t.get("has_answer")) for s in x["haystack_sessions"]] == [1, 1]]
    ids = sorted(x["question_id"] for x in all_clean)
    rng = random.Random(SPLIT_SEED)
    rng.shuffle(ids)
    held = set(ids[len(ids) // 2:])
    return [x for x in eligible(items) if x["question_id"] in held]


def render(item, order):
    """Section 6, verbatim. Dates stripped in BOTH arms; no chronology cue."""
    pairs = list(zip(item["haystack_dates"], item["haystack_sessions"]))
    if order == "reversed":
        pairs = pairs[::-1]
    blocks = []
    for i, (_date, sess) in enumerate(pairs, 1):
        turns = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in sess)
        blocks.append(f"=== conversation {i} ===\n{turns}")
    return ("Below are past conversations between a user and an assistant.\n\n"
            + "\n\n".join(blocks)
            + f"\n\n=== question ===\n{item['question']}\n\n"
              "Answer with the value that is currently true. Reply with the value only.")


def ask(prompt):
    body = json.dumps({"model": READER, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "seed": 0, "max_tokens": 128,
                       "stream": False}).encode()
    req = urllib.request.Request(ENDPOINT, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def mcnemar_exact_two_sided(b, c):
    """Exact binomial on the discordant pairs. No dependency: n is tiny."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--authorised-by")
    ap.add_argument("--prereg-sha256")
    a = ap.parse_args()

    raw = SRC.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != SUBSTRATE_SHA:
        raise SystemExit(f"REFUSED: substrate hash {got} is not the pinned {SUBSTRATE_SHA}. "
                         "Section 1: a run against other bytes is a different experiment.")
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    items = json.loads(raw)
    todo = unspent(items)

    print(f"substrate ok, sha256 {got}")
    print(f"preregistration sha256 {prereg_sha}")
    print(f"unspent and eligible: {len(todo)} items, {len(todo) * 2} calls")

    if a.dry_run:
        print("\nDRY RUN. No reader was called. Section 9: a reader call against an "
              "unspent item before authorisation VOIDS the run.")
        print(f"\nTo authorise:\n  --authorised-by '<who>' --prereg-sha256 {prereg_sha}")
        return 0
    if not a.authorised_by or not a.prereg_sha256:
        raise SystemExit("REFUSED: --authorised-by and --prereg-sha256 are both required. "
                         "Use --dry-run to see the hash.")
    if a.prereg_sha256 != prereg_sha:
        raise SystemExit(f"REFUSED: the preregistration has changed since it was authorised.\n"
                         f"  authorised: {a.prereg_sha256}\n  on disk:    {prereg_sha}\n"
                         "Section 9 voids unrecorded amendments. Re-read it and re-authorise.")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = OUT / stamp
    out.mkdir(parents=True, exist_ok=False)   # never overwrite evidence
    (out / "AUTHORISATION.json").write_text(json.dumps(
        {"authorised_by": a.authorised_by, "preregistration_sha256": prereg_sha,
         "substrate_sha256": got, "started_at": datetime.datetime.now().isoformat(),
         "n_items": len(todo)}, indent=2))
    journal = (out / "journal.jsonl").open("a")
    rows = []
    for i, item in enumerate(todo, 1):
        for order in ("chronological", "reversed"):
            prompt = render(item, order)
            raw_b = ask(prompt)
            journal.write(json.dumps({
                "question_id": item["question_id"], "order": order,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "response": raw_b.decode("utf-8", "replace")}) + "\n")
            journal.flush(); os.fsync(journal.fileno())
            ans = json.loads(raw_b)["choices"][0]["message"]["content"].strip()
            ok = hit(item["answer"], ans)
            rows.append({"question_id": item["question_id"], "order": order,
                         "gold": item["answer"], "answer": ans, "hit": ok})
            print(f"[{i:3d}/{len(todo)}] {item['question_id']:>12} {order:>14} "
                  f"{'HIT ' if ok else 'MISS'} gold={item['answer']!r:34.34} got={ans!r:40.40}",
                  flush=True)
    (out / "rows.json").write_text(json.dumps(rows, indent=2))

    by = {}
    for r in rows:
        by.setdefault(r["question_id"], {})[r["order"]] = r["hit"]
    b = sum(1 for v in by.values() if v["chronological"] and not v["reversed"])
    c = sum(1 for v in by.values() if v["reversed"] and not v["chronological"])
    p = mcnemar_exact_two_sided(b, c)
    powered = (b + c) >= 6
    res = {"n_items": len(by),
           "chronological_hits": sum(v["chronological"] for v in by.values()),
           "reversed_hits": sum(v["reversed"] for v in by.values()),
           "discordant_chronological_only": b, "discordant_reversed_only": c,
           "mcnemar_exact_two_sided_p": p,
           "preregistered_direction": "chronological > reversed",
           "direction_observed": "chronological > reversed" if b > c else
                                 ("reversed > chronological" if c > b else "none"),
           "underpowered": not powered,
           "reading": ("UNDERPOWERED: fewer than 6 discordant pairs. This run cannot "
                       "distinguish no effect from too few items, and its null is NOT "
                       "evidence of absence.") if not powered else
                      ("significant at alpha 0.05" if p < 0.05 else
                       "not significant at alpha 0.05")}
    (out / "RESULT.json").write_text(json.dumps(res, indent=2))
    print("\n" + json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
