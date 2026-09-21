# The minimal loop — requirements, revision 2

Written 2026-09-20. Revision 2 supersedes v1 (`4a8716f8e2ca04f0`, preserved at
`LOOP-REQUIREMENTS-20260920.v1-superseded.md`) after Tern's review
(`team/.director-loop-review.md`).

Her verdict was **"preserve the simplification, revise the guarantees."** She
was right, and v1's guarantees are withdrawn rather than defended. What changed
is listed at the end so the correction is checkable, not just claimed.

This is not derived from principles. It describes what happened on the evening
of 2026-09-20, when one row went from question to committed, pre-registered
negative result in forty minutes with every timer stopped — corrected by what
that same evening proved the description got wrong.

---

## Two lanes

v1 had one lane and exiled everything else. That was the largest error.

**The mechanical lane** takes work with a declared, checkable completion
contract.

**The judgment lane** takes everything else — what question matters, whether a
measurement is valid, whether an audit is adequate, what Brian should care
about. It gets a **named reader, a bounded effort, and a recorded disposition
that is equally visible.** It does not get a numeric bar, and it is not
invisible.

*Why both.* Mechanising judgment consumed three campaigns. But hiding judgment
is how Brian discovers that something has been waiting on him without his
knowing. Tonight's index review and this design review are judgment-lane work.
They were the most valuable output of the day and neither could pass a gate.

---

## The mechanical lane

### 1 → ADMITTED

**Requirement.** The row declares an artifact, a command, and *what the check
must establish*. A named reader then confirms, in one pass, that the contract
measures the intended question.

**Not** "a file can decide it." `true` is a command. Both failed S13 gates
named an artifact and a command; one demanded the frozen rule be an expression
tree it has never been, the other required a substantive section for
"External benchmark" and "TEAM RECOMMENDATION". Naming fields is not
decidability. Someone has to read the interface — that is a prerequisite to
specifying a check, not a breach of independence.

**Also distinguish finishing from succeeding.** A properly executed negative
experiment is finished. An invalid measurement is not a null merely because a
command returned a number.

### 2 → REGISTERED

**Requirement.** Criteria, bar, and pinned inputs committed **as their own
commit, before the runner or any result exists.** The evidence of order is
**commit ancestry**, not a hash.

*Why the change.* v1 said "the criteria existing before the result cannot be
faked, and a hash proves it." That is false. A hash proves content identity,
not chronology. The row that motivated this document introduced registration,
runner and results together in `99d8f6f`, so it does not demonstrate the check
it argued for. Ancestry proves recording order; it still does not prove absence
of prior exposure, so the registration must also disclose prior exposure and
pin code, input and environment versions.

**The bar must carry a number.** v1 wrote "materially above" a floor. That is
not a bar.

### 3 → RUN

**Requirement.** The author produces results and a verdict carrying the
registration commit and `verified_by: null`, writes a receipt (below), and
stops.

### 4 → REPRODUCED

**Requirement.** A different agent, **blind-first, not blind-forever.** It
freezes its own result *before* reading the author's verdict, then reads it and
examines any divergence.

*Why the change.* v1 said "never the verdict." That makes claim review
impossible. Tern caught three errors in my brief tonight *after* reading it, by
tracing claims to sources. Anchoring is the risk; permanent blindness is not
the cure — ordering is.

**The receipt must record which of three things happened**, because they carry
different weight:

| check | what it establishes | what it cannot |
|---|---|---|
| re-execution | execution integrity | shared code keeps shared bugs |
| independent derivation | the measurement, implemented twice | a shared invalid definition |
| validity review | does this measure the intended thing | nothing — this is judgment |

**Equality settles only deterministic replay** with pinned code, inputs and
environment, over meaningful fields. For stochastic runs — the local pilot,
anything model-in-the-loop — tolerances are predeclared, or the loop will
exhaust every row on ordinary sampling variation.

**"Different seat, fresh context" is a procedure, not proof.** Seats share
files, implementations and model-specific errors. Independence is claimed by
the receipt and bound to an actor and artifact versions; it is not structural.

### 5 → SETTLED, or EXHAUSTED

**Requirement.** One initial attempt plus at most one repair. Stated as a
budget, not an established optimum.

Four boundaries matter more than the integer:

1. **Bound the attempt, not only the count.** A round counter does not stop a
   hang. Each attempt carries a wall-clock limit and a distinct **blocked**
   disposition. v1's "the row ends, always" was not supplied by a counter.
2. **The budget follows the question**, not the row id. A rename or an amended
   declaration must not reset it, or the old retry ladder returns with fewer
   lines of code.
3. **Implementation repair is not amendment.** Correcting the runner to match
   the registered rule is a repair. Changing the population, metric or bar
   after seeing results is a new exploratory row.
4. **Exhaustion reports why**: valid measurements disagreeing, a broken
   environment, and a run that never completed are three different findings.
   "Could not reproduce within this budget" is an operational result, not proof
   that a finding is false.

At the cap, automatic repair stops and a bounded evidence packet goes to a named
decision-maker. Extension is a new explicit allocation with its cumulative cost
visible — never an automatic appeal.

---

## The receipt — one line per attempt

This is the record that makes four of the requirements above enforceable
instead of asserted. Append-only, beside the verdict, in the shape of the
escalation ledger, which already works.

```
question_id        stable across renames - the budget follows this
attempt            integer
role               author | reproducer
actor              seat + model + version
registration       commit id
inputs             hashes of every frozen input
runner             hash of the code that ran
started_at
ended_at           absent = still running, or died
outcome            settled | diverged | blocked | never_completed
why_ended
check_performed    re-execution | independent_derivation | validity_review
runtime_s
cost
human_touches      a person had to intervene
```

**What it enforces, that nothing else can.**

- **Binding.** A declared author and a null verification field are assertions
  until something ties them to the real actor and the exact bytes. This ties
  them.
- **Exhaustion reporting.** `why_ended` is the requirement above, stored.
- **Liveness without a scheduler.** `started_at` with no `ended_at` past the
  wall-clock limit is how the overseer sees stopped work. It is the answer to
  the objection that removing the daemon makes Brian the liveness monitor.
- **An effort alarm with real units.** Measured runtime, cost and human
  attention, reported separately, **including failed attempts.**

**Everything else is derived, never stored:** first-attempt success is
`attempt == 1 and outcome == settled`; rejection rate is a ratio over outcomes;
the effort ratio is reproducer effort over author effort.

**`human_touches` is the one field no machine can fill.** It will be
under-counted. An under-counted number that trends upward is still the only
signal that would have answered "is this working" on 2026-09-20 without Brian
asking eight times.

**It replaces rather than adds.** `fleet-ratio` (374 lines) and
`fleet-discipline` (355 lines) both measure how effort is spent, both measure
*activity* rather than outcomes, and neither has ever changed a decision. This
is one appended line.

---

## Supervision

> **No autonomous work-creation scheduler. One supervising process that cannot
> create work.**

v1 said "not a daemon," which was too blunt — the overseer is a daemon, and it
was the most useful thing built that day.

The overseer reads receipts and notices: registered but never run; run but never
reproduced; an attempt past its wall-clock. It has **no authority to start a
row**. Its own repair budget must be declared, or it recurses through repairs
exactly like the ladders it replaces.

*Why no scheduler.* On 2026-09-20 the timers produced thirty escalations into
an empty room and zero research rows. That is one bad day, not a law — the
tradeoff being accepted is **less unwanted work in exchange for more attention
at start and handoff**, and it is a tradeoff, not a free win.

---

## The enforcement layer

| check | how | mechanical? |
|---|---|---|
| admission fields present | field presence | yes |
| contract measures the question | a named reader, one pass | **no — judgment** |
| registration precedes results | commit ancestry | yes |
| reproducer ≠ author | receipt actor comparison | yes, once bound |
| attempt count | integer | yes |
| attempt wall-clock | receipt timestamps | yes |
| divergence is real | comparison, then judgment | **partly** |
| budget extension | a named decision-maker | **no — judgment** |

v1 claimed four mechanical checks were the whole apparatus. They are not: input
integrity, exit-status interpretation, result completeness, the comparison
itself, and the binding between registration and reproduction all have to exist.

---

## What is claimed, and what is proven

**Proven, 2026-09-20:** one row went from question to committed, pre-registered
negative result in forty minutes with every timer stopped.

**Not proven:** reproduction, exhaustion, the ancestry check, the receipt, and
the effort ratio. None has been exercised end to end.

**Withdrawn from v1:**

- *"Sixteen of twenty prevented."* The failure clusters total 23 by mechanism
  and 20 by detection with no unique incident map. The number does not derive.
- *"7:1 and 1:10 effort ratios."* 42 documents ÷ 6 closes is documents per
  closed row. 34.6% is a share of overlapping labels. Neither is effort.
- *"A hash proves it."* It proves content identity, not chronology.
- *"Never the verdict."* Replaced by blind-first.
- *"The row ends, always."* A round counter does not bound a hang.

**The defensible claim, in full:** removing autonomous scheduling and gate
generation eliminates several known defect sites and sharply reduces
opportunities for repeated repair. It leaves a simpler set of obligations. It
does not mechanically settle sixteen failure classes.

---

## What this makes impossible, that we will miss

1. Unattended progress across a dependency chain. The intended trade.
2. Exact-match settlement for stochastic work — hence predeclared tolerances.
3. Exploratory work inside the numeric lane, which must stay visible in the
   judgment lane rather than be pushed to invent a success number.
4. Repairs worth more than two attempts, recoverable only by explicit new
   allocation.
5. Error localisation from the author's account — preserved by blind-first.
6. A shared view of an experiment blocked on a judgment or an authorization.
   **This is the failure mode to watch:** two tidy halves can recreate the
   hidden pending decision.

**The loss that must not be accepted:** making Brian the invisible scheduler,
discrepancy resolver and liveness monitor. That reduces code by moving the work
onto the person the project exists to help. The receipt and the overseer are
the answer, and they are the part not yet demonstrated.

---

## How to falsify this

One row is registered, run, and reproduced by a second agent from the
registration alone, producing its own numbers, with receipts written at every
attempt.

If reproduction fails, that identifies a defect in the contract or the
execution — it does not by itself refute registration-first work. If it
succeeds, that proves the loop runs; it proves nothing about whether the
measurement was valid.

**Neither outcome settles this document. Only running it does.**
