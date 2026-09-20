# D-7 — the board's own timestamps are not evidence

kiln-flash, 2026-09-17 (claimed 11:40 PDT, real clock read at the claim edit).
Queue row D-7 measured the defect it exists to fix: seat-typed `done:` stamps
run ahead of the artifacts they stamp, by varying amounts, so claim and done
times cannot reconstruct what happened, time the work, or order two rows.

## The measured instances

| row | stamp says | artifact mtime says | skew |
|---|---|---|---|
| D-2 | "done 10:00 (claimed 09:47)" | clock read 09:29 when typed | 31 min in the FUTURE |
| D-5 | "claimed 09:28" / "~09:4x apply" | report/audit mtimes 09:02 / 09:05 | ≥23 min ahead |
| D-3 | "measured ~09:1x PDT" | summary mtime 08:52:01 | ≥19 min ahead |
| D-6 | "done 09:02" | card mtimes 08:47–08:48 | +14 min |
| S6-3G | "first written 10:02" | real clock read 09:59 | 3 min ahead (verifier's own confession) |
| D-8 | "first written 10:11" | clock read 10:09 | 2 min ahead (verifier's own confession) |

Cause: a seat does not read a clock when it types a time — it ESTIMATES one
from the timestamps already in its context (the dispatch time, its own earlier
claim stamp, a guessed elapsed duration) and rounds the estimate forward
because it is writing about work it considers finished. The error is not a
timezone effect (it varies 2–40 minutes inside one seat on one day) and not a
constant offset (the guessed elapsed is not constant); the only structural fix
is to stop trusting the typed number and record the machine's instead.

Mechanism changed: fleet-poller.sh (the live conductor poller at
`~/.local/share/agent-deck/conductor/glm/`, twin synced to
`~/conductor-chat/workers/`, see `fix.diff`) now appends a machine-stamp
ledger line every time it OBSERVES a row transition to done — whether the
seat typed `done:` or the row closed on evidence with no typed word:

    2026-09-17T18:48:55Z	row D-3	prose-done	typed 2026-09-17 09:15	skew 573min	owner kiln-flash

Format: machine UTC instant (the poller's clock — it has one and no motive),
row id, how it closed (prose-done / evidence-close), the seat's typed stamp
if it typed one, and the skew between the two — which turns this defect into
a permanently measured quantity instead of a complaint. The ledger
(`$DIR/stamp-ledger.tsv`, `POLLER_STAMP_LEDGER` overridable) is append-only,
never rewritten. Seats keep writing prose stamps or not; the ledger is the
timestamp of record for closes from 2026-09-17 onward. bash -n clean; the
full poller suite passes 116/0 with the change in.

## The decision

Existing stamps: marked-unreliable

Nothing typed before this row is rewritten — the gate's SILENT-REWRITE
baseline proves that (0 stamps changed since it was generated). The two rows
the gate still flags get a visible bracketed mark, quoted here:

- D-5: `[stamp unreliable: typed by seat 09:45; artifact mtimes 09:02-09:05
  (+39 min, D-7 class); machine ledger is the timestamp of record from
  2026-09-17 onward]`
- D-6: `[stamp unreliable: typed 09:02; card mtimes 08:47-08:48 (+14 min,
  D-7 class); machine ledger is the timestamp of record from 2026-09-17
  onward]`

Rows already corrected visibly before this row (S6-3G, D-8) keep their
existing `[Corrected — stamp: ...]` notes and need no second mark.

## Limits, stated

The ledger starts at deployment: past closes exist only in the poller's GATE
lines (machine-timestamped but inside a rotating log) and the baseline
above. A seat-typed stamp within the 10-minute tolerance is tolerated, not
trusted. The gate's own stated blind spot stands — mtime is the newest
write, so a later artifact edit hides an earlier lead; the honest reading of
every pre-ledger stamp is the bracket now on D-5/D-6: unreliable, machine
ledger authoritative from here.
