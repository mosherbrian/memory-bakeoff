# Gen58 — asking a second reader for harder tests

Evidence class: `architecture_model_assisted_challenge_generation_component_pilot`.
Base commit `dbae88a`. Local pinned model only, under standing authorization. No live coding-agent
arm, no new gate, no network beyond the local endpoint.

## The story, in plain words

The problem this whole line keeps circling is that an automated coding agent can produce wrong work
that its own tests accept. Gen56 showed running *more* of the test suite catches nothing. Gen57
showed that asking whether the tests *exercise* or *constrain* the change catches nothing either,
because those signals fire on three quarters of the correct runs too — and the cleanest known false
assurance was structurally spotless, since that agent edited the test to encode its own mistake.

Every route so far has tried to squeeze more meaning out of the tests that already exist. So this
generation tried the other thing: **ask a model to write additional tests**, giving it only the
original instruction and the starting code, and never letting it see anyone's solution.

Twelve generations — four tasks, three attempts each — then check whether those generated tests
recognise a known-good implementation, and only then run them against the historical work.

**The honest result is that the experiment cannot answer its own question, for a structural reason
that is itself the finding.**

Half the generated test banks are **wrong**. On two of four tasks the bank rejects a trusted correct
implementation that predates this experiment — it invents requirements the instruction never stated.
Those banks are unusable regardless of what else they catch.

And the two banks that *are* trustworthy cover tasks that contain **no wrong work at all**. Every
historical failure in this corpus sits in the two tasks whose banks are untrustworthy. So the
population where the evidence is sound and the population where there is something to catch do not
overlap. The screen is not failed; it is **unevaluable**.

One real positive survives that. On IP4 — a trustworthy bank — the generated tests **do** catch the
partial implementation that the project's own shipped test happily passes. That is the first time in
this line that anything has produced evidence the visible artifact lacked.

## What was frozen before any model output

`model-assisted-challenge-evidence-v1`. The generator receives the exact original instruction and
the exact shipped repository, and nothing else — no candidate tree, no diff, no transcript, no
outcome, no hidden verifier, no reference fix, no prior challenge result. Twelve stateless calls,
three per task, frozen order and sampling, on the same pinned local model as the Pi line.

Output must be one fenced Python block of tests only, checked by a deterministic sanitizer: no
production edits, no edits to shipped tests, no file access, size-capped, syntax-checked.

The trusted references are the `reference_fix` entries in the **committed Gen48 builder**, which
states in its own manifest that they "exist only in this builder and are never written into a
fixture tree or a prompt." They predate this generation, are evaluator-only, and are never shown to
the generator. IP4 additionally carries the recorded partial fix, which is what makes its sentinel
evaluable without inventing a patch.

### A defect of mine, and why the run was discarded rather than patched

The first frozen sanitizer counted only **top-level** functions named `test_*`. The model wrote its
tests inside `class Test…` blocks, which pytest collects perfectly well, so nine of twelve valid
outputs were rejected as "no test functions defined".

That was a bug in my detector, not a property of the outputs and not a policy judgement. It was
found **before any bank had been executed against any tree**, so the correction could not have been
informed by outcomes and nothing was selected or repaired on the basis of results.

The brief says a contract change after first model output means stop or regenerate, never
patch-and-continue. So the twelve outputs were quarantined under
`results/pi_model_assisted_evidence_gen58/superseded_attempt_1/` with a README, the sanitizer was
corrected, the contract re-frozen at `5bad7bd7…`, and **all twelve calls were regenerated from
scratch**. Nothing from the first attempt is used.

After correction all twelve outputs parsed, producing 4 to 26 tests each, in 176.7 seconds.

## Do the generated banks even know what correct looks like?

This is the first question, and it is the one that decides everything else.

| task | bank passes a trusted correct implementation | verdict |
| --- | --- | --- |
| IP1 | **no** | `UNSAFE_AS_GATE` |
| IP2 | yes | reference-valid |
| IP3 | **no** | `UNSAFE_AS_GATE` |
| IP4 | yes | reference-valid |

**Half the banks hallucinate requirements.** IP1's bank fails a known-good tree on assertions like
`test_one_mm_is_eight_steps` and `test_negative_mm_is_negative_steps` — it invented a unit
convention and a sign convention the instruction never specified. These banks are reported exactly
as generated and were not repaired, filtered or cherry-picked.

## The collision that makes the screen unevaluable

| | IP1 | IP2 | IP3 | IP4 |
| --- | --- | --- | --- | --- |
| bank trustworthy | no | **yes** | no | **yes** |
| hidden-wrong trees in this task | 9 | **0** | 5 | **0** |

Every historical failure lives in IP1 and IP3. Every trustworthy bank covers IP2 and IP4. The
intersection is empty.

Over the reference-valid population the cross-tab is therefore:

| | hidden wrong | hidden correct |
| --- | --- | --- |
| bank fails the candidate | 0 | **0** |
| bank passes the candidate | 0 | 36 |

Zero false alarms across 36 correct trees is a genuinely good specificity result, and it is all the
screen can say. The sensitivity cell is empty because there was nothing wrong to find.

`meets_frozen_screen` reads false in the artifact, and that must not be read as a merits failure.
The correct statement is **unevaluable on this corpus**.

### What the untrustworthy banks do, for completeness

IP1's bank flags **16 of 16** reconstructable trees; IP3's flags **18 of 18**. They reject
everything, including seven hidden-correct runs and the trusted reference itself. A bank that fails
every tree has no discriminating power at all — it is not a strict detector, it is a broken one.

## The sentinels

| sentinel | hidden | bank fails it | usable? |
| --- | --- | --- | --- |
| `gen49-IP1-r1-C` (structurally clean false assurance) | wrong | yes | **no** — IP1 bank is unsafe |
| `gen49-IP1-r3-D` | wrong | yes | no |
| `gen55-IP1-r1-F` | wrong | yes | no |
| `gen55-IP1-r2-F` | wrong | yes | no |
| `gen49-IP1-r1-D` (successful comparator) | **correct** | **yes** | no |
| `gen48-IP4-partial-fix` | partial | **yes** | **yes** — IP4 bank is reference-valid |

The crucial pairing fails. Yes, the generated tests catch the structurally-clean false assurance —
but the same bank also rejects the successful comparator *and* the trusted reference. Catching
everything is not catching the right thing.

The last row is the one genuine positive of this generation. On a bank that demonstrably recognises
a correct implementation, the generated tests fail the recorded partial fix, naming
`test_clamp_negative_returns_zero` — the negative-clamp requirement that the shipped visible test
does not check. **An independent reading of the requirement produced evidence the project's own test
suite lacked.** That answers the IP4 question affirmatively, on one case.

A small reporting gap: for some sentinels the failing-test names came back empty because my regex
did not match pytest's quiet-mode output. The pass/fail booleans come from exit status and are
sound; only the name list is incomplete.

## The nine questions

1. **Do banks pass trusted implementations?** Two of four. The other two hallucinate requirements.
2. **Fraction of hidden-wrong trees challenged?** Unevaluable — no hidden-wrong trees exist in the
   reference-valid tasks.
3. **Fraction of hidden-correct trees challenged?** 0 of 36 on reference-valid tasks. On unsafe
   banks, all of them.
4. **Does it catch `gen49-IP1-r1-C`?** Yes, but by a bank that also rejects correct work.
5. **Does it spare `gen49-IP1-r1-D`?** No. It rejects the successful comparator too.
6. **Does IP4 become detectable from the visible requirement alone?** **Yes** — the one clean result.
7. **Stability across repetitions?** Test counts vary widely (21/26/25, 9/14/11, 14/13/13, 4/5/8) and
   the IP1 hallucinations appear in specific repetitions, so the banks are not stable.
8. **Cost?** 176.7 seconds of GPU for 12 calls; 12 raw streams, 45,744 bytes, retained and verified
   after cleanup.
9. **Does the screen justify a next design?** Not on this evidence. See below.

## Recommendation for Gen59

Per the frozen decision rule, this outcome is the "specificity / oracle quality" branch, with a
twist: the failure is not that generated evidence is too noisy in general, but that **on this ruler
the tasks with wrong work and the tasks with trustworthy generated evidence are disjoint**, so the
component cannot be screened here at all.

Two things follow, and I would not proceed to a design generation on either without deciding first.

**The corpus is the binding constraint, not the component.** Any further work on generated evidence
needs a population where wrong implementations and checkable references coexist. That is a ruler
question, not a generator question. Building a design on top of a screen that could not run would
repeat the Gen51→Gen52 mistake of trusting a clean-looking screen.

**Half the banks being wrong is the real component result.** A generated test that rejects a correct
implementation is worse than no test, because it would block good work. Prompt tuning is the obvious
response and is exactly what the brief forbids post hoc — and rightly, since I have now seen the
outcomes. A cross-model or critic-checked variant would be the honest next ablation, preregistered
separately.

What I would not do is treat the single IP4 success as a green light. It is one case, on the one
task built specifically to have a visible-test gap, and it shows the idea *can* work — not that this
generator is reliable.

Nothing here revives structural coverage heuristics, validation breadth, or quiescence, all of which
remain closed.

## Evidence

All 12 provider streams finalized through `raw-evidence-retention-v1` into a durable archive outside
the repository: **12 streams, 45,744 bytes, `retention_verified` true after the in-repo captures were
removed.** Generated banks and their hashes are committed as derived artifacts; raw streams are not.
The superseded first attempt is retained, labelled and unused.

Artifacts: `results/pi_model_assisted_evidence_gen58/{model_assisted_challenge_contract,generation_log,evaluation,raw_stream_manifest}.json`,
`results/pi_model_assisted_evidence_gen58/generated/`,
`src/memory_bakeoff/pi_state_control/challenge_generation.py`,
`tests/test_gen58_model_assisted_evidence.py`.
