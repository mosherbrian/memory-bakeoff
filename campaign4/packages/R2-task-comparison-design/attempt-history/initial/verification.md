# R2-design-1 — independent verification

- **Verifier:** corvid-dsh (author kiln; not the verifier). **Baseline recorded
  first**: `review-baseline.md`, written before opening author output;
  historical exposure disclosed, no claimed fresh-session blindness.
- **Worker claim:** `ex-R2-design-1-w1.json` (`completed`); hashes verified
  equal — `design.md` `f39b0698…`, `feasibility.tsv` `9bf5d991…`.
- **Verdict: INCOMPLETE (outcome failed).** The design is substantively strong
  and mostly meets the six admission conditions, but two feasibility claims are
  not established from the record: the corpus is not actually pinned, and an
  existing executable task-outcome corpus was not inspected or excluded. Both
  are correctable without a new experiment.

## Six admission conditions

1. **Treatment path+hash+reversible disable — passes.** `ClaudeMemFTS5CoreProvider`
   is real at `implementer/repo-kiln-flash/src/memory_bakeoff/providers/claude_mem_core.py`
   (`53199f68…`, stdlib `sqlite3`, `class ClaudeMemFTS5CoreProvider` at line 42);
   commit `be2bfa9` resolves in that nested repo. Control = no provider + empty
   memory dir, same model/prompts. Reasonable.
2. **Task pool/rubric grounded in task completion — partial (defect D2).** The
   rubric is task completion (blind exact-match vs frozen expected answers),
   not retrieval; secondary evidence delivery is properly secondary. But the
   design asserts the pool "does not exist yet" without inspecting the
   **existing executable action-outcome corpora** — `team/invocation-corpus-v2-standard/`
   and `-v3-standard/` (60 scenarios each, `correct_action_set`/`wrong_action_set`,
   `run_standard.py`, results/controls; `manifest.json` `18cfe106…`) and
   `team/outcome-pilot-bundle-20260914/` (`7cd03aa5…`). Neither `design.md` nor
   `feasibility.tsv` cites them. This is the incomplete-search case the task
   flags, not a supported no-go.
3. **No proxy as primary outcome — passes.** FTS5/retrieval/abstention and
   P9/expose are explicitly excluded; null is "no detected difference at n=20",
   never proof.
4. **Freeze before outcome access — passes.** Choices, pool rules and exclusions
   are declared frozen; order randomized; calibration gate before the pool is
   accepted.
5. **Boundary/confounds/stops — passes, honestly scoped.** Session restart is
   the observed boundary; compaction is explicitly **excluded** (consistent with
   R1's `compaction_measured: false`); fixed n=20, no early stopping, interim
   check for missing data only; confounds listed.
6. **No build/study — passes.** Design only; no run, install, or web/model work.

## Defects

- **D1 — "corpus pinned" is not true (feasibility row `corpus pinned: ready`).**
  `ai-notes/` is its own repo and `be6cc97` resolves, but the corpus files are
  **untracked** there (`git ls-files claude-memory` = 0), so the commit does not
  pin their bytes. The design then ships **no per-file hashes**, yet its no-go
  branch keys on "corpus hash differs from the pins above" — a vacuous check.
  The glob is also inconsistent: `feedback_*.md` is **21** files, not the "79
  files" stated (79 is the count of all `*.md` in the dir; 512K matches). The
  corpus must be frozen by per-file sha256 (computable, e.g.
  `feedback_use_the_real_input.md` `62b16524…`) and the glob made exact.
- **D2 — incomplete local search.** Per above, existing executable
  task-outcome corpora were not considered. Either adopt one as the task pool,
  or record the exact inspected path/hash and the reason it cannot serve the
  contrast. The contract requires naming inspected local artifacts, and a
  "smallest feasible contrast" claim depends on this.

## Strengths retained

Treatment pinned and real; rubric is genuine task completion, not a proxy;
compaction honesty; explicit confounds, effort estimate and stopping rule; null
discipline; alternatives (BM25/S11, transfer, positional) ranked with reasons;
no hidden empirical work; author ≠ verifier.

## Required corrections (no new experiment)

1. Pin the corpus by per-file sha256 and fix the `feedback_*.md` count/glob.
2. Inspect and either use or explicitly exclude `invocation-corpus-v2/v3-standard`
   and `outcome-pilot-bundle-20260914`, recording path+hash and reason.

*Reviewed: `package.md`, `admission-review.md`, `inputs.json`,
`release-decision.json`, `design.md`, `feasibility.tsv`,
`implementer/repo-kiln-flash/.../claude_mem_core.py` (`53199f68…`),
`/var/home/bmosher/ai-notes/claude-memory` (79 `*.md`, 21 `feedback_*`),
`team/invocation-corpus-v{2,3}-standard/*`, `team/outcome-pilot-bundle-20260914/*`,
`team/PROPOSAL-R2-explicit-prompt-habit-v1.md` (`b587b263…`).*
