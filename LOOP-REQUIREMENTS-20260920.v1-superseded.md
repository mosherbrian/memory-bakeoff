# The minimal loop — one requirement per transition

Written 2026-09-20. Step 2 of Brian's five. Nothing here is proposed because it
would be nice to have: **every part names the defect it prevents, drawn from
the twenty found on 2026-09-20** (`team/FAILURE-CLUSTERS-20260920.md`), and the
last section names the four it does not fix.

This is not a design derived from principles. It is a description of what
happened on the evening of 2026-09-20, when one row went from question to
committed negative result in forty minutes with the fleet switched off.

---

## The admission rule, before any state exists

> **A row is admissible only if a file can decide when it is finished.**

It must name an artifact and a command. Nothing else is a row.

A question whose answer is a judgment — "audit these mechanisms and recommend
one", "is this thorough enough" — is real work and often the most valuable work,
but it is **not looped**. It goes to a person or to the director, with a
deadline and a reader, and comes back as prose that someone reads.

*Why.* Three campaigns were consumed by machinery built to close rows that could
not be closed, because their completion condition was an opinion. S13-2 has been
stuck for three days across two gates and a re-issue ladder for exactly this
reason. S13-1 finished in forty minutes.

**Prevents:** M6 (a gate that passes its own selftest while the verifier has
rejected it — a countable row needs no prose gate). Removes the need for the
free-text state predicates behind all three M2 defects.

---

## Transition 1 → REGISTERED

**Guarantee.** The criteria and the bar exist, and provably predate any result.

**Evidence that decides it.** A registration file exists, it is hashed, and its
commit is older than any result file. Two integers and a string comparison.

**Who.** Whoever will do the work — *not* a separate authoring service, and
*not* blind. They may read the system. They may not read the results, because
there aren't any yet.

**What it must contain.** The frozen inputs and their hashes; what will be
measured; what counts as success, stated as a number; a commitment to report
every arm, not the winning one; and an explicit statement that a null is
publishable.

*Why not blind.* Writing a test from prose alone, by an author forbidden to look
at the system, produced 28 re-issue rounds and two gates that could not accept
any faithful artifact. One demanded the frozen rule be an expression tree it has
never been. The other walked headings and required a substantive section for
"External benchmark" and "TEAM RECOMMENDATION". Ignorance was never the source
of rigor. **Order is** — the criteria existing before the result is what cannot
be faked, and a hash proves it.

**Prevents:** the authoring loop entirely. There is no second party to argue
with about whether the gate is fair.

---

## Transition 2 → RUN

**Guarantee.** Results exist, and the author has stopped.

**Evidence that decides it.** The named artifact exists; the command exits; the
verdict carries the registration hash and `verified_by: null`.

**Who.** The author. Their last act is writing `null`.

*Why.* On sprint 6 the same seat wrote the work and the test that proved it. The
author declaring their own work verified is the defect the entire project was
built to eliminate, and it is the one position I have occupied throughout.

**Prevents:** M1's provenance defect — authorship inferred from the act of
claiming. The author declares authorship in the verdict; they cannot declare
verification.

---

## Transition 3 → REPRODUCED

**Guarantee.** A second agent produced the same numbers from the same frozen
inputs, without seeing the first agent's reasoning.

**Evidence that decides it.** A second result file, written by a different seat,
whose values match. Comparison is `==`, not judgment.

**Who.** A different seat, fresh context. It reads **only** the registration and
the pinned inputs. Never the author's verdict, never a handoff, never a summary.

*Why this specific rule.* The original rivals design had it right: both
reviewers read the repository, blind to each other, so their attention went to
the code rather than to Claude's account of the code. We lost that. Tonight
Tern read my brief and three of its claims were wrong — she caught them only
because she went to the sources anyway. A reviewer reading the author's summary
is reviewing the author.

*And the weak spot it closes.* "Verified" has meant two different things:
re-running a gate, and reading a verdict for internal consistency. Only the
first is reproduction. This transition permits only the first.

**Prevents:** M1 provenance; M8's divergent-reader defect (one ledger, one
reader, one comparison).

---

## Transition 4 → SETTLED, or EXHAUSTED

**Guarantee.** The row ends. Always. In a bounded number of attempts.

**Evidence that decides it.** Numbers match → SETTLED. They differ → one repair
round, then re-reproduce. **Cap: 2.** An integer.

**Exhausting the cap is a published result**, not an error:
*"could not be reproduced in two attempts; the author got X, the reproducer got
Y, they diverge at Z."* That is a finding worth writing down.

*Why this is the single most important line in the document.* Review is
naturally bounded — two agents, one pass, a verdict. **Repair is not**, because
"is it fixed yet" is a judgment. This is the identical unbounded edge in every
campaign, with entirely different machinery each time:

| | the unbounded arm | count |
|---|---|---|
| rivals, gen120 | repair → re-review | **9 rounds** |
| campaign-1 | verification documents | **42**, against 6 closes |
| iteration 3, 2026-09-20 | gate re-issue | **28 rounds** |

`gate-batch` was the first component in three campaigns to carry a cap
(`GATE_MAX_REISSUES = 6`). It fired, printed `RE-ISSUE LIMIT reached`, exited 1
— and I treated the only correct refusal in the system as a fault.

**Prevents:** both M3 retry-ladder defects (a counter keyed per kind and reset
per row; a chase reset by a verdict but not by new work). A cap on rounds has
one key and cannot disagree with itself.

---

## The standing rule: it is not a daemon

> **A row runs when a person starts it.**

No poller. No sprint timer. No window. No dispatch.

*Why.* Across three campaigns nothing was ever improved by work starting without
a person. On 2026-09-20 the timers produced thirty escalations into an empty
room and zero research rows. The one piece of automation worth keeping is the
**overseer**, and only because it *reacts* to breakage rather than manufacturing
work — it acknowledged two escalations with real fixes within five minutes of
existing, including a defect in a repair I had shipped two hours earlier and
believed was complete.

Pull, not push.

**Prevents, by simply not existing:** M1 escalation transport (whichever process
won a port) and M1 role identity (a title prefix); all three M2 free-text
predicates, which live in the poller, `gate-batch` and `sprint-status`; M3's
per-row-checked / per-round-spent ceiling and the stale-brief guard; **both** M4
defects, where an empty quota reply and an unreadable window were each read as
"exhausted" and parked the fleet hourly; all three M5 defects, which are
supervision *of a daemon*; M7, the fallback that sat below the layer that
deferred before reaching it; and M8's sprint-close file disagreeing with the
computed board.

---

## The enforcement layer, in full

Four mechanical checks. No model decides any of them.

| check | how |
|---|---|
| admissible | row names an artifact and a command |
| registered first | registration hash exists; its commit predates results |
| reproducer ≠ author | different seat, fresh context — structurally cannot be |
| bounded | round count ≤ 2 |

That is the whole apparatus. It replaces 8,228 lines of loop and 1,003 lines of
gate machinery.

---

## The one number that says it is happening again

**Verification effort ÷ production effort.**

- campaign-1: ~7:1 — 42 verification documents against 6 closed rows
- the corpus as a whole: **34.6% of every role label is `verification`**
- 2026-09-20 evening: roughly 1:10 the other way — forty minutes of work, and a
  reproduction that is one script and two integers

**Alarm at 1:1.** Past that, the apparatus is eating the work, and it is visible
months before it becomes twenty defects in a day.

---

## What this does NOT fix — four of the twenty

Stated plainly, because a proposal that claims everything is the failure mode
this document exists to end.

1. **M1, ownership in the web UI** — derived from a session's `groupPath`. The
   UI survives this design and so does the defect. It needs `FLEET_SEATS`.
2. **M1, billing identity** — cost attributed to an adapter's name rather than
   the model behind the gateway. Untouched.
3. **M8, artifact visibility** — the corpus on disk and the repository seats
   resolve against were 983 files apart. One location for one fact is a
   discipline, not a transition.
4. **Who watches the overseer.** Removing the daemon removes the three M5
   supervision defects and introduces one new instance of the same class: the
   overseer is a process that can stop, and nothing currently notices. This is
   the honest cost of the design, and it should be solved before it is deployed,
   not after.

**Sixteen of twenty prevented. Four not. One new risk, named.**

---

## What survives, and what is deleted

**Survives:** the lanes (zero defects today), the conductor web UI, agent-deck,
the escalation ledger, the overseer, and the discipline that produced tonight's
result — a frozen declaration, pinned input hashes, criteria written first.

**Deleted:** the poller and its divergent twin, `sprint-next`, the gate-writing
service and its re-issue ladder, the board's machine column, the quota failover
ladder, the stall detector and the poller-liveness timer that watched it.

---

## The claim this document makes, and how to falsify it

One row, on the evening of 2026-09-20, went from question to committed,
pre-registered negative result in forty minutes, with every timer stopped and
no seat but the author. It is awaiting reproduction by corvid, which is the only
part of this loop not yet demonstrated end to end.

**If corvid cannot reproduce it from the registration alone, this document is
wrong about its central mechanism** and should be rewritten rather than
defended.
