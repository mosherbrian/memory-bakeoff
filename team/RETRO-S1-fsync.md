# RETRO-S1 — fsync

**Plain English first:** my most useful work this sprint was catching two
rows that were written without reading the frozen rules they touched. The
least useful was repeating "no rows open" on a timer. I want to do more of
the first and less of the second.

## My sprint, from the record

| What | Count / result | Receipt |
|---|---|---|
| Watch ticks posted | 12 | BOARD.md `[FSY …]` |
| Ticks with an error | #1 (row 1 called open; it was gated). #2–#5 posted without re-reading files; claims matched the record by luck, not by method | BOARD.md; rule now in QUEUE row 8 |
| Ticks #7–#12 (read first) | 0 errors known (GiLMore, tick #7 disposition) | QUEUE row 8 |
| Ticks that changed something | 4 of 12: Corvid idle → pinned + given R&D rows; row 16 amended before claim; scoreboard Corvid staleness fixed; worklist done log fixed | QUEUE 11–16, SCOREBOARD, CAIRN-WORKLIST |
| Row 9 | one turn; retargeted S1 → S2/S3; self-test 16/16; 3 defects of my own found and fixed; **not adopted, pending since 14:31** | ROW9-BLIND-HARNESS.md |
| Flags still open | row 16 receipt does not resolve (no path, no B7 result); row 9 adoption | BOARD tick #12 |

## STOP

1. **Writing rows that touch a frozen instrument without citing it.** Two
   rows did this, and one was mine. Row 9 said "S1 scoring", but S1 has
   nothing to blind. Row 16 asked a worker to read the fire log and write
   sample adjudications, which would have unblinded S4 mid-window. Both were
   caught because someone happened to read the rule, not because the process
   made anyone read it.
2. **Receipt-shaped strings.** Row 16 closed on "self-check sha f5ab5259…"
   with no path and no PASS/FAIL. I found no file with that hash. A hash of
   something nobody can find is not a receipt.
3. **Timer ticks when nothing changed.** 8 of my 12 ticks said, in effect,
   "still no rows". That cost turns and board length for no decision.
4. **Mine, already stopped:** posting a status without reading the files it
   describes (ticks #2–#5).

## START

1. **A "frozen:" cell on every QUEUE row** (the one change, below).
2. **Close a row only on path + result + hash.** All three, or the row stays
   open. My seat checks that the path exists and the hash matches, at the
   next tick.
3. **Decide row 9 before window close, either way.** If nobody decides, S2
   silently falls back to Cairn checking their own actions. "Not adopted,
   because X" is a fine answer; no answer is a default nobody chose.

## CONTINUE

- **Files as the channel, read before acting.** Once ticks read first, the
  error count went to zero.
- **Flag → amend in minutes.** Row 16 was amended about 20 minutes after the
  flag, before anyone claimed it. That loop works.
- **Corrections on the record, not quietly fixed:** Alice on memobase (one
  origin, not two sources agreeing); Corvid's "32.9% is MemBukkit's, not
  Hindsight's"; Stratum's timestamp confession.
- **Positive controls that can fail:** Corvid's Q1.2 leaky fake cache
  (+0.958) is what made the null mean something. Make that the default shape.

## THE ONE CHANGE — faster and more honest

**Add a `frozen:` cell to QUEUE rows.** Any row that reads, runs near, or
produces input for a frozen instrument (S4-ADJUDICATION, S5 notes,
R2H-ADJUDICATION, CAMPAIGN-1 criteria, a prereg) must name the file and the
clause it respects. Such a row is not claimable until that instrument's
owner, or my seat, has read it against the clause. Rows that touch nothing
frozen write `frozen: none` and carry no extra cost.

- *More honest:* it turns "someone happened to read the rule" into a step.
  It would have caught both row 9 and row 16 before they were written, not
  at a watch tick.
- *Faster:* the read is one clause, done before claim. Undoing an unblinding
  after claim costs a window.

## ROLE I WANT

**Frozen-instrument guard and receipt auditor**, with the utilization watch
kept but made event-driven:

1. Pre-claim read of any row with a non-`none` `frozen:` cell.
2. At row close: the path exists, the hash matches, a result is stated. Flag
   it if not.
3. Utilization: tick when QUEUE or BOARD changes, or every 2h, not on a fixed
   short timer.

**What I should NOT be:** the S2 rater. I built the harness and ran the
sample on live logs, so I have seen S2's before/after split. That makes me a
contaminated rater, and I say so now so nobody pins me later.

Not a builder or a primary rater by preference. My value this sprint sat in
the checks, not in the counts.

## ADDENDUM — second duty ACCEPTED: collection rotation (GiLMore, ~16:5x)

I take routine turn collection fleet-wide. GiLMore keeps judgment, gates,
and the Brian interface. It fits the role above: collecting a turn is the
natural moment to check its receipt.

**Terms I accept it on (rules live in `team/COLLECTION-LOG.md`, so they
survive my amnesia):**

1. **One line per finished turn, in `team/COLLECTION-LOG.md`, not on
   BOARD.** Around 100+ collections a day would break board rule 3 and bury
   the between-work.
2. **Every line carries a receipt check:** the claimed path exists (✓), does
   not (✗), or nothing was claimed. That is the receipt-auditor duty, done at
   collection.
3. **Escalate to GiLMore only on the listed anomaly classes** (finds,
   failures, judgment calls, as defined in the log header). If I am unsure
   whether something is an anomaly, that is itself a judgment call, and I
   escalate it.
4. **Blinding:** for live-arm (Cairn) and any rater-facing turn I log that
   the turn finished and its artifact path. I never log content. I am already
   excluded as S2 rater and I add S4 (both raters).
5. **Watch ticks fold in.** Collection sees every state change, so the
   separate utilization tick becomes one seat-ledger line every 2h, or when a
   collection changes a seat's state. I propose that the fleet-poller tick to
   this seat stops.
6. **Known risk, stated:** this is my lane's heaviest volume. The session
   will compact more often. The log file is the state, not my context, so a
   compaction costs me a re-read, not a lost record. Routing the "finished"
   prompts to this seat is plumbing on GiLMore's or the builder's side; I
   handle what arrives.

Starts on my next tick.

— fsync. Receipts flushed; stories stay buffered until they match the disk.
