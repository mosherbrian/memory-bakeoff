# muse-drafter: MemStrata grounding pass — paper pair, pin, collision, artifact (spark pulse 2026-09-14)

Follows the contradiction fan-out (`SPARK-CONTRADICTION-FANOUT-20260914.md`,
candidate #1). Abstract/body-level reads only, **no score import**; this is a
grounding + artifact/license pass, not a card.

## It is a paper pair, same single author

| | Paper 1 | Paper 2 |
|---|---|---|
| ID / date | [`arXiv:2606.26511`](https://arxiv.org/abs/2606.26511) v1 **2026-06-25**, 22 KB | [`arXiv:2608.20685`](https://arxiv.org/abs/2608.20685) **2026-08-21** |
| Title | *Temporal Validity in Retrieval Memory: Eliminating Stale-Fact Errors for AI Agents over Evolving Knowledge* | *Temporal Validity on Real Software Histories: Eliminating Stale-Fact Errors in Code-Assistant Memory over GitHub Fixes* |
| Author | **Neeraj Yadav** (single) | **Neeraj Yadav** (single) |
| Substrate | synthetic single-value benchmarks (code mutation, config migration, dependency bumps, API evolution) | **real SWE-bench Lite + Verified** GitHub fixes |
| Paper license | arXiv.org **perpetual non-exclusive** (not a CC reuse grant) | same |

Paper 1 is the mechanism; Paper 2 is the real-history validation. Treat them as
one candidate, pinned by **both** arXiv IDs.

## Name collision (pin by arXiv ID, not by name)

`github.com/cuhk-mass/memstrata` is an **unrelated** systems project (CXL memory
tiers in virtualized environments). "MemStrata" alone is ambiguous; every citation
must carry the arXiv ID.

## Goal grounding: the strongest of the fan-out, and it is a *method*

- **Direct E-7 / G1 / G2 analogue:** deterministic `(subject, relation, object)`
  supersession over a **bi-temporal ledger** (`valid_from`, `valid_to`,
  `superseded_by`; facts retired not deleted) — no cosine threshold, no LLM judge.
  This is the closest published shape to our supersession/stale-use discipline.
- **Coding-specific in Paper 2** (SWE-bench → G4/G5), which the abstract-only
  fan-out note could not see.
- **A structural claim we can test locally, cheaply:** cosine similarity cannot
  separate a contradicted fact from a duplicate (AUROC **0.59**, near chance;
  contradictions are *more* embedding-similar than rephrasings), so a
  similarity-threshold update policy leaks stale values (surprise-gate variants
  leak **25–60%**). Vendor numbers, not imported — but the *shape* is directly
  relevant to our dense-LSA null and our S6 rule.

## Vendor claims on record (unverified, not citable)

- RAG serves the superseded value **15–40%** when forced to answer (dependency
  bumps the exception at 15%, a string heuristic); MemStrata drives it to **~0**.
  Paper 2 on real fixes: RAG **36–38%** stale, MemStrata **~0** (forced 0.000–0.015
  across runs — one answer flip on 130).
- Accuracy: Paper 1 **0.95–1.00** vs RAG **0.20–0.47** on evolving knowledge, ties
  RAG on static; Paper 2 **0.91/0.99** vs RAG **0.57–0.62**.
- Latency ~2.1 s (embedding floor) vs ~16–18 s for LLM reranker/verifier.

## Two things worth stealing (design, not scores)

1. **The marker-free invariant** (Paper 1): a stale fact carrying any textual
   marker (`[OUTDATED]`, `(legacy)`) lets a baseline disambiguate by reading the
   label, silently inflating its score. This is a contamination corner for our own
   stale-path probe — the probe must render stale/current statements
   **differing only in the value**. Cross-links to
   `SPARK-STALE-PATH-PROBE-DESIGN-20260914.md` and design corner 5.
2. **The extraction-coverage decoupling** (Paper 2): only **~18%** of real GitHub
   fixes are clean atomic state transitions; the paper deliberately measures the
   mechanism *conditional on clean extraction* and defers extraction coverage.
   That is an honest scope statement, and it bounds how much of our coding-memory
   corpus a deterministic supersession rule could ever cover.

## Artifact / license status — still open

Paper 1's arXiv comment says "**Code, prompts, and evaluation datasets
included**", but **no public repo or dataset URL surfaced** in the abs page or the
HTML body, and the license is arXiv non-exclusive (no reuse grant). Under our P1
rule (verify before adapter work): **artifact availability and code license are
UNVERIFIED**. Next bounded step if the card is taken: check the arXiv ancillary
files / the author's site, or email for the harness. No adapter work may rest on
"we release" until a URL and a license exist.

$0, web reads only (arXiv abs + HTML bodies + search), no Muse batching. —
muse-drafter (Spark)
