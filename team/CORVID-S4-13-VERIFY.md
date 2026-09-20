# CORVID-S4-13-VERIFY.md — corvid-dsh verification of QUEUE row S4-13

**Verdict: PASS** — 2026-09-16 13:46 PDT. kiln-flash authored; corvid-dsh
verifies (independence holds).

## Declared check

`python3 team/s4-13-outcome/check_s4_13.py` → `0 findings`, rc 0. The check
re-executes both runners (`m4_replay.py`, `m124_window_table.py`) and
byte-diffs their outputs against the committed artifacts on every key except
`generated_at_utc`; gates the frozen bundle sha, exactly-once replay (286),
RI dedup (26→1), window equality with `team/WINDOW-campaign-1.json`, exact
reproduction of the S4-9 cross-check values, 122 table rows, and receipt
citations.

## Independent recomputation from primary sources (beyond the check)

- **Frozen bundle re-hashed this pass:** `events.jsonl` sha256
  `88f875e7…95d10` — matches the pin.
- **Calibration (part a):** raw classes 169/61/26/21/9 ✓; 286 events, 286
  unique ids (exactly-once) ✓; RI 26 events → 1 group (size 26) ✓; high-conf
  band 235 = negation 61 + actually 21 + wrong 9 + env_fact 143 ✓, and the
  band rule is explicitly declared in the JSON (`env_fact_correction` only if
  not quoted_speech) — F1 (detector confidence flat 0.0) is disclosed, not
  hidden.
- **M4 window overlap recounted from raw events:** exactly 5 bundle events
  inside the declared window — 4 `env_fact_correction` + 1
  `repeated_instruction` ✓ (F2's small-overlap caveat is honest).
- **M1 recomputed from S4-9's primary `pairs.json`** (n=122), bypassing
  kiln's outputs entirely: median token_delta_pct **80.739**, wall **149.233**
  (the claimed exact S4-9 cross-check); median token log-ratio **0.5918**
  (×1.81), wall **0.9132** (×2.49) — all four match the summary to the
  printed precision.

## Contract compliance

- Descriptive-only framing held throughout; **no score import**; pilot
  precision carried beside counts per the spec's "unmeasured precision is a
  claim" rule.
- Absent-vs-zero distinction respected (M2's undetectable kinds reported as
  absent, never zero); M3 declared not instrumented rather than invented
  (fuzzy matching stays `exploratory_only` per the spec); M4 window-level
  only, per-pair attribution impossible by construction and never imputed.
- F3 correctly quarantines the 13-vs-4 M2 direction from any memory-harm
  reading.
- Provenance pins fail-closed and verified: bundle sha, window file, S4-9
  frozen input manifest, pairs.json, and the pairing machinery imported
  read-only from the S4-9 code itself (no re-implementation).

## Caveats (non-blocking)

- All numbers are first descriptive numbers over one window/bundle; the
  receipt itself scopes them as such. The M1 token ×1.81 / wall ×2.49 figures
  reproduce S4-9's corrected-window report exactly — consistency, not new
  evidence.

Row S4-13 moves done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 13:46 PDT.
