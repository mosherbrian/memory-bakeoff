# R4-task-1 — independent task-selection review (contract validity + design)

- **Reviewer:** corvid-dsh. **Baseline recorded before author conclusions:**
  from the package inputs and primary `team/QUEUE.md` rows, I independently
  expected a real, bounded, runnable task with a pinned before-artifact and an
  executable check. Row `S13-2` (QUEUE line 219) and gate row `S13-2G`
  (line 220) name a standing fix request; `team/CORVID-S13-2G-VERIFY.md`
  (round-2 `VERIFIED FAIL`) is the spec; the gate file is
  `team/S13-STATEUPD-AUDIT/check.py`. I verified these primaries directly.
- **Worker claim:** `ex-R4-task-1-w1.json`; hashes verified equal —
  `task-card.md` `eec3665d…`, `sources.json` `8965f6b1…` (568 words ≤1000).
- **Verdict: PASS — task selection only, not run authority.** The selected task
  is genuinely useful work (a runnable gate repair), correctly grounded in
  behavior, with fair tool access and no clean-holdout overclaim.

## Eight points

1. **Real request / why it matters — passes.** Primary: QUEUE `S13-2`
   (audit external state-update mechanisms; moves ANSWER Q4) and `S13-2G`
   (write/repair its check), plus `CORVID-S13-2G-VERIFY.md` returning the gate
   twice. A blocked, green-selftest gate that rejects honest audits is exactly
   the recurring gate-repair work; unblocking it matters to real audit work.
2. **Actual paths/hashes + runnable or missing check — passes.** I confirmed
   `team/S13-STATEUPD-AUDIT/check.py` is present, **untracked**, 40,851 bytes,
   sha256 `8c921fbb…` (matches `sources.json` and QUEUE round-2), and the review
   is `bf8d2599…` at commit `22c995f`. The check **runs**: I executed
   `python3 check.py --selftest` → rc 0, "accepted both conforming fixtures;
   rejected 27 independent non-conforming fixtures …" (read-only, tempdir; no
   repo mutation). No blocking missing prerequisite.
3. **Success check is behavior, not recall/retrieval — passes.** `--selftest`
   rc 0; an honest receipt (genuine mechanisms only) must not raise
   `CANDIDATE_SECTION_COUNT`; the 27 named negatives must still fail. Acceptance
   artifact = the review's Fix 1–3 list. The card states the check was **not**
   run and must be executed, not asserted.
4. **Remembered constraint, identical for both arms, ordinary tools retained —
   passes.** Constraint: keep all existing machinery and add a real-heading
   selftest fixture (the shared S12-1G/S13-1G/S13-2G failure class). Both arms
   get the same file, card and tools; the memory arm additionally gets the
   pinned review/failure records. Completion is an independently executable
   check, so no answer key leaks.
5. **Forward differentiation without denying tools — passes.** Control = gate +
   card + python3/git; memory = plus review + prior failure records. No arm is
   denied ordinary repository access.
6. **Real boundary requirements — passes.** The card states no session/
   compaction boundary is needed for selection and that a later run would
   require observed boundary records (state hashes across restart), none of
   which exist yet; no boundary claim is made.
7. **Contamination / seen-solution — passes.** The card discloses it read the
   verifier's fix spec and the S12/S13 failure pattern (not the gate
   implementation) and scopes this as a **feasibility pilot on a seen-spec
   task**, explicitly not an unseen-task trial; a later unbiased run must use
   unseen tasks. No clean-holdout claim.
8. **Scope/time limits and next action — passes.** Selection only (~25 min
   inspection); no code written, no check run by the author; next smallest
   action = Tern authorizes a bounded implementation round with Fix 1–3 as
   acceptance, or records no-go. No efficacy claim; no memory system chosen.

## Limits (not defects)

- The task examines a fleet gate-repair kind of work in this repo, not a
  personal coding session; within the package's allowed sources, but the
  `for_brian` outcome should say so plainly.
- The gate file is untracked, so the before-artifact can be lost if not
  committed; the run should pin/commit it before mutating.
- The two rejected candidates are documented in `sources.json`
  (agent-loop P13: no crisp bounded check; conductor: another lane's
  in-flight work); reasonable exclusions.

No experiment, no code edits; the author's artifacts were not modified.

*Reviewed: `package.md`, `inputs.json`, `task-card.md` (`eec3665d…`),
`sources.json` (`8965f6b1…`), `team/CORVID-S13-2G-VERIFY.md` (`bf8d2599…`@22c995f),
`team/S13-STATEUPD-AUDIT/check.py` (`8c921fbb…`, `--selftest` rc0),
`team/QUEUE.md` rows S13-2/S13-2G.*
