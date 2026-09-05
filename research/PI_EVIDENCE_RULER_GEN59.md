# Gen59 — building a ruler where right and wrong answers live side by side

Evidence class: `architecture_generated_evidence_ruler_design_no_score`.
Base commit `fe91f5b`. No model, no GPU, no network, no live arm, no generator call.

## The story, in plain words

Last generation asked a model to write extra tests from the specification alone, to see whether an
independent reading could catch work that the project's own tests wave through. The idea showed one
real success — on the one task built with a deliberate gap, the generated tests caught a partial
implementation the shipped test accepted.

But the experiment could not be scored, and the reason had nothing to do with the model. Every
faulty implementation we had on record lived in two tasks whose generated tests *also rejected known
good code*, and the two tasks where the generated tests were trustworthy contained no faulty work at
all. There was nowhere to measure both halves of the question at once: can it catch what is wrong,
and does it leave what is right alone?

So this generation does not touch the generator. It builds the missing measuring stick.

Eight new tasks, each carrying **two genuinely different correct implementations** and **three wrong
ones** — and crucially, at least two of the wrong ones **pass the project's own shipped tests**.
That last property is the entire point: it is the situation an evidence generator is supposed to
help with, and it has to be present before the generator can be judged at all.

All eight tasks were admitted. The corpus holds **24 known-wrong implementations, 18 of which slip
past the shipped tests**, across seven different kinds of mistake. The bar set for it was six tasks,
eighteen wrongs and twelve slip-throughs.

Getting there meant throwing out some of my own work, which is described below rather than tidied
away.

## What the ruler contains

`evidence-generation-gen59-v1`, a new fixture family that leaves the old IP1–IP4 tasks untouched.

| task | the kind of mistake it makes possible | wrongs that pass the shipped tests |
| --- | --- | --- |
| `culvert` | a shared constant with two consumers, only one of which should change | 3 |
| `valve` | a limit stated at both ends, tested only at one | 2 |
| `tally` | behaviour that only appears across a sequence of calls | 2 |
| `manifest` | a blank field that must be distinguishable from an empty one | 2 |
| `ledger` | a rounding rule that only bites at an exact midpoint | 3 |
| `dispatch` | an ordering rule one call cannot reveal | 2 |
| `pathsafe` | an input that must be refused rather than repaired | 2 |
| `thermo` | a default value the shipped tests never exercise | 2 |

Every task ships a plain specification, a small repository with ordinary — deliberately incomplete —
tests, and an evaluator-only truth package holding the hidden verifier, the candidates and the
requirement labels.

`culvert` carries the shape that started this line: a wrong implementation that **edited the
shipped test** to agree with its own mistake, and consequently passes it.

## What was measured, not assumed

Every `passes_visible` label in my task definitions was a prediction. The builder treats them as
predictions: it materialises each of the 40 candidates, runs the shipped tests and the hidden
verifier against it, and admits a task only when the measurements agree with the design.

For all eight admitted tasks:

- both positives pass the shipped tests **and** the hidden verifier;
- the two positives have different tracked-tree digests, so they are genuinely different code;
- all three wrongs fail the hidden verifier, each for a named requirement;
- at least two wrongs pass the shipped tests.

## Three corrections, all found by measurement

**Two were bugs in my harness, and both made the ruler look broken when it was not.** The
materialised candidate trees had no git repository, so every tracked digest came back as the empty
string and all positives looked identical. And the hidden verifier was run as a script, which puts
the script's own directory on the import path rather than the candidate tree — so nothing imported
and *every positive appeared to fail*. That is the same `sys.path` trap as Gen57, now fixed in both
places.

**The third was a real design error of mine.** I built `ledger` and `thermo` on rounding a float at
an exact midpoint. That premise is unsound: `2.345` is not stored exactly, it sits slightly *above*
the midpoint, so Python's own `round` already returns `2.35` and my "wrong" candidates were simply
correct. Measurement caught it — those tasks were rejected for containing a wrong that passes the
hidden verifier.

Rather than weaken the invariant, I rebuilt the tasks. `ledger` now takes decimal strings, where a
midpoint is exact and the rule genuinely bites. `thermo` lost its rounding clause altogether and
tests only the untested default, because a requirement that cannot be evaluated has no business in a
ruler. When `half_to_even` still slipped through, the verifier gained `2.665` — the value where
half-away-from-zero and half-to-even actually diverge.

The brief's instruction was explicit: fix the specification or drop the task, and never use
ambiguity as difficulty. This is that instruction applied literally.

## Isolation: what a future generator can and cannot see

The generator's input is the specification plus the shipped repository, exactly as in Gen58. The
truth package lives in a sibling directory that is not on that path.

Checked mechanically, on the prompt a future generator would actually receive: **zero occurrences**
of `verifier`, `candidates.json`, `failed_requirement` or `VERIFIER OK`, and the truth directory is
absent from every generator-visible tree. The hidden verifier and candidate labels exist in this
generation only because this generation is building the ruler.

No wrong candidate was written by negating a verifier assertion. Each is an ordinary engineering
mistake — a stale shared constant, a missing lower bound, a deferred reset, a blank treated as an
empty string, a rounding mode, a queue that ignores priority, a path silently repaired instead of
refused, a default left as it was. The verifier confirms the error; it never defined the candidate.

## The Gen60 screen, frozen now

`gen60-generated-evidence-screen-v1`, sha256 `b694f7b8…`, written before any generated output
exists so the goalposts cannot move:

- a bank is usable for a task only if it passes **all** trusted positives; any failure marks that
  task `UNSAFE_AS_GATE`, kept and reported, never repaired;
- sensitivity: flag at least 50% of known-wrong candidates in the reference-valid population;
- specificity: flag no more than 25% of trusted positives;
- **coverage**: at least four tasks must remain reference-valid with two or more wrong candidates
  each, otherwise the screen is **UNEVALUABLE rather than failed** — the explicit branch that Gen58
  lacked;
- no tuning of prompt, sanitizer, task set, aggregation or thresholds after exposure;
- absence of a challenge is never proof of correctness.

Gen60 must re-test the **same** Gen58 generator on this ruler. Changing the model or adding a critic
now would confound a corpus repair with a generator repair.

## The nine questions

1. **Authored, rejected, admitted?** 8 authored, 8 admitted, 0 rejected — after three tasks were
   corrected and re-measured.
2. **Two positives and three wrongs everywhere?** Yes, all eight.
3. **Two visible-passing wrongs everywhere?** Yes; 18 in total, three tasks have three.
4. **All positives pass both checks?** Yes.
5. **All wrongs fail the hidden evaluator for a named requirement?** Yes, 24 of 24.
6. **Is the self-modified-test shape present without leaking truth?** Yes, in `culvert`, and the
   leak check is clean.
7. **Enough diversity?** Seven mechanisms across eight tasks.
8. **Is isolation mechanically demonstrated?** Yes, on the assembled prompt itself.
9. **Is the Gen60 screen frozen with an UNEVALUABLE branch?** Yes.

## Recommendation for Gen60

The bar was six tasks, eighteen wrongs, twelve slip-throughs. The ruler delivers eight, twenty-four
and eighteen, so **Gen60 should re-test the same pinned Gen58 generator contract on this ruler**, with
no change to model, prompt or sanitizer.

What this does **not** establish is that the generator will do any better. The ruler only guarantees
that the question is now answerable — that a failure will be a fact about the generator rather than
an artefact of the corpus. If the same component fails here, a cross-model or critic-checked
ablation becomes earned rather than speculative.

Nothing here revives quiescent completion, validation breadth, or artifact-only coverage heuristics.

## Evidence

Gen59 made no model call and created no provider stream; the Gen58 archive was not touched.
Historical fixtures and leaves are unmodified.

Artifacts: `fixtures/evidence_generation_gen59_v1/`,
`results/pi_evidence_ruler_gen59/{ruler_contract,task_manifest,candidate_matrix,reference_diversity,isolation_preflight,gen60_frozen_screen}.json`,
`src/memory_bakeoff/evidence_ruler/tasks_gen59.py`, `tests/test_gen59_evidence_ruler.py`.
