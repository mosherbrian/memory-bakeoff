# R4-task-repair-1 — independent parity recheck

- **Reviewer:** corvid-dsh. **Initial PASS preserved** at
  `attempt-history/initial/verification.md` (plus initial `task-card.md`,
  `sources.json`); this verdict concerns the repaired card only.
- **Worker claim:** `ex-R4-task-repair-1-w1.json`; hashes verified equal —
  `task-card.md` `93e777e8…` (repaired), `sources.json` `8965f6b1…` (unchanged).
- **Verdict: PASS.** The director's parity defect is fixed: both arms now get
  identical instructions, tools and repository, and the only proposed
  difference is memory of the arm's own prior-session materials across an
  explicitly specified, observable boundary — not extra answer information.

## The defect and its fix

Initial card §5 denied control the fix spec while giving it to the memory arm:
that made the treatment "extra instructions," not memory. The repaired card
reverses this correctly:

- **§4 "identical for both arms":** both arms receive the IDENTICAL task card,
  including the full fix specification (Fix 1–3) and normal repository access
  (python3, git, the gate file, prior reviews). It states the acceptance
  criteria "cannot be the memory treatment" — withholding them would make
  control do a different task. The historical constraint is seen by both arms
  at task start, equal timing "by construction, recorded in the run log."
- **§5 "what memory-only persistence/retrieval differs":** the sole systematic
  difference is runtime persistence across the task's own sessions (memory arm
  retains/retrieves its own earlier attempts, notes, failure records from THIS
  task; control starts without them) — same task, spec, tools and model. It
  plainly states the executable check cannot distinguish "derived
  independently" from "recalled the specification," and that shared-spec
  leakage is not prevented; the contrast measures only whether own-prior-session
  retrieval changes the completion outcome.
- **§6 observable end/start:** no boundary is claimed yet; it specifies the
  observables to collect later — end = the seat's file/byte inventory with
  sha256 in session N; start = session N+1's logged reads of those files (or
  their absence for control); continuity holds iff the start inventory matches
  the end for memory and is empty for control; a missing record means the
  boundary was not observed for that pair. Compaction remains excluded.

## Dispatch checks

- **Identical instructions/tools/repository — passes** (§4, explicit).
- **Difference is memory over a specified observable boundary, not extra
  answer information — passes** (§4–§6; the fix spec is given to both, the
  treatment is own-prior-session persistence, and the end/start observables are
  named).
- **No claim of executed boundary or efficacy — passes** (§6 "No boundary is
  claimed yet"; §8 "Efficacy of memory is not claimed"). Concrete
  prerequisite/no-go preserved as the alternative (§8).
- **Task usefulness and source checks retained — passes:** §1–§3 unchanged
  (S13-2G repair, `check.py` `8c921fbb…`, behavior check via `--selftest` +
  honest-receipt probes, 27 negatives; author did not run it).

## Limits (not defects)

- The work product (the gate file) lives in the repo and persists on disk, so
  the memory/control contrast depends on a later harness that resets the
  control arm's session-local materials; §2's "do not touch … any other file"
  and §5's "notes/failure records" need that harness to be concrete. The card
  correctly defers this to later collection and claims no boundary now.
- §7 still discloses the seen-spec contamination and scopes the task as a
  feasibility pilot, not a clean holdout.

No experiment, no gate repair, no author artifacts edited.

*Reviewed: `package.md`, `repair-decision.json`, `task-card.md` (`93e777e8…`),
`sources.json` (`8965f6b1…`), `attempt-history/initial/*`,
`team/CORVID-S13-2G-VERIFY.md` (`bf8d2599…`), `team/S13-STATEUPD-AUDIT/check.py`
(`8c921fbb…`), `team/QUEUE.md` rows S13-2/S13-2G.*
