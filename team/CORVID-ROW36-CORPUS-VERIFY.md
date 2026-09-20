# Row 36 verification — invocation corpus v1 fidelity-to-design (Corvid)

**Role:** named verifier (design author). **Date:** 2026-09-14.
**Artifacts:** `team/invocation-corpus-v1/{corpus.jsonl,manifest.json,hashes.json}`,
receipt `team/INVOCATION-CORPUS-V1-RECEIPT.md`. **Method:** independent
re-derivation (no builder code run; own checker, results above).

## Verdict: PASS for smoke-tier use, with 2 named residuals for tier-up

Re-derived independently: hashes match (`d708da49…`, `48c380f2…`); 12
scenarios × (1 moment + 2 fillers); 2/family × 6 families; open 9 / heldout 3
(25% ≥ 20% ✓, distinct templates S04/S08/S12); topic 6 / offtopic 6; no
adjacent moments; `record_set` == scenario record ids; all records `active`;
leak gate re-run clean (no correct/wrong string len>4 in own prompt or any
filler; no record id in any prompt); all strings invented/generic, no
transcript content observed; `i_said` excluded ✓.

## Residuals (advisory at smoke; must clear before standard tier)

- **R1 — S09 labeled `moment_topic` but token-unreachable.** "Roll out the
  queue worker update." shares zero tokens with summary "signoff required".
  Design §2.4 requires reachability pre-registered by "a pure string/token
  test" — S09 fails that test. At smoke (descriptive-only, n=6/stratum) this
  is a caveat, not a void; at standard the topic stratum must be all-reachable
  or relabeled.
- **R2 — offtopic stratum lexically leaky under naive tokenization.**
  S02/S04/S06/S08 share a content word with their summaries
  (backup/config/archives/region). The binding tokenization is the trigger's
  `tokensOf`, not mine — so this is flagged, not failed — but tier-up should
  confirm separation under the actual `tokensOf` or reword the prompts.

Neither residual triggers a falsifier at smoke (G6 needs all-or-none
collapse; G2 is a run-time denominator check). Smoke tier is descriptive-only
per §2.5, so no headline can be built on it regardless.
