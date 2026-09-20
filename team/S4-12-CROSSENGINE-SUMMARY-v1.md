# S4-12 — Cross-engine invocation measurement, summary table v1

**Row:** QUEUE S4-12 (Sprint-4 order 5; gate on S4-10 — satisfied 2026-09-16)
**Author:** kiln-flash (sole doer) · **Date:** 2026-09-16 12:01 PDT · **Cost:** $0, all local
**Verifier:** corvid-dsh (never reviews what it authored; I never verify what I wrote)
**Status:** done pending verification — all numbers below are computed programmatically
from the fire logs in the cited run dirs; **no score import**; no metered arm (the
metered product arm stays post-reset on Brian's GO).

## What was run

The frozen standard tier — **corpus v3** (`team/invocation-corpus-v3-standard/`,
`corpus.jsonl` sha256 `7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0`,
verified on disk at run time, fail-closed in the runner) — across **two
`controlled_core` engines plus one `baseline` context arm**, all in-process,
deterministic, local, $0:

| Engine | Class | Pin | results dir |
|---|---|---|---|
| `claude_mem_fts5_core` | controlled_core | claude-mem `@fa6a1e9ec12d23f98326a9b26e243acb0819e105` (Apache-2.0, CLAIMS-LEDGER row 10) + adapter sha256 `53199f688574c9e5b037c9231d87e560b21a6103d956ddc22036ef523c8d594a` | `team/s4-12-crossengine/results-claude_mem_fts5_core/` |
| `pi_lcm_store_reader` | controlled_core | pi-project-recall store queries (in-tree) + pi-lcm schema; receipt `docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md` rows 1–2 (12/12); adapter sha256 `e2f87f92b5651aee6ad77764ffbd1533ba9d07300899c6977bc23a01b431d42e` | `team/s4-12-crossengine/results-pi_lcm_store_reader/` |
| `bm25` (context only, not counted toward the ≥2) | baseline | in-tree `src/memory_bakeoff/providers/bm25.py` at canonical commit `be2bfa9` | `team/s4-12-crossengine/results-bm25/` |

**Harness trigger (fixed across arms):** canonical `pi-change-trigger` @ commit
`db31ea3e0138083bfd136233131f575f0640e9b5`, `index.ts` sha256
`ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01` — re-verified
on disk this turn (Addendum A pin). Harness = `team/invocation-corpus-v3-standard/run_standard.py`
rev `e84bd58e1ff8e8162406d33265c93cfcdcea0d61b0600fe0650dc6b3b5b00c0f`
(`metrics()`/`load_stopwords()` imported verbatim; `run_scenario` copied with **one
marked delta**: the topics file source). Runner: `team/s4-12-crossengine/run_crossengine.py`.
Model `night/qwen3.8-27b-code` via pi (pi binary sha256 `5406c369954516fb...`), same
as the validated S3-1/S4-10 harness. One scenario per isolated agent dir, exactly as S3-1.

**Engine-derived topic set (the cross-engine variable).** Per
`RESEARCH-INVOCATION-SURFACE-AUDIT.md` implication 3, the trigger's topic set is
derived from each engine's own stored surface: the engine ingests the scenario's
record (raw mode, fixed timestamp 2026-09-01T00:00:00Z), then is queried with each
of the scenario's three turn prompts (`top_k=2`); the retrieved stored-record texts
become the trigger's topics file. Empty retrieval → empty topics → the trigger
cannot fire on `topic`: an honest zero, never imputed. Per-turn retrieval evidence
(query, retrieved ids/texts) is in every run dir's `topics-derivation.jsonl`.

## Summary table v1

All values num/den computed by `run_standard.metrics()` from the fire logs.

| Metric | direct arm (S4-10 frozen run, reference) | claude_mem_fts5_core | pi_lcm_store_reader | bm25 (baseline ctx) |
|---|---|---|---|---|
| **FBMR_topic** (primary) | 30/30 | **0/30** | **0/30** | **25/30** |
| FalseFire (plain fillers) | 0/60 | 0/60 | 0/60 | 0/60 |
| NearMissFire | 24/24 | 0/24 | 0/24 | 20/24 |
| FirePrecision (S3-1 pre-reg def) | 30/114 | 0/60 | 0/60 | 25/110 |
| fresh_rate | 60/60 | 60/60 | 60/60 | 60/60 |
| gap_rate | 0/60 | 0/60 | 0/60 | 0/60 |
| engine-derived topic surface non-empty | n/a (ledger = summaries) | 0/60 scenarios | 0/60 scenarios | 47/60 scenarios |

The direct arm column is the S4-10 frozen run (`team/invocation-corpus-v3-standard/results/`),
cited as the **ceiling reference** where the trigger's ledger is seeded with the
corpus summaries themselves; it is not a new run and is not counted as an engine.

## Findings

- **F1 — strict stored surfaces are trigger-invisible (honest zero).** Both
  `controlled_core` engines score FBMR_topic 0/30 with a 0/60 non-empty derivation
  surface: their phrase-strict retrieval (claude-mem quoted-phrase FTS5 MATCH;
  pi-lcm FTS5/LIKE store queries) returns nothing for moment prompts, so the
  trigger sees an empty ledger. Per the surface audit, this is a **system
  property of the stored surface, not a harness artifact and not a product
  verdict** — the native_proactive-style caveat applies: the zero means "this
  integration surface carries no topic signal to a tokensOf trigger," not
  "the memory system is bad."
- **F2 — bm25 is family-blind exactly where its tokenizer is.** All 5 FBMR
  misses (T001,T003,T005,T007,T009) are env_fact topic moments: the stored text
  `STAGING_PORT=8443` tokenizes (bm25 `TOKEN_RE` keeps `_/./://:-`) as one token
  `staging_port`, while prompts use `staging` + `port` — zero lexical overlap.
  The other five families: 25/25.
- **F3 — entity-echo false fires from full-content surfaces (new, observational
  count, not a pre-registered metric).** bm25 fired `topic` on **5/30 offtopic
  moments** (T022–T030 even): its stored surface is the full record content,
  which contains the entity token (`billing-101`) that offtopic prompts
  deliberately reuse ("backup rotation for billing-101 storage"). The direct arm
  cannot exhibit this (0/30) because its ledger holds the terse summary. Also
  feeds NearMissFire 20/24. Over-specific stored surfaces create invocation
  false positives the summary-seeded ledger is immune to — the exact per-engine
  property a cross-engine run exists to expose.
- **F4 — fresh/gap behave as designed everywhere.** fresh fires on every
  scenario's turn 1 (60/60, the known method limit, excluded from FBMR_topic);
  gap never fires (30-minute gap, 2-second turn cadence). v3's stale/anachronism
  fillers drew 0 fires in every arm including bm25 — the S4-10 degeneracy fix
  holds under a second trigger-facing surface.

## Controls (separate, engine-independent by construction)

- `team/invocation-corpus-v3-standard/results-control-never-clean/` — trigger
  kill switch: 0/180 fires.
- `team/invocation-corpus-v3-standard/results-control-always-clean/` —
  matches-everything ledger: 134/180 fires.
- These exercise the trigger+fire-log machinery, not any engine's topic set
  (the never control disables the trigger; the always control bypasses engine
  topics with `ALWAYS_SUMMARY`), so they remain valid for every arm above and
  live in separate directories, none of which collides with an engine dir.

## Determinism

Spot-check re-runs (T001–T003, separate `detcheck-*/` dirs) match the full runs
on all invariant fire-log fields (scenario, turn type, fired, reasons, matched
tokens — wall-clock fields `at`/`gap_minutes` excluded) for both
`controlled_core` engines: **9/9 tuples identical each**. All three engines are
deterministic by construction (fixed insert order, SQLite FTS5 rank, seeded
BM25); no metered or non-deterministic arm was run ("deterministic-first").

## Receipts

- corpus v3 sha256 `7395b7d5...a369c0` (verified at run time, fail-closed)
- trigger commit `db31ea3e...f0640e9b5` + `index.ts` sha256 `ec6d8794...fbbdd01` (verified on disk)
- run artifacts (sha256): fts5 `60a694b2...98956c6`, lcm `a89baec9...c67777`,
  bm25 `e825fd75...6a120d5`; per-engine `summary.json` carry the same pins.
- executable declared check: `python3 team/s4-12-crossengine/check_s4_12.py` (rc 0)

## Disclosures for the reviewer

1. The engine-derived-topics protocol is **this row's operationalization** of the
   surface audit's implication 3 (retrieval-mediated: the ledger is fed by what
   the engine's surface yields when queried with the turn prompts). A store-dump
   derivation (ledger = everything the engine stores, regardless of retrieval)
   would be a different instrument; this run does not claim that arm.
2. FirePrecision denominators differ across arms (60 vs 110 vs 114) because the
   denominator is total fires, which is arm-dependent under the S3-1
   pre-registered definition; the definition dispute noted in the S4-10 freeze
   receipt remains open and is not adjudicated here.
3. F3's offtopic-echo count is observational (5/30), reported because the
   standard metric set has no offtopic slot; adding one is a prereg change and
   was not made unilaterally.
4. `agentmemory_core_lsa` (a third `controlled_core` candidate) was probed but
   not run: its vendored Node worker adds a subprocess dependency for a third
   arm the row does not require; noted here for completeness, not omission.

— **kiln-flash**, 2026-09-16 12:01 PDT. $0 local, no score import, controls
separate, verifier corvid-dsh.
