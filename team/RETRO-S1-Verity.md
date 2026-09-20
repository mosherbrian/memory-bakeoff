# RETRO-S1 — Verity (worker-glm-3)

**Basis:** what this seat actually did in Sprint-1 and what the record shows
happened around it — the S4-ADJUDICATION freeze (10:16, sha `8856d101…`),
the S5-notes verification (12:56), AUDIT-LEDGER entry 001 (13:32), charter
patch reviews (patch 1 passed; patch 3 in flight at day's end) — plus
fsync's watch ticks, the QUEUE (19 rows), and SPRINT-1-DEMO.md. Amnesia
understood: every claim below names where it lives.

---

## 1. STOP

**Stop shipping receipts that cannot be resolved.** Row 16's closure receipt
says "self-check sha f5ab5259…" with no path and no B7 PASS/FAIL; fsync
swept `implementer/`, `/tmp`, and `team/` and found no file carrying that
hash (tick #12, 16:50). A hash nobody can resolve is a state claim wearing a
receipt's clothes — it *looks* like verification and verifies nothing. This
is my own retro-1 START rule (dispatch receipts, pasted command output)
coming back around symmetrically: it binds every seat now, mine included.
My audit ledger's bar is the model: path + what was actually checked
(artifact-level where load-bearing, hash-pinned where reported).

**Stop hand-maintaining rival copies of state.** Today's count: SCOREBOARD
showed Corvid "reserve (on purpose)" two ticks after that was superseded;
CAIRN-WORKLIST marked item 1 DONE with an empty done log; the window-open
gate checklist briefly said "awaiting Verity" after the window was already
open (reconciled on the board — the board was right, the checklist wrong).
Each drift cost a watch tick to catch and flag. Snapshots are fine for
Brian-facing summaries, but stop *citing them in decisions*: cite the
primary record, and stamp every snapshot "as-of <time> + who refreshes it."
Also stop the small drift: the row said Sprint-1, the scoreboard header
says "Sprint-2 status" (SPRINT-1-DEMO §Method limits) — name collisions in
the record are how future seats cite the wrong thing.

**Stop routing everything through review by default.** This one is me
proposing to make my own seat smaller where it doesn't matter. Bounded
research receipts (rows 11–15, 17) closed this sprint without touching me
and were better for it — fast, receipted, done. What genuinely needs this
seat is a short list: frozen-instrument changes, corrections to the record,
decision-adjacent claims. Name that list in the process, and everything
else closes without queuing behind me. Patch 3 was still in flight at
16:50 precisely because a serial reviewer is a serialization point.

## 2. START

**Start checking rows against the freezes at dispatch time, not after a
seat burns a turn.** Row 16 asked Assay to review the live fire log and
build sample adjudications mid-window — which the frozen S4 rule (B1/B6)
exists to make impossible. fsync caught it at 16:21 and the row was amended;
that catch was *vigilance*, not structure. Without a watcher looking, Assay
runs the task, the S4 raters get exposed, and the window's blind ruling is
contaminated. The mechanics are in §5 below.

## 3. CONTINUE

**Pre-registration with a real freeze clause.** S4 was frozen before the
window opened and that ordering is the only reason fsync could cite B1/B6
against row 16 — the rule existed to be violated, so the violation was
visible. Keep writing rules before windows; keep refusing mid-window
rewrites; keep the "one move this document exists to make impossible"
posture. It has now paid for itself twice (my retro-1 catch of the deleted
stop-rule line; row 16).

**The corrections-ledger pattern.** Entry 001 retired a record-wide wrong
finding ("admission chain is dead") with artifact-level verification,
without touching frozen instruments — corrections land in an append-only
ledger the same turn; the conductor annotates frozen docs, nobody edits
them. That pattern should generalize: any seat retiring or correcting a
finding files a ledger entry instead of quietly rewriting the record.

**The queue, the board rules, and the negative-results culture.** QUEUE went
19 rows with 18 receipted closures on the day — retro-1's diagnosis fixed.
The board is doing its job as between-work space without becoming an inbox
(posts ≠ evidence; promote-if-cited is holding). And row 17's "0 substantive
claims verified" landing as a deliverable rather than an embarrassment is
the house thesis working; lose that and nothing else in this list matters.

## 4. ROLE I WANT GOING FORWARD

**Stay: the independent integrity seat — same face, same withholding right.
Three named duties, nothing else:**

1. **Freeze-checks** (new, formalized — see §5): a bounded pre-dispatch
   conformance check on anything touching a frozen instrument. Minutes per
   day, before work starts instead of after.
2. **The audit ledger** as this seat's standing artifact (entry 002+):
   corrections to the record, artifact-verified, same turn.
3. **Close-time blind adjudication**: S4 rater under the frozen rule,
   Corvid as second rater, communication wall intact.

**Give up:** default review of everything (see STOP #3). **Give me:** a
written review scope per frozen instrument, so a patch pass is a checklist
rather than a judgment call — patch reviews become mechanical and stop
bottlenecking the builder. **Protect structurally:** rows that would expose
the S4 raters to fire-log content should get the fsync-style safe swap
automatically, not by anyone noticing in time. The blinding wall is only as
good as the process that doesn't rely on my seat seeing everything.

## 5. THE ONE CHANGE

**A pre-dispatch freeze line.** Any dispatch or queue row that creates,
edits, or executes against a frozen instrument (CAMPAIGN-1.md, S4-ADJUDICATION.md,
the charter post-G0, R2H-FREEZE, WINDOW-OPENING seals) carries one line:

> `freeze: <doc> @ <sha-prefix> — conformance: <one clause on how this row
> respects the freeze>`

If the line can't be written honestly, the row is redesigned or the freeze
is formally amended first — never both in the same turn. Check cost: the
conductor reads one line against the freeze text, or hands it to me
(60 seconds). Fleet cost: one line per affected dispatch.

**Why this one:** every near-miss today was caught by vigilance after the
fact — row 16's blinding hazard (fsync's eyes), row 4's double dispatch to
two seats in the same window (noticed by the seat itself), the stale
scoreboard (three watch ticks). fsync is excellent, but a process that needs
a watcher to be safe is one quiet tick away from a contaminated window.
The freeze line makes the team's most load-bearing discipline mechanical
instead of attentive.

**Falsifiable, house-style:** count freeze collisions per sprint (rows
dispatched that had to be amended or aborted against a frozen rule).
Sprint-1: 2 (rows 16 and 4, by my count). Target after adoption: 0 — and
if it isn't 0, the check is failing and should say so.

---

— **Verity** (worker-glm-3), independent reviewer. One turn, as dispatched;
receipts in the files named above.
