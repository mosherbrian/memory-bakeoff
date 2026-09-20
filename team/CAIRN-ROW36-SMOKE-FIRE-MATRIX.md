# Row 36 corpus — offline smoke fire-decision matrix (PREP, second seat, goal 2)

**Seat:** Cairn (worker-pi) · **Date:** 2026-09-14 ~12:2x PDT · **Cost:** $0, local, read-only
**Status:** PREP — fire-decision table only. **No FBMR or other metric is claimed**
(S09 gate from `CAIRN-ROW36-TRIGGER-CHECK.md` stands: no FBMR_topic until S09 is
fixed or relabelled). Committed corpus untouched; nothing run through a live pi
process (the S4 fire log is not polluted with synthetic prompts).

## Method

Deterministic replay of the binding trigger logic (Python re-implementation of
`tokensOf`/`topicMatches`, verified line-by-line against
`implementer/repo/extensions/pi-change-trigger/index.ts`) over all 36 turns,
assuming the design's per-scenario fresh process (turn 1 = `fresh` fire; `gap`
cannot fire at smoke cadence). Topic set = the scenario's record summaries only.

## Fire-decision matrix (36 turns)

| scen | t1 filler_plain | t2 moment | t3 filler |
|---|---|---|---|
| S01 | fresh | topic: service,port | — |
| S02 | fresh | — (offtopic, correct) | — |
| S03 | fresh | topic: results | — |
| S04 | fresh | — (offtopic, correct) | — |
| S05 | fresh | topic: deploy,legacy | **topic: deploy** ← see F2 |
| S06 | fresh | — (offtopic, correct) | — |
| S07 | fresh | topic: retry | — |
| S08 | fresh | — (offtopic, correct) | — |
| S09 | fresh | **— (labeled topic, cannot fire)** ← F1 | — |
| S10 | fresh | — (offtopic, correct) | — |
| S11 | fresh | topic: restart | — |
| S12 | fresh | — (offtopic, correct) | — |

Totals: 12 fresh (t1 ×12), 6 topic fires on moments (S01/S03/S05/S07/S09-missing/S11
→ 5 of 6 labeled topic moments), 1 topic fire on a filler (S05 t3), 17 turns no-fire.

## Findings

**F1 (known, gated):** S09 moment cannot fire on topic — structurally unfireable,
guaranteed FBMR miss if counted as labeled. Fix proposed in the trigger-check
receipt; builder's call.

**F2 (RESOLVED 2026-09-14 ~16:5x by the design seat — Corvid,
`team/CORVID-ROW36-F2-DISPOSITION.md`):** reading (a) stands — S05 t3 is a
by-design hard negative (record shares only subject token `deploy`, does not
govern the choice = the design's `filler_near_miss` definition). No corpus
change. Run-plan requirements now fixed: pre-register expected near-miss fire
count = **exactly 1** (S05 t3, `matchedTokens=[deploy]`) as a positive control
for the trigger's token blindness; report `NearMissFire` with its denominator
`|filler_near_miss|` beside `FirePrecision`; do NOT fold near-miss fires into
`FalseFire` (denominator = `filler_plain` only); label the turn
`near_miss_fire` in the per-turn dump.

**F3 (note):** offtopic moments (S02/S04/S06/S08/S10/S12) all correctly no-fire on
topic — the AvoidRate material is clean under the binding trigger.

## Differential validation vs the real trigger code (added ~12:3x PDT)

The matrix above was produced by a Python re-implementation. Closed the fidelity
gap by driving the **actual TS code** — `evaluateFire` (pure exported function,
`extensions/pi-change-trigger/index.ts:153`) via `bun`, per-scenario topic set
built with the real `tokensOf` over record summaries, `isFirstPrompt = (turn==1)`,
`minutesSinceLastPrompt = null` (gap cannot fire at smoke cadence). No LLM, no
process, no fire-log write (`evaluateFire` is pure; logging lives in the
extension's event handler, not invoked).

**Result: 36/36 rows identical** — every `fired`, `reasons`, and `matchedTokens`
value agrees with the Python matrix, including S05 t3 (`topic: deploy`) and
S09 t2 (no fire). The matrix is now validated against the real instrument code;
a live-process smoke would add only process-integration evidence, not decision
logic. Repro: `team/cairn-diff-check.ts` (`bun team/cairn-diff-check.ts` — imports the
extension by absolute path, iterates corpus.jsonl, prints the 36 per-turn
decisions) — rerunnable as written, verified this tick.

## Consequence

Gate state (updated 2026-09-14 ~17:1x PDT): F2 CLOSED (Corvid disposition —
S05 t3 by-design hard negative, run-plan requirements fixed). F1 (S09) still
open: the corpus still reads `Ship the queue worker rollout` and Corvid's
binding-reachability guard (`team/CORVID-ROW36-REACHABILITY-GUARD.md`, rev 2)
reports exactly that one finding (re-run from my seat: rc=1, single finding,
no false positives on the other 11 scenarios; rev-2 filler rules clean — 6
offtopic moments binding-quiet, exactly 1 near-miss fire = S05 t3, the
F2-expected positive control). The guard is NOT yet wired into the corpus
selftest (still naive overlap) — Corvid marks wiring as an owner/QUEUE
decision. Sequence per Corvid: S09 fix (worker-glm-2) → guard green → wire +
map rev 20. Until then this matrix is the prep artifact; no metric travels
from it.

No S4/S5 figures in this note.
