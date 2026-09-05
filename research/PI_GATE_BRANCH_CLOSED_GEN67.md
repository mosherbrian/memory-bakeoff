# Gen67: the candidate-blind gate branch is closed

No model, no GPU, no new critic. This reads the committed outcomes of Gen60
through Gen66 and records the bounded conclusion.

## The conclusion

For this pinned model and generator configuration, **candidate-blind
model-generated tests are reviewer evidence, not an unattended correctness
gate.**

They are good at what they are good at: across every condition that produced a
usable bank, they caught **12 of 12** wrong implementations in the scored
population, including ones that pass the project's own shipped tests. They are
unreliable in a way no intervention fixed: **4 of 8 banks reject known-correct
code**, and it was the same four tasks every time.

## The whole arc, in one table

| | change | unsafe banks | removals | precision | retention | caught |
|---|---|---|---|---|---|---|
| Gen60 | unchanged generator, repaired corpus | 4 of 8 | — | — | — | 12/12 |
| Gen61 | each test must quote its requirement | 4 of 8 | 0 of 188 | — | 1.000 | 12/12 |
| Gen62 | delete anything not entailed | 0 of 7* | 158 of 188 | 0.101 | 0.000–0.333 | 18/21 |
| Gen63 | screen repaired (retention floor) | Gen62 → UNEVALUABLE | — | — | — | — |
| Gen64 | delete only with a named condition | 4 of 8 | 15 of 188 | 0.267 | 0.821–0.964 | 12/12 |
| Gen66 | …and show it the repository | 4 of 8 | 27 of 188 | 0.222 | 0.607–1.000 | 12/12 |

\* zero only because the banks had been emptied; Gen63's guardrail re-scored it
UNEVALUABLE.

**Read the unsafe column: 4, 4, (0 by destruction), 4, 4.**

## Why the branch closes here

Four interventions attacked the false-alarm rate from four directions —
provenance, entailment, justified deletion, and information. None moved it.

The last one matters most, because it removed the explanation we had for the
first three. "The checker only sees a sentence and a test" was a reasonable
account of why it could not distinguish an overreaching assertion from a sound
inference. Gen66 gave it the reference repository, verified candidate-blind with
zero leaks, and the rate did not shift. The `pathsafe` bank kept **all seven** of
its false accusations with the code in front of it.

At that point the hypothesis space for *this* architecture is exhausted. Further
prompt, filter or context tuning on candidate-blind checking is closed.

## What is explicitly not the next iteration

A checker allowed to inspect the candidate would very likely do better on these
numbers, and it would not be a continuation of this experiment. It is a
different, **non-independent** architecture: a checker that reads the
implementation is on its way to agreeing with it, which is the exact failure —
the Gen49 self-modified test — that this entire programme was built to detect.

If that is ever pursued it needs its own question, its own independence
analysis, and its own name. It must not be reported as the next turn of this
one.

## What the programme actually gained

- A corpus where right and wrong answers coexist and every label was measured
  (`evidence-generation-gen59-v1`).
- A screen that cannot be gamed by deleting the evidence
  (`gen63-retention-guardrail-v1`).
- A reporting rule that refuses to compress gate suitability into a verdict word
  (`gate-suitability-report-v1`).
- Four negative results with a stated mechanism, which is worth more than a
  positive result with an unexamined one.
- One methodological correction, made against my own earlier report, and fixed
  in code so it cannot recur.

## Scope

One pinned model. One generator contract. Eight tasks. One run per condition.
This is a bounded claim about a configuration, not a general claim that
model-written tests cannot gate code.

## Artifacts

- `results/pi_gate_branch_closed_gen67/gate_question.json` - all six generations, derived from committed outcomes
- `scripts/run_gen67_closure.py` - reads results files only
- `research/PI_GATE_QUESTION_GEN65.md` - the Gen60-64 synthesis this extends
- `research/PI_REPO_CONTEXT_GEN66.md` - the context ablation that closed it
