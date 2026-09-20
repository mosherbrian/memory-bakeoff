# S4-13 — Outcome measurement receipt: M4 calibration + first M1–M4 table

**Row:** QUEUE S4-13 (Sprint-4 order 6; (a) gated on nothing, (b) gated on S4-9 — satisfied)
**Author:** kiln-flash (sole doer) · **Date:** 2026-09-16 ~12:18 PDT (stamp bracketed by measured date calls) · **Cost:** $0, all local
**Verifier:** corvid-dsh (uninvolved-seat repro per SPEC §5: re-run
`team/s4-13-outcome/check_s4_13.py`, which re-executes both runners and diffs
every output key except the generation timestamp)
**Ceiling:** descriptive first numbers; **no score import**; no metered arm.

## Provenance pins (all verified at run time, fail-closed)

| Artifact | Pin |
|---|---|
| Frozen outcome bundle | `team/outcome-bundle-scale-20260915/events.jsonl` sha256 `88f875e7a7eb94663033d4a0dc684537486266ea3d51099ad945394f50095d10` (Cairn PASS, `gate_findings: []`) |
| Declared window | `team/WINDOW-campaign-1.json` — 2026-09-12T18:05:00Z → 2026-09-16T07:00:00Z |
| S4-9 frozen input | `~/acp-pi/s5-final-windowfix-20260916/frozen-input/INPUT-MANIFEST.json` sha256 `0f89ca5a…303ee` (the S4-9 declaration) |
| S4-9 rerun pairs | `…/run/pairs.json` sha256 `ce944879…d5f23` (n=122 pairs, generated 2026-09-16T17:18:39Z) |
| Pairing machinery | `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing.py`, imported read-only — the S4-9 code itself, not a re-implementation |

## Part (a) — M4 replay/calibration (`team/s4-13-outcome/calibration.json`)

Harness self-test PASS first (6 synthetic fixtures: exactly-once, RI dedup
3→1, band edges, duplicate-id catch, class attribution driven by event
content), then the real bundle:

- **Replay (SPEC §5.3.2):** 286 events consumed, **286 unique ids, counted
  exactly once**, class attribution exact. Harness findings: none.
- **Repeated-instruction de-dup (the spec's anti-gaming rule):** 26 RI events
  collapse to **1 repeat group** (all sharing one `normalized_prefix_hash`,
  consistency-checked). Raw 286 → 261 unique correction instances.
- **Calibration (§5.3.1), raw counts:** `env_fact_correction` 169,
  `negation` 61, `repeated_instruction` 26, `actually` 21, `wrong` 9 —
  reconciles to the gate receipt and README class counts.
- **High-confidence band (DECLARED rule, see finding F1):** 235 =
  negation 61 + actually 21 + wrong 9 + env_fact 143 (the 169 minus **26
  quoted-speech** events — the pilot's residual-noise class) + 1 RI group.
- **Precision carried beside counts (spec rule: an unmeasured precision is a
  claim):** pilot estimates quoted from SPEC §3 via
  `TRANSCRIPT-MINING-PILOT.md` — negation/actually ≈1.00, env_fact ≈5/7,
  wrong/facts ≈0.85–0.90.
- 5 distinct project pseudonyms; hourly buckets 2026-07-27T20 …
  2026-09-13T17.

## Part (b) — first M1–M4 table over the corrected window (`m124-window-summary.json`, `m124-window-table.md`)

Descriptive, per SPEC §3.1/§7; one row per pair, n=122:

- **M1 — time-to-complete** (tokens primary, wall beside):
  median per-pair **log-ratio 0.5918** (IQR 0.079–1.1312) ≈ ×1.81 tokens;
  wall **0.9132** (IQR 0.6498–2.4852) ≈ ×2.49. Cross-check: median pct
  deltas recomputed from `pairs.json` are **80.739% / 149.233%** — exactly
  the S4-9 corrected-window report values. Pooled by 5 families in the
  summary JSON.
- **M2 — errors committed:** detectable kind "non-zero-exit command used as
  a task step" (`toolResult.isError`), attributed to in-progress turns by
  the S4-9 turn builder itself: **13 memory-arm vs 4 no-memory-arm** across
  122 pairs (14 pairs with any error); 1,143 turns built from the 37 frozen
  sessions. The other frozen M2 kinds (reverted edit, wrong-scope write,
  test/CI failure, broken build) are **not detectable in this session
  shape** — reported as absent, never as zero.
- **M3 — redundant re-discovery:** **not instrumented this pass.** Needs
  record-state-at-start plus delivered-level matching; fuzzy matching is
  `exploratory_only` per the spec and was not invented. Column marked, not
  imputed.
- **M4 — operator corrections:** window-level only — the bundle's corpus
  (claude-code projects, opaque pseudonyms) is disjoint from the S5 trial
  lanes, so per-pair attribution is impossible by construction and is never
  imputed. **5 bundle events fall inside the declared window** (4
  `env_fact_correction`, 1 `repeated_instruction`) out of 286 total.

## Findings and limits

- **F1 — the v1 detector's confidence field is flat 0.0** across all 286
  events, so "high-confidence-only" cannot come from the detector's own
  confidence. The band used is **class+structure-derived** (quoted-speech
  flag as the quote-aware signal) under the spec's own pilot precision
  numbers, and the rule is declared in `m4_replay.py` and in the calibration
  JSON. A calibrated confidence belongs in the next detector version.
- **F2 — small window overlap:** only 5 bundle events fall in the S4-9
  window; the window-level M4 row is a first number, not a rate.
- **F3 — M2 direction is descriptive only** (13 vs 4 across 122 pairs, one
  detectable kind); it must not be read as a memory-harm result.
- The bundle remains the window-independent calibration set; window filtering
  is done only for the M4 row and does not touch part (a).

## Repro (uninvolved seat)

`python3 team/s4-13-outcome/check_s4_13.py` re-runs both runners, verifies
every pin and cross-check, and diffs the outputs against the committed
artifacts (all keys except `generated_at_utc`). rc 0 required.

— **kiln-flash**, 2026-09-16 ~12:18 PDT. $0 local; no score import; verifier
corvid-dsh.
