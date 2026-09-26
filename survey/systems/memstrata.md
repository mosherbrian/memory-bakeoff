# System card: MemStrata (deterministic supersession, bi-temporal ledger)

**kiln · 2026-09-26 · ~500w · advice only, no installs. Sources: web search this session — vendor research page + blog (memstrata.dev), paper abstracts (arXiv:2606.26511, 2608.20685), product site (memstrata.dev/.com). Papers themselves read at abstract/excerpt level only, not full methods. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack".**

## Boundary correction first

Gen124 recorded StateMemBench as NOT FOUND and MemStrata as not located. Both resolve now: StateMem/StateMemBench is arXiv:2608.19652 (Fan et al., 20 Aug 2026 — 234 multi-session scenarios, closed-pool current-vs-superseded grading, explicit-supersession method + single-call wrapper). I did not read it beyond search excerpts; its "not found" status is superseded, its methods are still unread by me. Card below covers **MemStrata**, the lead with a concrete mechanism and local-first fit.

## Mechanism (vendor-described, structure-first)

- **Write path:** each turn yields a candidate fact → exact-duplicate short-circuit (normalized hash) → deterministic assertion path: clean (subject, relation, object) triples normalize the (subject, relation) key; different object → **supersede**, same object → reinforce, new key → store. Non-triple prose falls to a text-gate (similarity + judge, secondary). An early lossy-merge variant regressed below RAG on static recall, so the shipped design retains like RAG and bounds growth only on contradictions.
- **Read path:** query embedding → top-k over **active** facts only → packs original source sentences. No LLM on the read path (~2.1s, "the embedding floor" vs 16–18s rerank baselines).
- **Ledger:** facts retired, not deleted, in a bi-temporal ledger preserving validity intervals for as-of queries. Their own AUROC 0.59 result (cosine cannot separate contradiction from duplicate) is the reason the rule is deterministic rather than similarity-thresholded.

## Applicability to Brian's costs

Preferences map cleanly onto triples ("Brian / prefers-package-manager / pnpm" — a correction is literally a supersession event). Multi-step procedures do not — 76% of code is not triple-shaped by their own admission (Paper 5: detect-and-flag). So MemStrata addresses cost #2 (repeated preferences) structurally and cost #1 (procedures) barely at all.

## Failure modes / cost / fit

- Triple-only coverage: outside clean assertions the system degrades to similarity+judge — the fuzzy regime with a deterministic core, not instead of it. Extraction quality decides keys; a mis-extracted triple supersedes wrongly with no LLM to catch it on read.
- All accuracy numbers are vendor-reported preprints (0.95–1.00 evolving vs RAG 0.20–0.47; Paper 2: 0.91 vs 0.57–0.59 on 130 SWE-bench transitions; scope: only ~18% of fixes are clean atomic transitions).
- Install: local-first product (PyPI 0.6–0.7.x, linux-x64), consumer-hardware tested (Qwen2.5-Coder-7B, temp 0, fixed seeds, no network) — the closest any candidate comes to Brian's local stack; commercial compiled products with trial + claimed MIT open core (site claims, license not verified by me). Maintenance: fact-key hygiene, fallback-gate behavior, version tracking across their fast-moving releases.

## Deepened: full methods read (arXiv:2606.26511v1, §§1–8 + appendices)

Upgraded from excerpts to the full paper. What changed: (1) Authorship is single-author vendor (Neeraj Yadav, MemStrata.dev/Called It Inc.) — this is a vendor technical report, not independent evidence; treat all numbers accordingly. (2) The limitations section (§7) is unusually honest and directly relevant: extraction keys reliably (~97% supersession) on structured single-value templates but drops to ~44% on messier natural-language contradictions — a whole benchmark quarantined as "a flawed ruler" rather than reported. For Brian's preferences (often one-liners, triple-shaped) the 97% regime plausibly holds; for procedures it does not. (3) As-of-time queries are built (validity intervals stored) but explicitly **not evaluated** — the bi-temporal half of the claim is architecture, not evidence. (4) Ingestion order proxies time throughout; real timestamps + "as-of-T" retrieval are future work. (5) Ablations bracket the result properly (lossy-merge forfeits static recall 0.62/0.13; no-supersession collapses to RAG 0.33) — the method section earns its causal claim *within its envelope*. None of this changes the watch verdict; it sharpens the admission test: triple-shaped preference corrections (the 97% regime) plus one messy NL case (the 44% regime) to map the boundary before any deployment talk.

## Advice: **watch, medium-low confidence**

Strongest lifecycle mechanism per unit of install cost on the roster, and the only one tested on the same class of hardware Brian runs — but every number is vendor-side, the methods are excerpt-read, and procedures (cost #1) fall outside its triple envelope. Admission test is named and narrow: near-neighbor scope families through deterministic supersession, false-supersession counted, plus one non-triple procedure to map the boundary.
