# Decisions and findings, 2026-09-20

Written because this was settled in conversation and would otherwise live only
in scrollback. Short on purpose. Each entry is a conclusion, its evidence, and
where the detail lives.

Companion documents: `LOOP-REQUIREMENTS-20260920.md` (the design),
`POSTMORTEM-CLAUDE-20260920.md`, `RUNBOOK-20260920.md`,
`WHAT-WE-BUILT-20260920.md`, and Tern's three reviews in
`team/.director-*.md`.

---

## The diagnosis

**The thing that spirals is repair, not review.** Review is naturally bounded —
two agents, one pass, a verdict. "Is it fixed yet" is a judgment and does not
terminate. Same edge, three different machines:

| | unbounded arm | count |
|---|---|---|
| rivals, gen120 | repair → re-review | 9 rounds |
| campaign-1 | verification documents | 42, against 6 closes |
| iteration 3, today | gate re-issue | 28 rounds |

`gate-batch` carried the first cap in three campaigns (`GATE_MAX_REISSUES=6`).
It fired, printed `RE-ISSUE LIMIT reached`, exited 1 — and I read the only
correct refusal in the system as a fault.

**Only admit work whose completion a file can decide.** Not because judgment is
worthless — it produced the most valuable output of the day — but because
judgment cannot be *looped*. S13-1 (countable) finished in forty minutes. S13-2
(an audit) was stuck three days across two gates and a re-issue ladder.

**Gated verification was not wrong.** It worked wherever the row had a countable
outcome; corvid confirmed the gate machinery fails honestly. It failed where the
row's outcome was a judgment, because there the gate could only check the
*shape of the prose* — S13-2G required a substantive section for "External
benchmark" and "TEAM RECOMMENDATION".

**What multi-agent actually buys: disagreement.** Every time a second agent
earned its cost, it was contradicting the author — corvid rejecting both S13
gates, the overseer finding a defect in my repair five minutes after starting,
Tern correcting three of my claims tonight. Not throughput: 13 seats once spent
$21.65/day for three lines of code, 58% of it on polling.

---

## Naming, which I had wrong

The corpus knows **campaign-1** and **campaign-2** only. There is no campaign-3
document in 827 files. What we have been calling campaign 3 is **iteration 3**
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
  5,697 files — the frozen 827-document corpus with labels and index, 11
  verdicts, external cards, `ANSWER.md`, Tern's reviews, S13-1 entire.
- **Does not carry:** poller ×2, sprint-next, gate-batch/gate-write, the quota
  failover ladder, the board's machine column, 51 dead scripts, 19 unused
  lanes, `fleet-ratio`, `fleet-discipline`.
- **Stays in the repo but unwired:** the 112 checkers. One is adopted when a
  row declares it.

---

## Implementation, decided but NOT started

**The loop contains zero model calls.** Every transition is parsing, git
ancestry, two integers, two timestamps, or `==`. The models do the work; they
are not in the state machine. Tonight's run demonstrates it.

**Go, not scripts.** Nine of today's twenty defects are classes a compiler
catches: absence-as-value (2) is `*int` vs `int`; free-text state predicates (3)
are unwriteable against an enum; counter-key ≠ reset-key (4) is one struct
field. agent-deck is itself Go (`go 1.25.13`) and the iMessage bridge is Go, so
it is not a new language here. `go` is **not currently on PATH** and golang is
not installed.

**Determinism is provable, not merely claimed.** Five states and about a dozen
inputs: enumerate every state × input exhaustively and assert the result. For a
machine this small that is a proof, not sampling. Termination is checkable the
same way.

**Caveat:** a deterministic loop does not make the *work* deterministic. Corvid
diverged from me tonight, legitimately. Determinism means divergence is handled
identically every time, not that it disappears.

**Size estimate: 300–500 lines.** The plan is mostly the test list, because for
a state machine the tests are the specification.

**The one LLM doing a machine's job:** the overseer noticing stopped work.
Reading receipts for a start with no end past its deadline is a timer.

---

## Changing the loop, once it exists

**A change to the loop is a row in the loop.** Register what changes and what
test proves it; run the patch plus test; the overseer reproduces by running a
suite it did not write.

**Hard, mechanical criterion:** a change arrives with a test that **fails at the
parent commit and passes after**. The overseer checks out the parent, runs the
new test, asserts it fails. No test, or one that passes at the parent →
rejected without discussion.

**Three boundaries:** the overseer gets the same budget (reject once, repair
once, then Brian); **the overseer may not review its own changes**, or
authorship has simply moved to the reviewer; and a declared emergency path where
a provisional patch **auto-reverts** unless it completes the full path inside a
stated window — without the revert, the ceremony is bypassed on the first
emergency and never returns.

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
| **1** agent-deck out of the box, + conductor chat UI + sprint board | **not done** | still on 1.16.4; 1.16.10 exists and is unmeasured. Nothing native has been diffed against our 82 live scripts |
| **2** minimal loop, a use case per part | **done** | `LOOP-REQUIREMENTS-20260920.md` rev 2 — reviewed twice by Tern, amended, and run once end to end tonight |
| **3** observability use cases + roadmap with phases | **partly** | Tern's index review answers "where we are" on the research. The phased roadmap to the project goal does not exist |
| **4** critical roles and escalation paths | **partly** | author, reproducer, named reader and overseer are defined. Ownership of an ordinary handoff and of a blocked attempt is **not** — Tern's answer to that question was flatly "not yet" |
| **5** storage, memory, artifacts — what goes where, tracked, dispositioned, disposed | **not done** | untouched. The receipt schema is the natural seed for it |

Cheapest next, and they gate the rest: **1** is an afternoon; **4** is a page.
**5** falls out of the receipt schema. **3** last — a roadmap written before the
pilot has run is a guess.

---

## Research state

**S13-1 is VERIFIED and the answer is negative.** The S11 corpus-coverage rule
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

**Corpus:** 827 documents frozen and labelled, 1,519 role labels; 29 newer
documents in a separate cohort; frozen snapshots verified untouched.

---

## Open items

1. **Corvid's divergence against me.** Threshold 0.5: 13 answerable probes
   declined vs my 10. Cause: my runner pools every inscribed record so later
   records support earlier queries; corvid built the corpus at each probe's own
   position. Three probes cross: `s1-R403`, `s2-R1204`, `s2-R1603`. **The
   reproducer's reading is the one my own pre-registration specifies.** The
   repair budget is spent, so this is an amendment or a new row for a named
   person — currently Brian, which is what step 4 exists to fix.
2. **Handoff ownership is unnamed** (Tern, question 3: "not yet").
3. **The prior-only label control** has not run.
4. **S13-2 (the mechanism audit)** — Tern's advice is to drop it; corrected
   Round-2/3 work already covers those systems.
5. **Three survivors the loop does not fix:** web-UI ownership from
   `groupPath`, billing identity from adapter name, corpus-in-two-places.
6. **Who watches the overseer.**

---

## Operational state at close of 2026-09-20

**Stopped and disabled:** `fleet-poller.service`, `fleet-window-up`,
`sprint-next`, `gate-batch`, `agent-deck-failover`, `fleet-stalled`,
`poller-liveness`. **Nothing starts work tomorrow.**

**Still armed, read-only:** `fleet-spend-stop`, `sprint-status`,
`escalation-watch`. **Leftovers that fire tomorrow evening and do nothing
useful:** `fleet-discipline`, `fleet-ratio`, `fleet-window-down`.

**Running:** the overseer, as `agentdeck_fleet-overseer_*`. The GLM promotion
expired today, so kiln and corvid now cost real quota.

**Nothing is being built.**
