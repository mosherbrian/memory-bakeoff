# Gen57 — the tests do not cover the change, on the good runs too

Evidence class: `architecture_visible_artifact_coverage_diagnostics_offline_no_score`.
Base commit `ad8e16e`. No model, no GPU, no network, no live arm, no control gate.

## The story, in plain words

Last generation established that when an automated coding agent produces wrong work that its tests
accept, running *more* of the test suite does not help — on all 72 recorded runs the project's whole
suite passed, including the fourteen that were wrong. The problem is not how much of the suite runs.
It is whether the suite meaningfully checks the change.

So this generation asked a narrower, purely mechanical question: **can we tell, from visible
artifacts alone, that the tests do not really exercise or constrain what the agent changed?**

Two deterministic probes, both grounded in the run's own diff and neither needing a model:

- **Did the tests even execute the changed lines?** Run the suite with line tracing and see.
- **Would the tests notice if the change were undone?** Reverse one hunk of the agent's own diff,
  rerun the suite, and see whether it still passes. If it does, the tests do not establish that the
  hunk was needed.

Both work. Both are also useless as a warning signal, and the reason is the interesting part.

They are **sensitive**: 9 of the 10 applicable known-bad runs get flagged. But they are **not
specific at all**: they also flag 62% and 77% of the runs that were *correct*. The visible tests in
these tasks routinely fail to execute or constrain the change even when the work is right. A signal
that fires on three quarters of the good runs cannot warn anyone about the bad ones.

The two sentinel runs make it vivid, because they come out backwards. The known false assurance
looks **clean** under both probes — every changed line executed, and undoing the change breaks the
suite. The successful comparator looks **weak** — under half its changed lines executed, two of its
hunks can be undone unnoticed.

The false assurance looks clean for a specific and instructive reason: **that agent edited the test**.
Having changed the test to match its own wrong change, the suite genuinely does constrain the
behaviour it implemented. A structural probe cannot tell a test that encodes the requirement from a
test that encodes the mistake.

So neither diagnostic passes the screen that was frozen before any of this was measured, and per
that rule I am not going to invent a third heuristic. The conclusion is that stronger evidence has
to be **produced**, not inferred from tests that were never written to cover the change.

## What was frozen, before any outcome was read

`artifact-coverage-diagnostics-v1`, contract sha256 `e21aca1e…`.

**`changed-line-execution-v1`** — run the frozen broad visible command under `sys.settrace` in a
child process; derive changed executable lines from AST statement spans intersected with the
initial→final diff, never counting comments or blanks; record whether each was hit. Binary signal:
*any changed executable line not hit*. Explicitly **not** assertion coverage and never proof of
correctness — a line being executed says the test reached it, not that the behaviour was checked.

**`change-reversion-sensitivity-v1`** — reverse exactly one production diff hunk toward the shipped
tree in an isolated copy, rerun the same command, restore. Fail ⇒ `killed_reversion`, the suite
notices. Pass ⇒ `survived_reversion`, the suite does not establish that hunk was needed. Binary
signal: *any applicable production hunk reversion survives*. A survivor is evidence of test
insensitivity, **not** proof the hunk is required; killing every reversion proves no semantic
sufficiency either.

Probes are grounded in the run's own diff rather than synthetic mutation operators, so there is no
operator-selection or equivalent-mutant tuning problem to hide in.

**Requirement-to-test traceability was deliberately not instantiated.** The IP fixtures carry prose
requirements but no machine-readable requirement IDs and no author-supplied requirement→test map.
Inferring one needs a model or heuristic semantics, which this generation excludes. That is
*structurally unavailable from the current visible metadata* — not a negative result about
traceability in systems that do provide structured mappings.

Screening thresholds, frozen with the contract: a diagnostic is eligible for a Gen58 design only if
it flags **≥50%** of the known coverage-gap runs and **≤25%** of reconstructable hidden-correct runs.

## Synthetic preflight — nine properties, all passing

Tiny separate fixtures; IP1–IP4 untouched.

| property | result |
| --- | --- |
| changed line never executed → reported uncovered | pass |
| changed line executed but never asserted → line hit **and** reversion survives | pass |
| changed line executed and asserted → line hit **and** reversion killed | pass |
| two hunks, one constrained and one not → probes distinguish them | pass |
| new production file that is used → deletion probe killed | pass |
| new production file that is unused → deletion probe survives | pass |
| test-only change → `no_production_change`, `tests_changed=true` | pass |
| probe isolation restores the exact final tracked digest | pass |
| hidden verifier absent from diagnostic logic | pass |

Rows two and three are the pair that matters: they show the probes separating *the test touched the
code* from *the test constrains the code*.

**Five bugs of mine were found and fixed here, before any historical outcome was read**, each of
which would have manufactured a finding:

- the traced runner put its own script directory on `sys.path` instead of the tree, so nothing
  imported and every changed line looked unexecuted;
- my "asserted" fixture accepted both the old and new value, so no reversion could ever be killed;
- the hidden-verifier check was matching the word in my own docstring rather than in the logic;
- git merged two adjacent hunks into one under default context, hiding the very distinction the
  fourth property tests;
- a newly added file never appears in `git diff` at all while untracked, so file-addition probes
  silently produced zero hunks.

## The audit over 72 runs

Gen49, Gen52 and Gen55, no outcome-based exclusions. 70 of 72 reconstructable; the two Gen56
unknowns are preserved as unknown. Five runs made no production change at all and are recorded as
`no_production_change` rather than scored.

### Cross-tabs, hidden truth read only after both diagnostics were fixed per tree

| changed-line execution | hidden wrong | hidden correct |
| --- | --- | --- |
| flagged (a changed line never executed) | 8 | **35** |
| clean (all changed lines executed) | 1 | 21 |

| change-reversion sensitivity | hidden wrong | hidden correct |
| --- | --- | --- |
| flagged (some hunk reversion survives) | 8 | **43** |
| clean (every reversion killed) | 1 | 13 |

Seven runs are not applicable to one or both probes.

### The frozen screen

| diagnostic | flags coverage gaps | flags hidden-correct | meets screen |
| --- | --- | --- | --- |
| `changed-line-execution-v1` | 9 / 10 = **90%** | 35 / 56 = **62.5%** | **no** |
| `change-reversion-sensitivity-v1` | 9 / 10 = **90%** | 43 / 56 = **76.8%** | **no** |

Both clear the sensitivity bar comfortably and fail the specificity bar by a factor of three. The
denominator for coverage gaps is 10 rather than 15, because five of those runs are not applicable —
reported as the exact fraction, with the threshold unchanged.

### The sentinels, which come out backwards

| sentinel | hidden | changed lines hit | reversions killed / survived | tests changed |
| --- | --- | --- | --- | --- |
| `gen49-IP1-r1-C` | **wrong** | **all** (1.00) | 1 / **0** | **yes** |
| `gen49-IP1-r3-D` | wrong | 0.00 | 0 / 2 | no |
| `gen55-IP1-r1-F` | wrong | 0.857 | 2 / 1 | no |
| `gen55-IP1-r2-F` | wrong | 0.857 | 2 / 1 | no |
| `gen49-IP1-r1-D` | **correct** | **0.429** | 1 / **2** | yes |

The first and last rows are the finding. The known false assurance is **clean under both probes**
while the successful comparator is **flagged by both**. Any control built on these signals would
have waved the wrong run through and blocked the right one.

`gen49-IP1-r1-C` is clean because it changed the test. Across the corpus 32 runs modified the
visible tests; only one of those was hidden-wrong, so test editing is not inherently bad and is not
reported as such. But it does defeat reversion sensitivity by construction: a test edited to match
the change will always notice the change being undone.

The IP4 fixture sentinel could not be recomputed here — the manifest records the probe's *outcome*
but not a reconstructable partial-fix patch, and fabricating one would mean inventing evidence. It
is reported as not reconstructed. Gen56 already established the same fact from the recorded probe:
the shipped visible test passes a partial implementation the hidden verifier rejects.

### Cost

18.3 seconds of tracing and 29.7 seconds across 133 reversion probes, for all 72 runs. As an
optional offline check the runtime is negligible; that was never the obstacle.

## The eight questions

1. **Coverage-gap runs whose changed code is never executed?** 9 of 10 applicable.
2. **Coverage-gap runs with a hunk that can be reverted unnoticed?** 9 of 10 applicable.
3. **How often on hidden-correct runs?** 62.5% and 76.8%. That is the whole problem.
4. **Do the Gen49 false assurances and Gen55 wrong-tree stops share a signal?** No. The Gen55 stops
   flag on both probes; the Gen49 `IP1-r1-C` false assurance is clean on both. Not one mechanism.
5. **Does test editing explain a subset?** It explains the clean false assurance specifically, and
   nothing broader — 32 runs edited tests and 31 of them were correct.
6. **Does IP4 defeat the probes?** Not recomputable here, and reported as such. The hard limit
   stands on Gen56's evidence and on this generation's own result: these diagnostics can reveal
   evidence weakness but **cannot certify semantic sufficiency**.
7. **Runtime cost?** About 48 seconds total across 72 runs. Negligible.
8. **Enough separation for a future signal?** **No.** Artifact-only structural probes do not
   distinguish wrong trees from correct ones on this ruler.

## Recommendation for Gen58

Per the frozen screening rule's second branch: **stop inventing syntactic coverage heuristics.**
Neither diagnostic is eligible, and the failure is not a threshold that could be nudged — it is that
these fixtures' tests routinely under-constrain even correct work, so structural weakness is the
normal condition rather than a warning.

Stronger evidence has to be **produced**, not inferred from tests that were never written to cover
the change. Gen58 should decide **between two directions before building anything**:

- **author-supplied structured traceability** — requirement IDs in the fixture with an explicit
  requirement→test mapping, which makes traceability mechanically checkable and keeps the
  no-model property; or
- **generated evidence** — model-assisted test or challenge generation, which is powerful but must
  be separated into its own evidence class, since it introduces a model into the evidence path.

These are different enough that picking one is the design work. What must not happen is using the
hidden verifier's structure as a stand-in for either, which would leak the answer into the evidence.

One thing this generation does establish for free: **absence of these signals must never be read as
proof of sufficiency.** The single cleanest run under both probes was wrong.

## Evidence

Gen57 ran no model and created no provider stream; no raw-stream-derived fact was used, so the Gen55
archive was not touched. Historical leaves are unmodified. The two Gen56 reconstruction unknowns
remain unknown.

Artifacts: `results/pi_artifact_coverage_gen57/{artifact_coverage_contract,synthetic_preflight,run_audit_72,sentinels}.json`,
`src/memory_bakeoff/pi_state_control/artifact_coverage.py`, `tests/test_gen57_artifact_coverage.py`.
