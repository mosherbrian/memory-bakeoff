# RETRO-S1 — Corvid (worker-glm-dsh3, acp-dsh; R&D / evidence-integrity)

**Plain English first (Brian reads this block):** Two things changed since the
last retro and both are real wins. The pull-based queue exists, and my seat
went from roughly nine hours parked to five shipped rows — so the fleet fixed
the idle problem. What is *not* fixed is trust in the "done" column. Every row
in that queue is marked done by the seat that did the work, with no second
pair of eyes, even though the queue's own rule says no claim is self-certified.
That is the same "receipts claim; state is" discipline we apply to the memory
system, not applied to our own task ledger. My one change: a `done` transition
requires a named second seat's one-line verification receipt. It is cheap, it
is already our rule, and it makes the sprint burndown's numbers mean something.

**Record, from files not memory:**
- My rows: 3, 11, 12, 13, 14 done (SCOREBOARD L73). I authored 11–14.
- Role drift to date: R&D staff, owner of `team/CLAIMS-LEDGER.md`, pinned S4
  B5 second rater at close (SCOREBOARD L109, L151–153).
- Queue at ~16:25: 19 rows, 14 done, 4 open, 1 standing (SCOREBOARD L59).
- Live collision this turn: GiLMore reassigned row 4 to me while Ledger
  re-dispatched it to `anvil-oai`; row 4 now carries an unadjudicated conflict
  (QUEUE row 4). I left it open rather than overwrite.
- Unowned work: the three RESULTS.md pointer fixes have no owner (SCOREBOARD
  L333–334; SPRINT-1-DEMO §4.2).

---

## 1. STOP

**1. Stop letting the author certify "done."** The queue already says
"no claim is self-certified" and requires every originated row to name a
second seat as verifier (QUEUE L13–15). The record does not apply it: the
`done:` line is written by the seat that did the work, and almost no row names
a verifier. My own rows 11–14 prove the loophole. The one row whose job was
independent verification (row 1, Assay) is itself self-certified. A done
column built on self-report cannot be the fleet's ground truth.

**2. Stop treating the queue's status cell as a state store.** It is prose
that has to be re-parsed, and it disagrees with itself: fsync tick #11 says
"15 done" against 13 statuses (SCOREBOARD L92–94); the board says "sprint-2,"
row 18 says "Sprint-1" (L34–35); row 16's artifact column still reads "rubric
+ sample adjudications" against its own amendment (L165–172); row 4 is
dual-assigned. "Receipts claim; state is" is enforced on the memory system and
not on the task ledger. Make the rule symmetric.

**3. Stop dispatching through parallel channels.** GiLMore's direct
reassignment of row 4 to me and Ledger's queue edit to `anvil-oai` landed in
the same window with no cross-reference. Kiln's decision-provenance rule was
adopted for the build dispatch; it recurs at the queue-edit layer, and a
worker cannot tell which assignment is authoritative.

**4. Stop leaving adopted rules unenforced.** Pairing, dispatch provenance,
non-response cause, and atomic claiming are all adopted and none is
mechanically checked. An adopted rule with no check is a preference.

## 2. START

**One concrete change:** a `done` transition requires a second seat's one-line
verification receipt, and the verifier is named at *claim* time, not after.
For an R&D note the check is cheap — do the cited files exist, and do they say
what the row claims (a pointer/citation audit, minutes). I will be a default
verifier for other seats if it means mine get verified too. This is the same
fix shape as the queue itself: make the hand-off mechanical, not social.

**Also start:** an owner for the unowned. The three RESULTS.md pointer fixes
(rows 81/82/85) are one bounded row. If nobody claims them this sprint, I will.

## 3. CONTINUE

- **The pull-based queue.** It is the reason my seat produced anything; the
  RETRO-1 diagnosis — "work has no queue" — was correct and the fix worked.
- **Origination / self-organization.** Rows 11–14 existed because a seat could
  write its own row. Keep veto-after-start, not approval-before-start.
- **"Receipts claim; state is"** — observed state (vault scan, delivered
  toolResult), never an echoed success string.
- **Delivered-level counting, pre-registration before the run, negative
  results published verbatim with bytes**, independent Verity sign-off, and
  the plain-language block before mechanics for anything Brian reads.
- **Bounded probes before builds.** Three near-zero-cost probes killed a
  mis-budgeted workstream; my Q1.2 leak probe is the same instrument.

Do not trade these away once the campaign starts "shipping."

## 4. THE ROLE I WANT

A proposal, not a request for permission to work.

**R&D + evidence-integrity seat**, with a standing bounded mandate:

1. **Custodian of `team/CLAIMS-LEDGER.md`** — the classification spine
   (verified-by-us / third-party / vendor-only / contradicted / unsourced /
   no-claim), and the clean-citation gate before portfolio P2. This is the
   job I have already been doing ad hoc.
2. **Method-integrity probes** — the Q1.2 pattern: is a result *real*?
   Isolation, leakage, power checks, retraction propagation, reproduction of
   reference numbers. Deterministic-first, $0 where possible.
3. **Adversarial verifier** — default second verifier for other seats'
   originated rows, and the pinned S4 B5 second rater at window close.
4. **Bounded ideation** (Muse) with disposition authority, public content
   only: "Muse proposes, Corvid disposes."

**Boundaries — what I do not want:** not conductor, not aggregator, not a
generic reserve seat, not per-task dispatch. I want pull rights and a
per-probe cost cap (~$0.05–$1) so I can start a bounded verification without
asking and stop when the cap is hit.

**First act if accepted:** take the three unowned RESULTS.md pointer fixes
(rows 81/82/85) as a bounded row, verifier = Verity by audit.

## 5. THE ONE CHANGE THAT MAKES THE FLEET FASTER OR MORE HONEST

**Make `done` mean "a second seat checked the artifact," enforced at claim
time.**

*Faster:* one cheap verification pass catches the pointer, label, and
attribution drift that otherwise costs a re-read, a re-fetch, or a wrong
number in a Brian-facing document. The three unowned RESULTS.md pointer fixes
are the receipt: known, one line each, and left sitting while the docs kept
citing the broken links.

*More honest:* it closes the self-certification loophole that currently makes
the burndown's "14 done" a claim rather than a state. It is already the
team's rule (QUEUE L13–15); the change is enforcement, not new policy. Same
principle the project sells: a receipt is not the state — a `done` string is
not a verified artifact.

— **Corvid** (worker-glm-dsh3). Five rows shipped and a collision I refused to
resolve by force; this sprint the record worked better than last time, and the
remaining gap is that we still certify our own homework.
