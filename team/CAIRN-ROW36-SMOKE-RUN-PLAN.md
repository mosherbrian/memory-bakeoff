# Row-36 live smoke — run plan (PRE-REGISTERED, second seat, goal 2)

**Seat:** Cairn (worker-pi) · **Date:** 2026-09-14 ~17:3x PDT · **Cost:** $0 (local model)
**Status:** WIRING VALIDATION COMPLETE 2026-09-14 ~18:3x PDT — **36/36
match** on the current corpus (`--expect pre`), exactly 1 near-miss fire
(S05 t3, `matchedTokens=[deploy]`), 0 filler_plain topic contamination.
Consolidated results: `~/acp-pi/row36-wiring-20260914/results-consolidated.jsonl`.

## Gate

No `FBMR_topic` claim until the S09 fix lands (guard rc=0). This plan and the
wiring-validation run make **no metric claim** — smoke tier is
"instrument wiring + controls only" (DESIGN-INVOCATION-BENCHMARK.md tier table).
The metric run is `--expect post`, executed once after the guard goes green.

## Pre-registered expectations (36 turns)

From `CAIRN-ROW36-SMOKE-FIRE-MATRIX.md` (differentially validated 36/36
against the real `evaluateFire` via bun):

- **t1 (filler_plain) ×12:** fire, reasons exactly `{fresh}` — a `topic`
  reason on any t1 is a control-contamination finding.
- **t2 (moment) ×12:** topic fire with exact matched-token sets for
  S01 {service,port}, S03 {results}, S05 {deploy,legacy}, S07 {retry},
  S11 {restart}; no-fire for S02/S04/S06/S08/S10/S12 (offtopic) and —
  **pre-fix only** — S09 (F1, structurally unfireable as labeled).
- **t3 (filler) ×12:** exactly **one** fire — S05 t3 `matchedTokens=[deploy]`
  (F2 disposition: by-design hard negative, pre-registered positive control
  for token blindness; reported as `NearMissFire` with denominator
  `|filler_near_miss|`, never folded into `FalseFire`); all other t3 no-fire.
- **Post-fix delta (S09, row 42):** t2 fires on topic, matched ⊇ {required}
  (moment → `What is required before the queue worker rollout ships?` per
  `CORVID-ROW42-CORPUS-FIX.md` — my originally-proposed `Get the signoff
  line…` wording leaked `signoff` ∈ correct_action_set and failed the leak
  gate; `required` is the only non-answer summary token).
- `gap` cannot fire at smoke cadence (turns minutes apart, threshold 30 min);
  any `gap` reason is a harness finding.

## Metrics (post-fix run only)

- `FBMR_topic` = topic fires on the 6 labeled topic moments / 6.
- `NearMissFire` = 1 / `|filler_near_miss|` (denominator reported beside it).
- `FirePrecision` = fires on labeled moments + pre-registered near-miss /
  all fires, denominators stated.
- `AvoidRate` material = the 6 offtopic moments + 11 clean fillers, all
  expected no-fire (0 topic fires).

## Isolation (S4 feed protection)

Each scenario runs a fresh `pi --mode rpc --no-session` process with
`PI_CODING_AGENT_DIR` pointed at a throwaway agent dir:

- `settings.json`: packages = [pi-change-trigger] **only** (no
  pi-perseus-recall — the trial vault is never touched by smoke processes);
  `changeTrigger.topicsFile` = per-scenario file (one `{"summary": …}` line
  per corpus record); `changeTrigger.fireLog` = per-scenario file.
- `auth.json` / `models.json` / `models-store.json` are **symlinks** into the
  live trial agent dir (house rule: link, never copy).
- The committed S4 fire log (`~/acp-pi/change-trigger-firelog.jsonl`) is
  never written by the smoke; synthetic prompts never enter it.

## Runner

`~/acp-pi/row36-smoke-run.py` — sequential scenarios (local model, one
process at a time), per-turn comparison of `fired` / `reasons` set /
`matched_tokens` (superset check on tokens, exact on reasons), results to
`<out>/results.jsonl`, exit 0 iff all turns match. `--expect pre|post`
selects the S09 expectation. **v2 (this tick):** each turn is ABORTED as soon
as its firelog line appears (the trigger evaluation is written synchronously
in `before_agent_start`, before the LLM call) — ~4 s/scenario instead of
3.5–7 min, and the smoke agent never runs tools to completion (cwd is a
scratch dir). v1 (wait-for-`agent_settled`) hung on slow local-LLM turns
(S03/S05 hit the 420 s timeout with only t1 logged — protocol artifact, not
a wiring defect; both pass under v2).

## Sequence

1. S09 fix (worker-glm-2) — PENDING apply. **QUEUE row 42 now carries it**
   (proposed by Corvid, design seat): ready-to-apply diff
   `team/CORVID-ROW42-CORPUS-FIX.diff` (S09 moment + binding selftest
   predicate + re-stamped hashes `65ba8592…`). Independently verified from my
   seat in a temp copy (2026-09-14 ~18:4x PDT): fixed selftest ALL GREEN 7/7
   on fixed corpus; probe 0 findings rc 0; power — fixed selftest on the
   UNFIXED corpus FAILs `['S09']` rc 1. Owner applies from `team/`; verifier
   Corvid.
2. Guard green (rc=0) → 3. `row36-smoke-run.py --expect post` (wiring already
   validated 36/36 pre-fix; the post-fix run adds the S09 t2 topic fire) →
   4. metric claims per the table above → 5. Corvid wires the guard into the
   corpus selftest + map rev 20 (owner/QUEUE decision per his guard note).

No S4/S5 figures in this note.
