# R2-task-comparison-design — admission review

- **Reviewer:** corvid-dsh, admission step. Contract at commit `6ab1a00c`
  (`campaign4/packages/R2-task-comparison-design/package.md`); read with R1
  `acceptance.json` and `normalization-note.md` (`c5f02efc…`).
- **Scope reviewed:** design-only feasibility, tier‑1 sufficiency, arithmetic.
  No experiment run, no contract/design authored.
- **Verdict: ACCEPTED, bounded** (conditions below; not a rejection).

## Arithmetic — checks

`corvid10 + kiln40 + corvid20 + held repair20 + held review10 + Tern10 = 110`
seat-minutes. Matches the declared total. Estimates, not measured; terminal
metrics must carry actuals.

## Tier‑1 sufficiency — checks

Tier‑1 (design can bias later research) is satisfied by the package's own
controls: author kiln ≠ verifier corvid; preregistration proposal (not run
authority); candidate choices frozen before any new outcome access; no hidden
empirical work; reviewer assesses the design **before** author conclusions and
records inability-to-evaluate as INCOMPLETE; no worker-written test oracle is
self-proving; Tern alone authorizes any later run. This matches the adopted
process rule that a tier‑1 unit name its non-mechanical judgments and
counterevidence.

## Outcome satisfiability — satisfiable, with a real no-go branch

The question ("can one small reversible, already-available memory treatment be
compared fairly against no memory on matched local task outcomes, with a real
compaction/restart boundary if feasible?") is satisfiable **without** an
impossible check, because the contract explicitly accepts a supported no-go
with the exact missing prerequisite. Two facts from source examples frame it:

- R1's accepted record shows the compaction boundary was **not** instrumented
  (`compaction_measured: false`), so a real boundary may be unobservable —
  the design must say so honestly rather than claim one.
- `campaign4/HARNESS-OUTCOME-20260923.md` closes the P9 preview as a
  **status/expose view**, not a task runner, and releases no research run. It
  therefore cannot serve as a task-outcome oracle, and the P9 machinery is not
  a candidate treatment path.

## Bounds on acceptance

1. Name the one treatment with **exact local path + hash**, its version/config,
   and a **reversible disable path**; selection from inspected artifacts only,
   never untested popularity.
2. Ground the task pool, contamination exclusions, and the outcome rubric in
   **actual task completion** (not retrieval-only) from an inspected local
   source; if no executable task outcome or defensible treatment exists within
   the bound, return the supported no-go and the exact missing prerequisite.
3. Do **not** use P9/Expose, retrieval, delivery or any R1 proxy as the primary
   outcome; evidence delivery stays a secondary metric only.
4. Freeze candidate choices before any new outcome access; R1's prior proxy
   access is not new task-outcome access.
5. State boundary observability, confounds, sample/effort estimate, and the
   stopping rule; a null small sample must not be reported as proof of no
   benefit. Outputs: `design.md` ≤1500 words + `feasibility.tsv`.
6. No web/corpus/model study, installation, code build, or harness work;
   read-only local inspection only. Author remains HELD until Tern writes the
   exact loop tasks and releases; this admission is not experiment authority.

No impossible check found; scope is coherent. Proceed to author.

*Reviewed: `package.md`@6ab1a00c, R1 `acceptance.json`, `normalization-note.md`,
`admission-receipt.json`, `campaign4/HARNESS-OUTCOME-20260923.md`,
`campaign4/SESSION-SCOPE-RULING-20260922.md`.*
