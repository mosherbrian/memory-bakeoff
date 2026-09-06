**Lead finding: the Gen114 result is sound — I rebuilt the frozen v4 ruler from the current source, re-graded all 60 sealed raw responses byte-for-byte, and every published number (12/12/9+3/12/12 per condition, 9/9 controls per core, Q4 `REPLICATED_ACROSS_CORES`, order effect only in `budget:solstice`) reproduces exactly; no defect invalidates it.**

What was verified, not just claimed:

- Manifests of `results/gen114/attempt1` and `results/gen113/attempt2` verify; all artifact SHA-256s match bytes on disk.
- The frozen contract digest `2bc281b9…` equals the digest rebuilt from the current sources; `verify_contract` passes; worktree is clean at `b905cf7`.
- All 60 request prompts are byte-identical to `project_prompt()` today and match the 20 prompt hashes frozen in the v4 payload.
- Independent re-grade of the raw responses with the frozen parser/classifier/grader: 0 mismatches on outcome, answer class, and citation relation.
- Gen113 attempt1 untouched; attempt2 consumed as declared; grading wrote once (evidence contract refuses overwrite).
- The "192 of 192" Round-3 citation exists in `ROUND3_FINAL_READOUT.md`.

Remaining defects, most severe first:

1. **The executing scripts were untracked at the pinned commit.** `scripts/run_gen114_reader.py` and `scripts/grade_gen114.py` do not exist in commit `b286c21` (first committed in `b905cf7`). The preflight's clean-worktree check filters out `??` untracked lines, and the v4 freeze hashes only the three `reader_interference*` files — so "this exact runner executed" is not hash-attested. Mitigated: all scientific behaviour lives in the hashed files, and the sealed raw evidence plus the frozen ruler independently reproduce the result.
2. **Nondeterminism under "temperature 0, seed 0".** One of 20 cases (`throughput:atlas|CONFLICT_CURRENT_FIRST`) returned different text across repetitions (rep 1 "…fix; 27 t/s" vs rep 2/3 "…fix and 27 t/s"); both grade MIXED, so no count changes, but the settings must not be read as reproducibility. Related: `seed_accepted: true` in the addendum is hardcoded, never read from the server.
3. **Interpretation caveat on two cores.** For `branch:vega` and `oncall:kestrel`, no marker in the record texts distinguishes current from superseded (same scope/configuration wording, no dates), and the questions are value-neutral. "Contradictory" is the frozen contract's label for reporting both values; the measured fact — the reader fails to select the single current value — stands, but "the AI contradicts itself" is a definitional framing for those two cores, not evidence the reader ignored a knowable recency cue.
4. **Environment, not the repo:** the AGENTS.md gate `pytest -q` fails here — 25 collection errors, all `ModuleNotFoundError: sklearn`. Unrelated to Gen114; the five reader-interference test modules pass (184 tests).
