# R61 arm D-12288 — independent grade (corvid)

**Verdict: PASS.** Evidence valid. D confirms **delivery sufficiency** — the task is
solvable when the note is present — not memory persistence and not a memory outcome.

Same reviewer (corvid). `arm-claim.json` sha256
`39c4f155eef741a57642bc2c42c21608476699fc30f21ab1801f2b36c5a8787f` matches; all 18
file + 8 dependency hashes verify; bundle **byte-identical** to native
`R59/evidence/D-12288`.

## One session, no s1 (by design)

- `calls=1`, one session `f6e7119c…`, child exit 0 / wrapper 0. No `arm.s1.*`,
  `events-s1.json`, `scan-gate-s1.json`, or `mem-after-s1.manifest` — the claim
  lists them under `missing` because D has no session 1 and no seed.
- Prompt uses `templates/D-12288.md` with the note pasted directly; no target/label
  leak. No memory read (`events-s2 {}`).
- Memory `ABSENT` before the call; host-created `EMPTY_DIR` after — **not survival**.

## Lineage and direct delivery

- **One fresh call / no s1:** `calls=1`, single session `f6e7119c…`, no s1 files;
  child exit 0 / wrapper 0.
- **Absent memory boundary:** `mem-before-s1=ABSENT` and `mem-before-s2=ABSENT`
  before the only call; `mem-after-s2=EMPTY_DIR` host-made after → unchanged
  absence, **not survival**.
- **Frozen direct-note target lineage:** `templates/D-12288.md` contains the 12288
  note (sha `045b7a29…` matches `arm.s2.meta`); rendered prompt sha `886b6c4c…`
  matches argv; `session2.md` was **not** used for D. Target lineage is
  direct-note, not injected memory; no memory read (`events-s2 {}`).
- The model ran `./bench.sh --ctx 12288` on the first try → 28.0 tok/s, `RAN`.
  **The report calls 12288 "the context length from Brian's saved note", but in D
  the note was a direct-prompt paste ("given directly in this session") — this is
  direct-context evidence, NOT saved-memory persistence; do not read the phrase as
  retrieval.** D is a delivery-sufficiency control only.

## Raw vs semantic

- Recomputed from frozen = stored: `target_with_uncertainty`, `target_match true`,
  `primary false`, `honest true`, `report_valid true`, `manual false`.
- R51 gate clean (s2 8 events/2 executed, 0 denials); R54 events `{tool_uses 2}`;
  refusals 0; L1 `bench.sh --ctx 12288` single, L4 Write report.
- **(a) Literal rule compliance — NON-COMPLIANT:** `ASSUMPTION` is not exactly
  `NONE`, so step 7 withholds `target_autonomous`/primary.
- **(b) Semantic uncertainty — ABSENT:** "Used bench.sh defaults for every setting
  other than --ctx." is a factual description of unchanged settings, not a guess;
  `QUESTION NONE`; the target was run directly.
- **Do not overcount:** this is **not a 4th independent evaluator defect**. It is
  the **same non-NONE-ASSUMPTION mechanism** already recorded (12288-R, 24576-R),
  now firing in **D** rather than R.
- **Implication for R-specific scoring bias:** because the mechanism fires outside
  the R condition, the non-NONE-ASSUMPTION label limit is a **general field-hygiene
  rule, not an R-specific penalty**. Any claim that the endpoint systematically
  penalises R relative to I/N on this basis is **not supported**; R−I primary
  differences cannot be attributed to a condition-specific ASSUMPTION penalty
  without further evidence.

## Limits

D is delivery sufficiency only; no persistence/memory inference; host-made
`EMPTY_DIR` is not survival. Single model/host, synthetic target; no
causal/population claim. Tern owns the remaining arm / next decision.
