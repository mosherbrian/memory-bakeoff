# CORVID-S4-14-VERIFY — independent verification of QUEUE row S4-14

**Verifier:** corvid-dsh (GLM-5.3-Flash via ZCode). Did not author the row;
producer is kiln-flash. **Date:** 2026-09-16 ~17:00 PDT. **Cost:** $0, read-only
plus re-computation; no engine re-run, no result directories touched.

**Verdict: PASS.**

## What was re-derived independently (not taken from the producer's checker)

1. **All six metrics recomputed from raw `results.jsonl` under the frozen S3-1
   definitions** (`team/invocation-corpus-v3-standard/run_standard.py::metrics`,
   read this turn): FBMR_topic 7/30 / 30/30 / 30/30, FalseFire 0/60 ×3,
   NearMissFire 10/24 / 24/24 / 24/24, FirePrecision 7/79 / 30/119 / 30/119,
   fresh_rate 60/60 ×3, gap_rate 0/60 ×3 — exact match to the claimed values for
   all three corrected arms.
2. **Table == summary.json == recomputation.** `gen_summary_s14.py` reads every
   number from summary.json on disk (old arms from the S4-12 record
   `team/s4-12-crossengine/results-*/summary.json`); old-arm cells match S4-12's
   stored summaries exactly (0/30, 0/30, 25/30; 25/110; 20/24). Nothing is
   hand-transcribed.
3. **Companion check `check_s4_14.py` rc 0, 0 findings** — and the checker
   itself was audited, not just run: it substantively verifies 4-file pin drift
   (trigger index.ts, pi-project-recall index.ts, both provider adapters),
   frozen corpus sha (7395b7d5…), per-run failure counts, T001–T003 determinism,
   control separation + counts, the zero-demonstration row rule, and required
   summary tokens (iteration-1 anchors 0.2227 / 0.208 / 0.958 included).
4. **A/B byte-identity:** claude-mem window-on vs window-off identical on all
   180 invariant-field tuples (scenario, turn_type, turn, prompt_sha256,
   prompt_len, fired, reasons, matched_tokens, gap_minutes).
5. **Determinism:** T001–T003 invariant tuples identical full-vs-detcheck for
   all 3 arms — the declared protocol's spot-check scope, same as S4-12.
6. **Controls recomputed from their results.jsonl:** never 0/180, always
   134/180; dirs distinct from every engine dir.
7. **F4 zero-demonstration annex:** pi arm `topics-derivation.jsonl` has 180
   derivation turns, 23 non-empty across 19/60 scenarios (matches the table),
   `tool_level` audit on every turn, 157 audited-empty
   (`exact_nonempty: false, relaxed_with: null`).
8. **F1 mechanism claims:** pi topic-fire scenario set is exactly
   {T021, T027, T031, T033, T035, T037, T039}; matched tokens across fires are
   deploy×9, mode×6, service×2, billing-100×1 (+ billing-103/106/109 and
   filler-side tokens) — consistent with the claimed rescue mechanisms.
9. **F2 rescue distribution exact:** relaxed_with = to×10, mode×4, deploy×4,
   101./103./105./107./109. ×1 each.
10. **"Verbatim port" audited:** `relaxed_variants` in run_s4_14.py is
    semantically identical to the pinned `relaxedVariants`
    (extensions/pi-project-recall/index.ts:121-133 @9025eef5…): same
    progressive trailing-drop keeping ≥2 terms, then single tokens last-first,
    same 6-attempt cap, same tokenization semantics.
11. **Declared adaptation documented** in the runner docstring and summary
    §What-changed (single-session gate port: exact AND first, relaxed variants
    only on empty, else exact empty stands unmarked).
12. **Re-measurement rule (Brian, 2026-09-16) satisfied:** prior measurements
    are cited and reported side by side — S4-12's numbers with their artifacts,
    plus the iteration-1 anchors labelled by instrument with an explicit
    not-same-instrument caveat.
13. **rowcheck S4-14 --json:** rc 0, status_declares_done true, 0 findings.

## Notes (non-blocking)

- F3's "every record sits inside the window" is correct because the modeled
  window is a **lower bound only** (claude_mem_core.py: `start = eval_now −
  90d`; drop when `r.timestamp < start`). Records stamped 2026-09-01 vs
  eval_now 2026-08-30 pass trivially. Cite the byte-identity as the measured
  fact; do not read "inside" as a two-sided bound.
- Determinism is a spot-check by declared protocol (T001–T003), not a
  full-corpus re-run — same scope S4-12 used and the row asked for.
- FirePrecision denominators (119/79) are run-dependent by the pre-registered
  definition; the summary says so. 30/119 vs 7/79 is not comparable as a ratio
  across arms without that caveat.
