# Decisions and findings, 2026-09-20

Written because this was settled in conversation and would otherwise live only
in scrollback. Short on purpose. Each entry is a conclusion, its evidence, and
where the detail lives.

**Companions are snapshots, not current truth.** `WHAT-WE-BUILT-20260920.md`
still says no task outcomes were ever measured and that the filename control had
not run; both were overtaken the same evening. Read each with its date.

Companion documents: `LOOP-REQUIREMENTS-20260920.md` (the design),
`POSTMORTEM-CLAUDE-20260920.md`, `RUNBOOK-20260920.md`,
`WHAT-WE-BUILT-20260920.md`, and Tern's three reviews in
`team/.director-*.md`.

---

## The diagnosis

**Repair is the recurring uncontrolled edge.** Repeated repair and re-review had
no effective stopping policy in any campaign. Note the weaker claim: review is
**not** naturally bounded either — it is bounded only when policy bounds its
scope, time and repetition. Reviewers can expand scope, disagree indefinitely or
hang. What is true is that "is it fixed yet" had no stopping rule anywhere. Same edge, three different machines:

| | unbounded arm | count |
|---|---|---|
| rivals, gen120 | repair → re-review | 9 rounds |
| campaign-1 | verification documents | 42, against 6 closes* |
| iteration 3, today | gate re-issue | 28 rounds |

\* the 42/6 count does not separate repair from initial verification or useful
investigation. It is a document count, not proof of the diagnosis.

`gate-batch` carried a cap (`GATE_MAX_REISSUES=6`). It fired, printed
`RE-ISSUE LIMIT reached`, exited 1 — and I read a correct refusal as a fault.
"The first cap in three campaigns" and "the only correct refusal" are unsourced;
what is established is that this cap fired and was misread.

**Only mechanically checkable contracts enter the mechanical lane; judgment work
gets a named reader and a visible disposition.** (An earlier line here said
"only admit work whose completion a file can decide", which contradicts the
two-lane design already agreed with Tern. Corrected.) Not because judgment is
worthless — it produced the most valuable output of the day — but because
judgment cannot be *looped*. S13-1 (countable) finished in forty minutes. S13-2
(an audit) was stuck three days across two gates and a re-issue ladder.

**Gated verification was not wrong in principle**, but "it worked wherever the
row was countable" is **false**: S13-1 is countable and its gate still demanded
input shapes that do not exist. A verifier catching a defective gate is evidence
for independent scrutiny, not evidence that the gate worked. Gates failed worst
where the row's outcome was a judgment, because there a gate can only check the
*shape of the prose* — S13-2G required a substantive section for "External
benchmark" and "TEAM RECOMMENDATION".

**What multi-agent buys: independent scrutiny**, of which disagreement is only
the visible part. Agreement after a competent independent check earns its cost
too, and disagreement can itself be wrong. In this project every time a second
agent earned its cost it was contradicting the author — corvid rejecting both S13
gates, the overseer finding a defect in my repair five minutes after starting,
Tern correcting three of my claims tonight. Not throughput: 13 seats once spent
$21.65/day for three lines of code, 58% of it on polling.

---

## Naming, which I had wrong

The corpus knows **campaign-1** and **campaign-2** only. No campaign-3 document
appears **in the selected 827-file index** — which is a search scope, not proof
the term was never used elsewhere. "Campaign 4" is therefore a new initiative
and profile name; it should not be read as implying an established campaign 3. What we have been calling campaign 3 is **iteration 3**
of the loop. Two counters have been running. The 42-documents-to-6-closes
figure is a fleet measurement of **2026-09-15**, campaign-1 era — not campaign 2
as I said.

---

## Campaign 4 — two goals that must not merge

**Research goal** (Tern's north star): does a small, reversible memory aid
improve Brian's real work across compaction and restart? First move is the
**local cairn pilot** — already authorized, $0, no further scope decision
needed. Two plumbing pairs, then eight scored pairs.

**Machinery goal:** the loop, and nothing else.

**Governing rule: machinery gets built only when a row needs it.** No
infrastructure sprint.

**Fresh `agent-deck -p campaign4` profile, not a fresh install.** Profiles
already exist (`default`, `claude`); a clean slate is one flag. A reinstall
means re-plumbing the lanes, which is how campaign 4 becomes an infrastructure
project in week one.

- **Carries, by repository not by copying:** `team/` on `fleet/team-corpus`,
  5,705 tracked paths at commit `20f393a` — **and `implementer/repo`, which is a
  SEPARATE git repository contributing zero files to that branch.** Tern's
  synthesis rests on its corrected Round-2/3 findings, the live Pi outcome
  results, and closure records. Carrying only `team/` would silently drop the
  older half of the evidence base. Preserve both by location and commit, pinned.
  Earlier text said 5,697 files — the frozen 827-document corpus with labels and index, 11
  verdicts, external cards, `ANSWER.md`, Tern's reviews, S13-1 entire.
- **Not wired into the new profile** (NOT an authorization to delete evidence or
  recovery assets): poller ×2, sprint-next, gate-batch/gate-write, the quota
  failover ladder, the board's machine column, 51 dead scripts, 19 unused
  lanes, `fleet-ratio`, `fleet-discipline`.
- **Stays in the repo but unwired:** the 112 checkers. One is adopted when a
  row declares it.

---

## Implementation, decided but NOT started

**Zero model calls in the transition engine — a boundary requirement, not an
observation.** The engine consumes authenticated dispositions produced by
judgment work; it does not call a model itself. Tonight's run was manual and
does not establish this. It also does not follow that all of the overseer's
diagnosis and review work is a machine's job; timeout detection is.

**Go, a chosen tool — not a demonstrated cure.** Go permits unsafe assumptions
about optional values, free-text comparison, incomplete switches and wrong
resets; types make some mistakes harder, they do not prohibit these semantic
bugs. The four M3 incidents were also not all counter-key/reset-key defects —
two were budget-scope and freshness-scope mismatches. The defect classes that
motivated the choice: absence-as-value (2) is `*int` vs `int`; free-text state predicates (3)
are unwriteable against an enum; counter-key ≠ reset-key (4) is one struct
field. agent-deck is itself Go (`go 1.25.13`) and the iMessage bridge is Go, so
it is not a new language here. `go` is **not currently on PATH** and golang is
not installed.

**Exhaustive transition tests, but not a proof of the system.** Enumerating a
finite state/input table checks that table against its specification. It does
**not** prove the specification is right, and it does not cover unbounded
counters, timestamps, artifact contents, crashes, duplicate or out-of-order
events, or external effects. Determinism and termination are separate
properties: a perfectly deterministic machine can wait forever. Termination
needs bounded attempts **plus** assumptions about timeout delivery and
supervision. Keep the exhaustive test requirement; the proof-of-determinism
claim is withdrawn.

**Caveat:** a deterministic loop does not make the *work* deterministic. Corvid
diverged from me tonight, legitimately. Determinism means divergence is handled
identically every time, not that it disappears.

**Size estimate: 300–500 lines — an estimate, not a budget that licenses
omitting error handling, receipts, storage, authentication or supervision.**
Separate a small pure transition core from those. Tests are executable examples
of requirements, not a substitute for the requirements that say whether a test
is right. The plan is mostly the test list, because for
a state machine the tests are the specification.

**The one LLM doing a machine's job:** the overseer noticing stopped work.
Reading receipts for a start with no end past its deadline is a timer.

---

## Changing the loop, once it exists

**A change to the loop is a row in the loop.** Register what changes and what
test proves it; run the patch plus test; the overseer reproduces by running a
suite it did not write.

**Criterion for a bug fix, not a universal admission rule:** a regression test
that **fails at the parent commit and passes after**, with the **intended
failure reason** declared — a test can fail at the parent merely because it
imports a new API or will not build, which proves nothing. Refactors, dependency
and security maintenance, documentation and dead-code removal are valuable with
no behavioural test that fails at the parent; require evidence matched to the
change class rather than forcing an artificial failure. The overseer checks out the parent, runs the
new test, asserts it fails. No test, or one that passes at the parent →
rejected without discussion.

**Three boundaries:** the overseer gets the same budget (reject once, repair
once, then Brian); **the overseer may not review its own changes**, or
authorship has simply moved to the reviewer; and an emergency path with a **tested, bounded rollback or safe-stop and a named
recovery owner** — blanket auto-revert is not universally safe, since a
migration can make rollback destructive and a dead supervisor never executes it.

**Two authority problems this does not solve.** The loop cannot be the sole
authority approving changes to its own verifier, budget or admission rules —
pin the checking version outside the patch. And "a change is a row in the loop"
cannot explain how the *first* loop is authorized; bootstrap needs an authority
outside it. "Then Brian" is the unresolved human-burden issue, not its answer.

**Accepted cost:** the loop becomes slow to change. That is the point —
patch-patch-patch is how 2,388 lines of poller accumulated — and it argues for
the exhaustive transition tests up front.

---

## Brian's five, in his words

Stated 2026-09-20. Quoted rather than paraphrased, because everything below is
scored against them and a paraphrase drifts.

> 1. We look at what the newest agent-deck has out of the box along with our
>    conductor chat ui and the sprint board to the extent it makes sense
>    (maybe/maybe not)
> 2. We ask what would a minimal loop contain and write it down as a use
>    case/requirement for each part of the loop.
> 3. We write down use cases for what our observability needs are - sprint,
>    research, potential future research areas, along with the big picture
>    roadmap and where we are. The roadmap should also show how it leads to the
>    overall project goal with discrete phases/steps.
> 4. We define the critical roles, and escalation paths.
> 5. We define storage, memory, and artifacts, and the rules about what goes
>    where and how it's tracked, dispositioned, or disposed of and when.

And the purpose the five serve, also his words:

> I think with this, we could then do a real architecture and plan, or hand it
> over to be done. This would have unit tests, and system tests, and gates
> phases, and a real architecture rather than accretion of a pile of scripts
> that change each time we hit a bug and build a new chunk that gets thrown on
> the pile. **Each part of the system should not be added unless we justify its
> existence first and know why we need it.**

## Status against those five

| # | state | where it stands |
|---|---|---|
| **1** agent-deck out of the box, + conductor chat UI + sprint board | **not done** | the `-p/--profile` flag is confirmed to exist; the feature comparison and the isolation boundaries are not. "An afternoon" is an estimate |
| **2** minimal loop, a use case per part | **drafted and reviewed; closure pending** | requirements exist and improved across two reviews. Owners and enforcement details are unresolved. **No receipt-backed, ancestry-checked loop has run end to end** — S13 is a manual exemplar, not that demonstration |
| **3** observability use cases + roadmap with phases | **partial synthesis; use cases and roadmap incomplete** | Tern's review gives findings and direction, not the requested use cases or a maintained phased roadmap |
| **4** critical roles and escalation paths | **partial** | roles have names. Ordinary handoff, timeout, exhaustion and supervisor-liveness ownership still need **decisions** — and a page recording them is not the same as completion |
| **5** storage, memory, artifacts — what goes where, tracked, dispositioned, disposed | **partial inputs; policy incomplete** | "untouched" was too absolute: existing repositories, the freezes and the proposed receipt are inputs. Access, canonical location, retention, deletion, migration and recovery do **not** fall out of a receipt schema |

**Do not defer all of step 3 until after the pilot.** A conditional roadmap can
be drawn now — local feasibility → real harness and compaction testing →
representative work — with failure branches, stop branches and authorization
boundaries. The pilot updates it. Brian asked for visibility into direction
*before* an architecture and plan; deferring that repeats the problem this
record exists to solve.

Cheapest next, and they gate the rest: **1** is an afternoon; **4** is a page.
**5** falls out of the receipt schema. **3** last — a roadmap written before the
pilot has run is a guess.

---

## Research state

**S13-1: author execution reproduced, and the negative conclusion independently
confirmed.** Not "every numerical and fidelity question closed" — one divergence
and the corpus-semantics question remain open. The S11 corpus-coverage rule
does **not** transfer. At threshold 0.5 — where it scored 5/5 on our own cases —
it declines **0 of 40** external abstention probes, the same as the five systems
it was meant to beat. Abstentions appear only at 0.75 (6/40, costing 20/80) and
1.0 (24/40, costing 51/80). Mechanism: KnowledgeDrift recombines vocabulary the
corpus already holds — `"ashen estuary ingest job retry budget"` scores 6/6 and
no record holds the combination. **Per-term coverage cannot see a novel
combination of covered terms.**

**What that says about our method:** our own irrelevant queries were irrelevant
*in vocabulary*, which is the easy construction. It bears on every result
produced on self-written cases.

**The corpus labels are not filename-driven.** 20 documents replaced by their
own filenames: 14 produced a label, all `unknown`; 6 produced none. Zero
agreement on 11 pairs, including files with the answer in the name. Tern's
second control — a prior-only baseline, independently adjudicated — **has not
run**, so proportions stay provisional.

**Corpus:** 827 documents **processed** — 757 labelled, 54 producing no label,
16 flagged for review — 1,519 role labels; 29 newer
documents in a separate cohort; frozen snapshots verified untouched.

---

## Open items

1. **Corvid's divergence against me.** Threshold 0.5: 13 answerable probes
   declined vs my 10. Cause: my runner pools every inscribed record so later
   records support earlier queries; corvid built the corpus at each probe's own
   position. Three probes cross: `s1-R403`, `s2-R1204`, `s2-R1603`.

   **Correction, and it is mine.** I wrote that the reproducer's reading is the
   one my pre-registration specifies, repeating corvid's report. **The sentence
   corvid quoted is not in the registration.** Verified: `grep` for "own
   position in the ops stream" in `PREREGISTRATION.md` (sha `7e0484db`) returns
   zero. What the registration actually says is *"The corpus is the records
   inscribed by that stream"* — which is **ambiguous**, and if anything reads
   closer to the pooled interpretation I implemented.

   That changes the classification. Aligning code to a protocol that was already
   fixed would be an implementation *repair*. Resolving a protocol that is
   genuinely ambiguous is an **amendment**. This is the second kind. The budget
   being spent does not decide the scientific question either way.

   It is also the third time today I relayed a claim I had not checked. Tern
   caught it; I did not.

   A second error inside corvid's report: it says threshold 1.0 "declines
   everything", contradicted by its own grid — 24/40 and 51/80, not all probes.
   And at 0.75 and 1.0 the 20/80 and 51/80 counts are **answerable probes
   rejected**, never demonstrated destroyed answers. Corvid also showed it used
   inscriptions *before* each probe, which closes future-record leakage but is
   **not** full live-store replay with `supersede` replacements and removal of
   released or purged records. That distinction stays open.
2. **Handoff ownership is unnamed** (Tern, question 3: "not yet").
3. **The prior-only label control** has not run.
4. **S13-2 (the mechanism audit)** — Tern's advice was to **narrow** it: reuse
   the corrected Round-2/3 work and consider only a justified delta for a
   genuinely new mechanism. "Drop it" overstated her disposition; what should be
   dropped is the current broad row.
5. **Three survivors the loop does not fix:** web-UI ownership from
   `groupPath`, billing identity from adapter name, corpus-in-two-places.
6. **Who watches the overseer.**
6b. **Liveness BETWEEN units of work — found 2026-09-21.** The design watched
    work that started and did not finish, never work that finished while
    nothing started. Tern stopped at a package boundary she had authority to
    cross; nothing could tell that from a campaign that had finished. This is
    M5 ("supervision covers failure, not absence") reproduced in the design
    written to replace the system that had it. **Fixed where it is fixed:**
    `campaign4-watch` detects the state fault (six branches tested, both
    legitimate rest states included); `campaign4/CHARTER.md` carries the
    standing boundary instruction so it survives a session reset; r2's package
    requires the director to dispose or open a successor without a prompt.
    **Still open:** nothing yet writes the machine-readable declaration the
    watcher reads, so it falls through to a 45-minute silence check. r2 owns
    the schema.
7. **Receipt persistence and actor binding** — a self-written actor field is an
   assertion; binding needs a trusted launcher.
8. **Timeout enforcement, and who may mark an attempt blocked.**
9. **Question-level budget ownership.**
10. **How a judgment-lane dependency is resolved and propagated** to the rows
    waiting on it.
11. **Bootstrap and change-control authority** outside the loop itself.
12. **Safe rollback**, tested and owned, rather than blanket auto-revert.
13. **The local pilot still needs** its frozen treatment, numeric resource caps
    and instrumentation. Authorization is not an executed protocol.
    Private-transcript scale-up remains unauthorized, and operator burden (M4)
    is unmeasured without a design for it.

---

## Operational state at close of 2026-09-20

**Stopped and disabled:** `fleet-poller.service`, `fleet-window-up`,
`sprint-next`, `gate-batch`, `agent-deck-failover`, `fleet-stalled`,
`poller-liveness`. **Nothing starts work tomorrow.**

**Still armed — and NOT all read-only, which I got wrong.** Verified from the
unit files: `fleet-spend-stop.service` runs the bare command, not `--status`,
so it **can write a dispatch-stop marker**. `fleet-window-down.service` runs
`fleet-window down`, an **action** that will try to stop seats tomorrow at
18:00. Also armed: `sprint-status`, `escalation-watch`, `fleet-discipline`,
`fleet-ratio`. Do not classify a leftover as harmless without reading its
`ExecStart`.

**Running:** the overseer, as `agentdeck_fleet-overseer_*`. The GLM promotion
expired today, so kiln and corvid now cost real quota.

**Nothing is being built.**
