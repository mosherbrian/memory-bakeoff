# Row-36 smoke — post-fix run results (goal 2, second seat)

**Seat:** Cairn (worker-pi) · **Date:** 2026-09-14 ~18:4x PDT · **Cost:** $0 (local model)
**Corpus:** post-fix `invocation-corpus-v1` (corpus `65ba8592…`, row 42 applied
byte-identical, selftest ALL GREEN 7/7, probe rc 0 — gate clear).
**Runner:** `~/acp-pi/row36-smoke-run.py` v2 (`--expect post`), isolated agent
dirs — the committed S4 fire log was never written by this run.
**Results:** `/tmp/row36-postfix-1842/results.jsonl` (36 turns).

## Verdict vs pre-registration

**36/36 match** against the pre-registered expectations
(`CAIRN-ROW36-SMOKE-RUN-PLAN.md`), including the post-fix delta: S09 t2 fires
on topic, `matchedTokens=[required]` (exactly the pre-registered ⊇ {required}).

## Controls (the smoke-tier claim)

| control | result |
|---|---|
| fresh (t1 ×12) | 12/12 fire, reasons exactly `{fresh}`, 0 topic contamination |
| offtopic stratum (moment_offtopic ×6) | 0/6 fires |
| near-miss positive control | exactly 1 fire — S05 t3 `matchedTokens=[deploy]` (pre-registered) |
| gap | 0 fires (smoke cadence < 30 min, as designed) |

## Rates (DESCRIPTIVE — smoke tier, not a headline)

Per DESIGN-INVOCATION-BENCHMARK §2.5: smoke tier is "instrument wiring +
controls only; no per-system claim"; "any headline below `standard` is
descriptive only." Denominators per §4.5.

| metric | value | denominator |
|---|---|---|
| FBMR_topic | 6/6 | \|L\| = 6 labeled topic moments (fire at `before_agent_start`, before action) |
| NearMissFire | 1/3 | \|filler_near_miss\| = 3 (S01/S05/S09 t3) |
| FirePrecision | 6/19 | fired turns = 19 (12 fresh + 6 topic + 1 near-miss); load-bearing fired = 6 |
| FalseFire (literal §4.3, incl. fresh) | 12/15 | \|filler_plain\| = 15 (12 t1 + S04/S08/S12 t3) |
| fresh_rate / gap_rate (beside primary, §4.1) | 12/12 t1 / 0 | process artifacts, excluded from primary |

CBMR / AvoidRate / ExplicitBefore: not measurable in a wiring smoke (no
delivery/context instrumentation, agent actions unscored) — N/A at this tier.

## Fresh-in-FalseFire — RULED (design seat, 2026-09-14)

**Ruling:** fresh/gap are EXCLUDED from FalseFire — the shipping definition is
`fired(topic) on filler_plain / |filler_plain|`, with `fresh_rate` 12/12 and
`gap_rate` 0 reported beside (per `CORVID-STANDARD-TIER-PREREG-DRAFT.md` §2,
"the two smoke rulings"). Under the ruling, this run's FalseFire is **0/15**;
the literal §4.3 value (12/15) is retained above for the audit trail. The
ruling sits inside the standard-tier pre-reg draft, which freezes only on
Brian/Stratum's corpus-tier decision (§2.5).

**RULING (Corvid, design seat, 2026-09-14):** fresh (and gap) are process
artifacts and are **excluded from FalseFire** per §4.1 — the standard-tier run
**ships `FalseFire = 0/15`** (topic fires on `filler_plain` only), with the
literal 12/15 labeled the process-artifact-inclusive form and not shipped, and
§4.3's `fired(fresh|gap|topic)` corrected to `fired(topic)` with `fresh_rate`/
`gap_rate` reported beside the primary (the `fire-always` control still reads
`FalseFire=1`).

## Gate sequence status

F1 landed (row 42) · F2 closed · wiring validated pre-fix 36/36 · post-fix
36/36 · **invocation-side smoke is DONE at the smoke tier.** Remaining per the
run plan: map rev 20 wiring (owner/QUEUE item; probe→selftest done via row
42). Standard tier (60 moments) is the minimum for a per-system headline —
**pre-reg draft is ready** (`CORVID-STANDARD-TIER-PREREG-DRAFT.md`, design
seat): tier/corpus build, frozen metric definitions incl. the two smoke
rulings, required instrument controls, decision rule; freezes only on
Brian/Stratum's corpus-tier decision per §2.5.

No S4/S5 figures in this note (the S4 fire log is untouched by this run).
