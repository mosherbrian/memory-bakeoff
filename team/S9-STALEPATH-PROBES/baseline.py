#!/usr/bin/env python3
"""Marker-canary baselines for the S9-1 stale-path probes (design addendum §3).

Two declared, deterministic, local baselines. Each is run on an item's packed
context over exactly two orderings — as shipped, and with the positions of the
paired value statements swapped — and commits one of the two values per run
(closed pool: an entry is a candidate only if it carries a value). stale-use
rate = stale commits / runs. Rates are in [0, 0.5, 1] over the two runs.

1. "lexical-overlap-position" — the per-item canary baseline. Score = count of
   distinct query tokens present in the entry; high score wins, tie broken by
   earliest packed position. Marker-blind by mechanism: an injected currency
   label shares no token with the query, so on a marker-free item the
   injection must not move this baseline's stale-use rate. On the authority
   item the injected directive IS a candidate (it carries the retired value)
   and must still lose to the paired statements.

2. "label-reader" — the surface-reading control. Identical, except a candidate
   matching a negative-currency label lexicon is demoted. It MUST move under
   injection (that is what makes the canary discriminating): the label alone
   decides, which is precisely the leak the marker-free rule exists to close.

Marked variants, per the gate's injection contract:
  checked-value item: the superseded statement gains " (deprecated)".
  authority item:     the directive text alone is appended to the context.

Usage: python3 baseline.py [ROOT]   (prints one JSON receipt; the rates land
in canary.json exactly as printed here)
"""
import json
import re
import sys
from pathlib import Path

LABEL = "label-reader"
LEXICAL = "lexical-overlap-position"
LABEL_RE = r"legacy|deprecated|outdated|obsolete|retired|superseded|\[[A-Z]+\]"
MARKER = " (deprecated)"


def tokens(text):
    return set(text.lower().split())


def commit(item, context, query_tokens, label_reader):
    best, best_score = None, None
    for pos, entry in enumerate(context):
        if item["current_value"] not in entry and item["superseded_value"] not in entry:
            continue
        score = len(tokens(entry) & query_tokens)
        if label_reader and re.search(LABEL_RE, entry, re.I):
            score -= 100
        if best is None or score > best_score:  # strict: ties keep the earlier entry
            best, best_score = entry, score
    if best is None:
        return "fail"
    if item["superseded_value"] in best:
        return "superseded"
    if item["current_value"] in best:
        return "current"
    return "fail"


def stale_use(item, context, label_reader):
    query_tokens = tokens(item["query"])
    runs = []
    for swap in (False, True):
        ctx = list(context)
        if swap:
            i = next(k for k, e in enumerate(ctx) if item["current_value"] in e)
            j = next(k for k, e in enumerate(ctx) if item["superseded_value"] in e)
            ctx[i], ctx[j] = ctx[j], ctx[i]
        runs.append(commit(item, ctx, query_tokens, label_reader))
    return runs.count("superseded") / len(runs), runs


def marked_context(item):
    ctx = list(item["context"])
    if item["kind"] == "stale-premise-checked-value":
        return [e.replace(item["superseded_statement"],
                          item["superseded_statement"] + MARKER) for e in ctx]
    return ctx + [item["directive"]["text"]]


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    items = [json.loads(line) for line in (root / "items.jsonl").read_text().splitlines() if line.strip()]
    receipt = {"baselines": {LEXICAL: "marker-blind canary baseline",
                             LABEL: "surface-reading control (must move)"},
               "protocol": "two orderings per run (shipped, value-statements swapped); rate = stale commits / 2",
               "runs": {}, "rates": {}}
    for item in items:
        iid = item["item_id"]
        clean = list(item["context"])
        lex_clean, lex_runs_c = stale_use(item, clean, label_reader=False)
        lex_marked, lex_runs_m = stale_use(item, marked_context(item), label_reader=False)
        receipt["runs"][iid] = {
            LEXICAL: {"clean": lex_runs_c, "marked": lex_runs_m},
        }
        receipt["rates"][iid] = {LEXICAL: {"stale_use_clean": lex_clean,
                                           "stale_use_marked": lex_marked}}
    first = items[0]
    ctl_clean, ctl_runs_c = stale_use(first, list(first["context"]), label_reader=True)
    ctl_marked, ctl_runs_m = stale_use(first, marked_context(first), label_reader=True)
    receipt["runs"][first["item_id"]][LABEL] = {"clean": ctl_runs_c, "marked": ctl_runs_m}
    receipt["control"] = {"item": first["item_id"], "baseline": LABEL,
                          "stale_use_clean": ctl_clean, "stale_use_marked": ctl_marked}
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
