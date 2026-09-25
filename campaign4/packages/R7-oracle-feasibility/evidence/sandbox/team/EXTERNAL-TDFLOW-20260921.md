# EXTERNAL — TDFlow: the test author is the bottleneck, measured

**Filed** 2026-09-21 by Claude, from a link Brian supplied. **Class:** research
intake. **Nothing here has been run by this project.**

**Source:** arXiv **2510.23761v2**, *TDFlow: Agentic Workflows for Test Driven
Development*. Han, Maddikayala, Knappe, Patel, Liao, Barati Farimani. Page
fetched and read in full; every number below was read from the paper, not from
a summary.

## Why this one is different from the other intakes

It has a standard benchmark, named authors, published negative results, a
measured gaming rate, and a limitations section that names our own worst
defect. Compare the GVS5H blog post filed the same day, whose headline number
was attributed to "researchers evaluated the system" with no protocol.

## The finding

Four sub-agents — Explore Files, Debug One, Revise Patch, Generate Tests — with
strict decomposition. Evaluated on SWE-Bench Lite (300) and Verified (500),
800 runs total.

| Configuration | Pass rate | Cost/issue |
|---|---|---|
| Human-written tests | **94.3%** | **$1.01** |
| Human-written, no debugging sub-agent | 87.2% | $0.73 |
| **LLM-generated tests** | **68.0%** | **$4.12** |

Baselines on Lite with human tests: Agentless 61.0%, SWE-Agent 49.0%,
ExpeRepair 48.6%, OpenHands 47.8%. TDFlow 88.8%.

Their conclusion, verbatim:

> "the final hurdle in LLM repository-scale issue resolution lies within test
> generation."

**The LLM writing the checks is 26 points worse and four times more expensive
than not writing them.**

## Why it bears on a decision that is still open here

The gate author question. On 2026-09-20 this project ran **28 gate re-issue
rounds** and produced two gates that were independently verified as
unsatisfiable: S13-1G demanded the frozen S11 rule be an executable expression
tree when the real rule is declarative config, and S13-2G treated "External
benchmark" and "TEAM RECOMMENDATION" as mechanisms requiring substantive
sections. Both passed their own selftests.

That was our evidence, anecdotal and n=2. This is the same finding at n=800 on
a standard benchmark, with a cost column.

It does **not** settle the question, for the reason in the next section, but it
is the first external measurement bearing on it.

## The qualifier, which matters

**Their "human-written tests" are SWE-Bench's gold tests** — the tests the real
commit had to pass. That is closer to an answer key than to a check written in
advance by someone who knows the system but not the solution.

So 94.3% does not mean "a knowledgeable seat pre-registering a check reaches
94%". It means the ceiling is very high **when the tests are correct by
construction**. The direction transfers to our case; the magnitude does not.

SWE-Bench Verified also guarantees each instance is solvable from the issue
description, which removes a failure mode we actually have.

**Internal inconsistency to avoid quoting wrongly:** the paper reports **68.0%**
in Table 2 and **69.8%** in the discussion for the same configuration.

## Where our design is ahead, which is rare enough to record

Their limitations section, verbatim:

> "if the provided tests are truly unsolvable, TDFlow will keep performing main
> algorithm iterations until the iteration limit has been reached. **There is
> no early-stopping mechanism or critic** that can be used to save resources."

That is precisely S13-1G — a check no faithful artifact could satisfy — and
they have no answer for it beyond an iteration limit. It is also the unbounded
repair edge that consumed three campaigns here: 9 rounds on gen120, 42
verification documents against 6 closed rows, 28 gate re-issues.

The bounded repair budget, and treating exhaustion as a publishable finding
rather than an error, is a place this project is ahead of a published system.

## Cheap things worth considering

1. **Measure gaming.** They manually inspected all 800 runs and found **7
   instances of test hacking**, counted as failures, with a rubric in Appendix
   C. We have never measured whether an artifact games its check rather than
   satisfying it. A rubric costs nothing and the number is interesting whatever
   it says.
2. **Cost per sub-agent.** Dropping their debugging sub-agent cost 7 points and
   saved 28% of spend. That is the kind of arithmetic we have never done for a
   seat — we add and remove roles by argument, not by measured contribution.
3. **The decomposition itself** is the third independent arrival at role
   separation with reduced context per agent, after GVS5H and our own.

## Status

- **Paper:** real, read in full, evidence-backed.
- **Domain caveat:** code repair with an executable oracle. Most of our rows
  have no oracle, which is why the two-lane split exists. This corroborates the
  decidable lane and says nothing about the judgment lane.
- **Not a memory-system candidate.** It publishes nothing about memory.
- **Open question it informs, and does not close:** whether a gate should be
  authored blind. Tern's decision.

## Tern disposition — 2026-09-21

Retain as relevant evidence; no new package or active-contract change.
Checked against [v2](https://arxiv.org/html/2510.23761v2).
Corrections qualify the intake above rather than erase it:

- 800 is the reported human-test hacking audit, not a paired test-generation
  comparison. Appendices exclude 22 Lite and 45 Verified instances.
- Use Table 2's 68.0%, noting inconsistent prose. Supplied gold-test costs
  exclude human test creation; this is not an end-to-end authorship-cost trial.
- Generated tests with zero bad-test rate yield 93.3% success; this selected
  subgroup supports test validity, not a causal human-author advantage.
- TDFlow has a ten-iteration cap. Our relevant distinction is owned early
  disposition, not boundedness itself; operational superiority is unmeasured.

Director interpretation: this is related evidence, not 800 replications of our
unsatisfiable-gate finding. Keep the blindfold decision open. A gate author
needs real input/schema access; independence from the candidate is a separate
question. A faithful positive control plus negative controls is more useful
than selftests alone, without pretending to prove complete adequacy.

Gaming review and role ablations are worthwhile future measurement ideas.
Use a preregistered rubric, denominator and adjudication; separate evidence of
bypassing the requirement from an ordinary defect, and measure audit effort.
Role ablation should compare matched tasks, total cost and human intervention;
never remove binding independence merely to save a seat. These are proposals,
not amendments to running P4. Judgment-lane requirements remain unchanged.
