# Gen66: showing the checker the code did not help either

## The new branch

Gen65 closed the text-only question: a checker reading one requirement sentence
and one test cannot tell an overreaching assertion from a sound inference. The
one remaining plausible variable was **context** — a checker that can see what
the code actually is might have the material to separate them.

This opens that as a new experimental family rather than a fifth turn of the old
one, because it moves the checker's information boundary.

**Permitted:** the reference repository as shipped, before any work, and its
visible tests. **Forbidden:** the candidate under test, any diff, the hidden
evaluator, any outcome, the known-wrong labels.

The repository shown is identical for every candidate, so nothing the critic
reads is evidence about the implementation being judged. It learns what the code
*is* and cannot learn what the candidate *did*. Isolation was verified on the
assembled prompt before the first call: zero evaluator tokens and zero candidate
lines across all eight tasks.

Everything else is Gen64 unchanged — same pinned model, deletion only, a named
extra condition required, Gen63's guardrail in force. The verdict reader is
imported from Gen64 rather than reimplemented, and a test asserts it is literally
the same function, so exactly one thing differs between the runs.

## What happened

| | Gen61 | Gen64 (text only) | Gen66 (with the code) |
|---|---|---|---|
| removals | 0 | 15 of 188 | **27 of 188** |
| removal precision | — | 0.267 | **0.222** |
| known-false removed | 0 of 16 | 4 of 16 | **6 of 16** |
| valid removed | 0 of 172 | 11 of 172 | **21 of 172** |
| retention (worst bank) | 1.000 | 0.821 | **0.607** |
| **unsafe banks** | **4 of 8** | **4 of 8** | **4 of 8** |
| detection (shared population) | 12/12 | 12/12 | **12/12** |

**Same rate, same four tasks: `culvert`, `ledger`, `pathsafe`, `tally`.** For the
fourth time.

Recall improved slightly (0.250 to 0.375) and precision fell slightly (0.267 to
0.222). Nothing hollowed; detection intact. The context changed the critic's
behaviour without changing the outcome.

## The crux: `pathsafe`

`pathsafe` holds seven of the sixteen false accusations. With the repository in
front of it, the critic removed **none of them**. Every one was KEEP.

Those tests say things like "a name with a Windows drive letter must raise
ValueError", citing a sentence that says absolute paths must be refused. Reading
the shipped code — which handles POSIX-style relative depot names — did not lead
the critic to notice that a drive letter is not what that sentence is about. It
saw an assertion that echoes the requirement and approved it.

Meanwhile on `culvert` it removed 11 tests, 6 genuinely false and 5 sound,
including `to_steps(0) == 0` and a check that the module constant is 8. The extra
context made it more willing to reason about specific values, and that
willingness cut in both directions at once.

## What this establishes

Four interventions have now failed to move the unsafe-bank rate:

1. **Gen61** — quote the requirement. No effect; the false accusations already
   quoted correctly.
2. **Gen62** — delete anything not entailed. Deleted the evidence.
3. **Gen64** — delete only with a named condition. Removed the wrong few.
4. **Gen66** — do that with the repository in view. Removed slightly more of both
   kinds, and the rate did not move.

That is a stronger result than any single run: the failure survives the removal
of the constraint we thought was causing it. It was reasonable to think the
checker was handicapped by seeing only text. It was not — or at least, this
amount of context does not repair it.

**I would stop pursuing automated gating for this configuration.** That was Sol's
own stated stopping condition for this branch, and the measurement met it.

## What this does not establish

The repository the critic saw is the *pre-work* state. A checker that saw the
post-change code would have more to work with — and would be exactly the failure
mode this design exists to avoid, since a checker that reads the implementation
starts agreeing with it. So this is not evidence that no amount of context could
work; it is evidence that **candidate-blind** context does not, and candidate-
blindness is what makes the evidence independent in the first place.

Scope is unchanged and bounded: one pinned model, one generator contract, eight
tasks, one run per condition.

## Artifacts

- `results/pi_repo_context_gen66/isolation_preflight.json` - zero leaks, checked before the first call
- `results/pi_repo_context_gen66/critic_contract.json` - frozen before exposure
- `results/pi_repo_context_gen66/critic_log.json` - every verdict with its named condition
- `results/pi_repo_context_gen66/critiqued/` - surviving banks
- `results/pi_repo_context_gen66/screen_result.json` - outcomes plus retention
- `src/memory_bakeoff/evidence_ruler/repo_context_critic.py` - prompt, boundary, contract
