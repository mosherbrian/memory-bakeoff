# EXTERNAL — GVS5H ledger orchestration: convergent architecture, unverifiable number

**Filed** 2026-09-21 by Claude, from a link Brian supplied. **Class:** research
intake, unverified. **Nothing here has been run by this project.**

**Source:** `claw.rommark.dev/blog/zcode-smart-skill-gvs5h-ledger-orchestration-review.html`
— a **review blog post**, not the project's own documentation and not a paper.
Author "Roman · Rommark.Dev, AI Architect", published 2026-09-21, Tbilisi. The
subject is "ZCode Smart Skill" v2.2.0, Apache-2.0. Page read in full, not via
summary.

## Why it is filed: it reached our conclusions independently

This is the second artifact this week that arrived at our design from a
different direction. The convergence is the finding.

| Theirs, verbatim | Ours |
|---|---|
| "no conversational context is passed directly between agents" | file-based continuity; cairn lost its context twice on 2026-09-21 and resumed from files |
| "Adversarial Pre-Testing — test suites generated before code writing. **Eliminates tautological tests where LLMs test their own bugs**" | registration before scored execution; "a check fitted to a finished artifact passes by construction" |
| "Ground-Truth Verification — OS process exit code 0 enforcement. Prevents premature 'I have completed the task' claims" | computed done-state from files and exit codes; no prose predicate |
| **"Does NOT ask LLM if it's 'done' — verifies exit code 0"** | the same sentence, reached by counting three files where `\bclosed\b` matched inside `fail-closed` |
| "Branch Checkpointing — automated `cp-*` snapshots. Instant rollbacks" | attempt history preserved; a repair never overwrites the attempt it replaces |
| "Progressive Context Shedding — scratchpads wiped between sub-phases" | blind-first reproduction; the verifier freezes its own numbers first |
| "Strict Token Budgets — cap subagents at 8,000 output tokens" | per-attempt wall-clock and resource limits |
| "Ledger Compaction — 1-page executive post-mortem" | disposition recorded at close |

Their phases: Manager → Adversarial Tester → Implementation Worker → Strict
Verifier, each a fresh instance, coordinating only through
`.smart/<task-hash>/` holding `plan.md`, `task.md`, `tests_spec.py`,
`verify.log`, `cp-*`.

## What it has that we do not

**A measured number.** 92.4% pass@1 on LiveCodeBench-Hard, claimed to beat
Claude Fable 5 monolithic at 90.4%, GPT-4.5 Preview at 87.1%, and a single
Qwen 27B baseline at 74.6%. We have no outcome number for our loop at all.

**Dual-Hypothesis Racing** — two approaches run in parallel, first to pass the
suite wins, the other is killed. We have no equivalent and it is interesting:
it converts a judgment ("which approach?") into a race with a mechanical
finish line.

## Why the number should not be cited

The architecture is described precisely. The evaluation is not.

- **"researchers evaluated the system"** — passive, unnamed, no citation, no
  link to raw results, no protocol, no per-task breakdown.
- The claim is that an ensemble of **27B open-weight models beats frontier
  monolithic models** on a hard contamination-resistant coding benchmark. That
  is an extraordinary claim carried by one sentence on a review blog.
- **"0% Context Smear or Drift"** is a headline statistic. It is not a
  measurable quantity.
- Register: "revolutionary", "Spectacular", "cannot be overstated", "Paradigm
  Shift", and a **9.8/10** rating. This is marketing prose, not evaluation
  prose.
- No cost or wall-clock figures beyond "execution time is higher".
- Author's relationship to the project is not stated.

This is the pattern this project has already been burned by, and the one Tern
flagged on memoose: vendor-adjacent self-report, no independent replication.
Compare the honest version — memoose published a **null result against its own
central claim** with a named statistical test. Nothing here cuts against the
author.

## Two gaps in the architecture itself

**1. The repair loop appears unbounded.** Section 7 is titled "Failure
Resilience & Anti-Loop Rollbacks", but the mechanism shown is:
`FAIL → rollback to cp-* → synthesize 3-line error → dispatch new Worker`,
with **no round cap stated anywhere**. That is precisely the edge that
consumed three campaigns here: 9 rounds on gen120, 42 verification documents
against 6 closed rows, 28 gate re-issues. Their fresh-context-per-attempt
design may mask it for longer — a new worker does not see its own prior
failures — but nothing stated terminates it.

**2. Nobody checks that the test suite is satisfiable.** Their adversary
writes tests before code, which correctly prevents a worker grading its own
bug. But no second party checks the suite can be passed by an honest
implementation. That is exactly S13-1G on 2026-09-20: a gate that passed its
own selftest, rejected 29 non-conforming fixtures, and **could not be
satisfied by any faithful artifact**, because it demanded an input shape the
frozen declaration never had. corvid caught it by probing the gate against
real inputs. An exit code cannot.

## Why their design can be simpler than ours

**They have an oracle and we mostly do not.** Code compiles and passes tests,
or it does not. Exit code 0 is ground truth.

Our work often has no such oracle, which is why 2026-09-21 landed on two
lanes. The evidence is one day old: the transfer test, which has a mechanical
answer, went from question to committed independently-reproduced negative
result in forty minutes. The mechanism audit, whose answer is a judgment about
thoroughness, was stuck for three days across two gates and a re-issue ladder.

So this architecture is strong corroboration for the decidable half of our
design and **silent on the half that is not decidable**. It should not be read
as evidence that the judgment lane is unnecessary.

## Cheap things worth considering

1. **Dual-hypothesis racing**, where two approaches are genuinely available
   and the finish line is mechanical. It replaces a director's judgment with a
   race.
2. **A synthesized 3-line error on failure** rather than the whole log. We
   hand a verifier the entire verdict; they hand the next worker three lines.
   Cheaper, and it cannot carry the previous attempt's reasoning.
3. **Dynamic difficulty tagging** — skip the adversary phase for trivial work.
   We have one contract weight for everything, and Tern already flagged
   contract heaviness as a risk.

## Status

- **Architecture:** read in full, convergent with ours, worth Tern's attention.
- **Benchmark:** unverifiable as published. Do not cite 92.4% anywhere.
- **Not a memory-system candidate.** It is a coding orchestrator; it publishes
  nothing about memory.
- **Next cheap step if pursued:** ask only whether the repair loop has a cap in
  the actual repository. That single fact decides whether their design has
  solved the edge that killed three of ours, or has not met it yet.

---

## Disposition — 2026-09-21

**Considered and declined. Interesting, not adopted.** Tern's call, relayed by
Brian.

Consistent with her rulings on memoose and Munder Difflin: architectural
reference, not an adoption candidate. Nothing here is a capability we lack —
the convergence itself was the finding, and it corroborates the decidable half
of the design we already have.

Not implemented, and no package opened:

- **Dual-hypothesis racing** needs two genuinely available approaches and a
  mechanical finish line. Our stalls have been judgment calls with no race to
  run.
- **Three-line error handoff** is a saving on a cost we are not paying; our
  repairs have been one-value corrections.
- **Difficulty tagging** addresses contract weight, which r2 is handling
  directly rather than by adding a classifier.

**The one open question, left open on purpose:** whether their repair loop has
a round cap in the actual repository. The published description has none, and
that is the edge that consumed three of our campaigns. Worth one look if
anyone is ever in there; not worth a package to find out.

Declining a candidate for a stated reason is a use of it, not a failure to use
it.
