#!/usr/bin/env python3
"""S10-2 rank-aware retrieval diagnostics — the reporting-path tool.

Usage:  python3 diag.py RANKINGS --k 5
Prints: {"per_adapter": {adapter: {condition: {mrr, ndcg, presence}}}}
on stdout, one line of JSON, nothing else. Exit 0 on success.

Sprint reports surface rank ordering by calling this tool on a rankings
file and embedding its cells beside whatever set/presence numbers they
already carry (see design.md for the rankings schema). Positives only
(category "negative" is skipped, as metrics.aggregate does).

The three numbers stay separate, each its own number, never blended:
  mrr       mean metrics.score_case(...).reciprocal_rank  (imported, the
            repo's own reciprocal rank — not re-derived here)
  presence  mean metrics.score_case(...).hit_at_k            (imported)
  ndcg      binary gain, DCG@k = sum 1/log2(rank+1) over relevant ids in
            the top k, each id counted once, divided by the ideal DCG for
            min(|relevant|, k) hits   (the extension this row adds;
            declared as "binary-gain-log2" in report.json)
No LLM, no network."""
import argparse
import json
import math
from statistics import mean

from memory_bakeoff.metrics import score_case
from memory_bakeoff.models import QueryCase, RetrievalItem, RetrievalResult


def ndcg(relevant: set, ranked: list, k: int) -> float:
    seen, dcg = set(), 0.0
    for rank, rid in enumerate(ranked[:k], 1):
        if rid in relevant and rid not in seen:
            seen.add(rid)
            dcg += 1 / math.log2(rank + 1)
    ideal = sum(1 / math.log2(r + 1)
                for r in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("rankings")
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()

    cells = {}
    with open(a.rankings, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r["category"] == "negative":
                continue
            got = score_case(
                QueryCase(r["case_id"], r["category"], "",
                          tuple(r["relevant_ids"])),
                RetrievalResult([RetrievalItem(i, "") for i in
                                 r["ranked_ids"]], 0.0), a.k)
            cells.setdefault(r["adapter"], {}).setdefault(
                r["condition"], []).append(
                (got.reciprocal_rank,
                 ndcg(set(r["relevant_ids"]), r["ranked_ids"], a.k),
                 got.hit_at_k))
    print(json.dumps({"per_adapter": {
        ad: {c: dict(zip(("mrr", "ndcg", "presence"),
                         (mean(col) for col in zip(*v))))
             for c, v in sorted(conds.items())}
        for ad, conds in sorted(cells.items())}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
