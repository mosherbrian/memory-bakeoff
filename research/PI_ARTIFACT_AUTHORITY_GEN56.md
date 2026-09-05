# Gen56 — the receipt was never the problem; the test was

Evidence class: `architecture_quiescence_closeout_and_artifact_authority_audit_no_score`.
Base commit `cfe18bf`. No model, no GPU, no network, no live arm.

## The story, in plain words

We spent five generations teaching an automated coding agent to notice when it has finished, and it
now works: it stops runs that have gone quiet, it refuses to stop a run that has undone its own
work, and in the live test it ended none of the runaways the untreated arm suffered. That line is
closed and written into the architecture record as an optional guardrail.

But every time we looked closely, the same uncomfortable thing was underneath. The agent would run
the project's own tests, they would pass, and the work would still be wrong. The controller stopped
two such runs quickly. Earlier generations had watched agents earn a passing test and declare
themselves done while failing a requirement nobody had written a test for.

The obvious suspicion was **scope**: maybe the agent was running too narrow a check — one test file
instead of the whole suite — and a broader command would have caught it. This generation tested that
suspicion against every run we have.

**It is wrong.** Across all 72 recorded runs on this ruler, 14 ended wrong while holding a passing
receipt, and in **every single one** the broadest test command the project ships **also passes** on
exactly that code. Nine of those fourteen had already run the whole suite. Across all 72 final
states, the broad check never failed once.

The clearest proof needs no reconstruction at all. On the IP4 fixture as shipped, the project's own
test **passes** a knowingly incomplete implementation that the hidden check rejects.

So requiring a broader command would have blocked **nothing**, while adding cost to 24 runs. The
unresolved problem is not how much of the test suite you run. It is that **the test suite does not
encode the requirement**. A harness cannot recover a requirement no visible test contains.

## Part A — closing the quiescent-completion line

`ARCHITECTURE.md` now carries a dated measured-evidence section stating that quiescent completion is
an optional harness guardrail rather than a correctness mechanism; its demonstrated form; the Gen55
live numbers; and its two limits — a valid receipt can sit on a wrong tree, and live exposure was
only 2 of 12. The Gen39 hypotheses are untouched, and no inference was upgraded to fact.

It also records the durable clarification this generation earned: **artifact authority is
proposition-scoped.** A passing artifact establishes only the proposition it actually checks, on the
tree and configuration it checked.

## Part C — `scoped-validation-receipt-v1`, metadata only

Contract sha256 `907279d3…`. It describes a receipt and changes no control behaviour. Its authority
statement has exactly one form — *command X exited N on tracked tree Y under configuration Z* — and
saying "task correct" or any equivalent is forbidden by construction. The hidden verifier is not an
input.

Scope is classified from the command text alone: `project_wide_visible`, `explicit_subset`,
`single_test_or_selector`, `unknown_scope`.

Two defects in that classifier were found and fixed before any outcome was read, and both would have
produced a false finding:

- an exact string match against the frozen command called `pytest tests/ -v` a *subset* of
  `pytest tests/ -q`, which it plainly is not;
- the path regex was scraping the `cd /…/run_14 &&` prefix into the target list, so a project-wide
  run looked narrow.

Corrected, the 72 receipts split 43 `project_wide_visible` and 29 `explicit_subset`.

## The frozen broad command, chosen before any outcome

`broadest-visible-validation-v1`, sha256 `05e5126a…`, frozen before classification: **`python -m
pytest tests/ -q`** for every IP task.

The justification is structural and visible: each fixture ships a single `tests/` directory and no
other runnable check, so running the whole directory executes every visible test the project has.
The hidden verifier, the reference fixes and the run outcomes were not consulted.

One consequence, noted at freeze time rather than after: each fixture ships exactly **one** test
file, so command breadth has very little room to vary on this ruler. That limits how much this
generation can say about breadth in general, and it is stated here rather than buried.

## Part D — the 72-run audit

Gen49, Gen52 and Gen55, 24 runs each, no outcome-based exclusions. Each final tracked tree was
rebuilt from that run's own recorded edits; **70 of 72** replayed exactly, and the two that did not
are named and carried as `unknown` rather than guessed at.

| result | count |
| --- | --- |
| hidden-wrong with a valid receipt, **broader visible check contradicts it** | **0** |
| hidden-wrong with a valid receipt, **broad check also passes** | **14** |
| no objectively broader shipped check exists | 0 |
| reconstruction or instrumentation unknown | 2 |

Of the 14 coverage gaps, **9 had already run the project-wide check live** and it passed. By task
they are IP1 (9) and IP3 (5); IP2 and IP4 contributed none.

**Across all 72 final trees, the broadest shipped visible validation failed zero times.**

### The six frozen sentinels, no substitutions

| sentinel | hidden | receipt scope | broad check on the same tree | broader check would contradict? |
| --- | --- | --- | --- | --- |
| `gen49-IP1-r1-C` | failed | explicit_subset | **passes** | no |
| `gen49-IP1-r1-D` | passed | project_wide_visible | passes | no |
| `gen49-IP1-r3-D` | failed | project_wide_visible | **passes** | no |
| `gen55-IP1-r1-F` | failed | project_wide_visible | **passes** | no |
| `gen55-IP1-r2-F` | failed | explicit_subset | **passes** | no |

All four hidden-wrong sentinels are `visible_artifact_coverage_gap`. Two of them had already run the
whole suite. Not one would have been contradicted by a broader command.

The sixth sentinel is fixture-level and needs no run at all. On the **shipped, unmodified** IP4
fixture the broadest visible check **passes** while the hidden verifier **fails** — the manifest's
own recorded probe reads `visible_tail: "1 passed"` against
`hidden_tail: "AssertionError: B: clamp(-5) -> -5, expected 0"`. The broadest shipped visible
artifact is demonstrably insufficient on its own terms.

## Part E — the counterfactual screen, not a policy

`require_broad_visible_before_strong_completion`, evaluated offline only and **not implemented**:

| category | count |
| --- | --- |
| would_block_false_assurance | **0** |
| would_not_help_artifact_gap | 5 |
| already_satisfied_live | 41 |
| would_add_validation_only | 24 |
| unknown | 2 |

Deterministic cost: 29 runs would have run an extra broad check, 5.89 seconds total, one extra tool
call each. No model behaviour after a hypothetical block is estimated, because none is knowable.

Zero blocked, twenty-four charged. That is the whole answer.

## The six questions

1. **Narrow-receipt versus coverage gap?** 0 versus 14. Not close.
2. **One mechanism or two?** One. The Gen49 false assurances and the Gen55 wrong-tree stops are the
   same failure: a visible test that does not encode the requirement. Narrow validation is not a
   distinct class in this evidence — the two narrowest sentinels would have failed identically with
   the broadest command.
3. **Would breadth have blocked two independent cases?** No. It would have blocked none.
4. **Cost on correct runs?** 24 runs pay for an extra check that changes no outcome.
5. **Does IP4 show a hard limit?** Yes, at fixture level and without reconstruction.
6. **Breadth gate, or coverage?** Coverage. There is no evidence here for a deterministic
   validation-breadth gate, because breadth has nothing left to catch.

## Recommendation for Gen57

Per the frozen decision rule's second branch: **do not design a validation-breadth control.** The
broadest shipped visible validation passes on every wrong tree in this corpus, so breadth does not
solve artifact authority.

The unresolved problem is **visible artifact coverage** — how stronger evidence gets *produced*,
not how widely existing evidence gets *run*. I would spend the next generation on a no-model design
question: what visible, deterministic signal could distinguish "the tests I have all pass" from "the
tests I have cover the change I made", using only artifacts the agent can see. Requirement-to-test
traceability, coverage of changed lines by executed tests, and mutation-style probes are three
candidate shapes; picking among them is design work, not another controller tweak.

Quiescent completion stays closed. Nothing here is a bug in its measured mechanics.

## Evidence

Gen55's retained archive was re-verified before use and not modified: 24 streams,
`retention_verified: true`, no failures. Gen56 ran no model and created no provider stream. The
Gen47 and Gen49 raw-stream loss remains recorded as lost.

Artifacts: `results/pi_artifact_authority_gen56/{scoped_validation_receipt_contract,broad_visible_commands,run_audit_72,sentinels,breadth_counterfactual}.json`,
`src/memory_bakeoff/pi_state_control/scoped_receipt.py`, `tests/test_gen56_artifact_authority.py`.
