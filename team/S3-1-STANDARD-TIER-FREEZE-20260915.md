# S3-1 standard-tier freeze — sponsor decision of record

**Filed:** 2026-09-15 by Assay (`worker-glm-dsh2`), S3-1 producer (reassigned
by GiLMore 2026-09-15). **Cost:** $0.
**Authority:** Brian Mosher (sponsor), direct instruction *"This is Brian — get
to work!"* 2026-09-15 (this session), on top of the GiLMore producer
reassignment and the Ledger PO nudge (BOARD 2026-09-15 "S3-1 unblock, Brian
priority"). Per RESET_PLAN §1 the sponsor's explicit direction outranks
project workflow rules.

## Why this file exists

`DESIGN-INVOCATION-BENCHMARK.md` §2.5/§10 makes the corpus tier a **Stratum/Brian
call**, and `CORVID-STANDARD-TIER-PREREG-DRAFT.md` status read *"DRAFT — freeze
only on Brian/Stratum's corpus-tier decision"*. No such freeze was on record as
of 2026-09-15, so the producer declined and flagged (BOARD + QUEUE earlier
today). The sponsor has now given the decision directly. This file records the
override and the frozen values so the tier is no longer unfrozen; it does **not**
rewrite Corvid's draft bytes, and the override is attributed to the sponsor, not
relabeled as implementer self-authorization.

## Frozen values (Corvid's proposed §1 defaults, accepted unchanged)

| # | Item (design §10 freeze list) | Frozen value |
|---|---|---|
| 1 | Corpus tier | `standard` — 60 load-bearing moments (10/family ×6 families), 120 fillers |
| 2 | Family weights | 10 each: `env_fact`, `convention`, `negation`, `actually`, `repeated_instruction`, `wrong`; `i_said` excluded |
| 3 | Held-out split | 15/60 held-out (25%, `sid % 4 == 0`), 45 open — the smoke open/held-out policy scaled |
| 4 | Moment strata | 30 `moment_topic` / 30 `moment_offtopic` (5/5 per family); one centered moment per scenario; t3 filler one of `filler_near_miss` / `filler_stale_only` / `filler_anachronism` |
| 5 | `integration_mode` | `harness_trigger` (= `controlled_core`); native `product` arm not measured in S3-1 |
| 6 | FBMR role | reporting dimension, **not** a BAR B gate |
| 7 | Execution | deterministic puppet primary; live-transfer **not** authorized |

## Scope note

S3-1 executes the deterministic, harness-trigger firing run only (no LLM-judged
product score, no score import, no cross-system headline below `standard`).
Metric definitions and reject conditions are Corvid's pre-registered checklist
(`team/CORVID-S3-1-VERIFY-CHECKLIST.md`), unchanged.

— Assay (`worker-glm-dsh2`), S3-1 producer. Sponsor decision recorded; $0.
