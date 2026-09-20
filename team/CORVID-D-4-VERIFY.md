# CORVID-D-4-VERIFY — verification of the re-done seat_mute in-flight guard

Verifier: corvid-dsh, 2026-09-17 10:27 PDT (clock-read at close). Author: kiln-flash;
check amendment: cairn. Prior measurement cited: cairn's CHECK AMEND on the row —
the original check passed VACUOUSLY (suite green with zero in-flight cases; grep
count 0), the 15:01:34Z evidence-close was voided, and the row re-opened on
evidence. This verification is of the re-done work against the amended check.

## Verdict: VERIFIED PASS

## What was checked

1. **Amended declared check, run verbatim**
   (`bash /home/bmosher/conductor-chat/workers/test-fleet-poller.sh && grep -Eqi 'in[ -]flight' .../test-fleet-poller.sh`):
   suite **116 passed / 0 failed**; in-flight grep HIT; `bash -n` clean on both
   files. The two halves together cannot pass vacuously: the grep asserts
   in-flight coverage exists in the suite, the suite runs it against the real
   guard — pre-guard code fails the case (mute5 expects NOT-mute where the old
   logic returned mute).
2. **Guard source read** (fleet-poller.sh:44-52, 296-362): `STREAM` derives
   from `POLLER_STREAM` or `${HIST%/*}/acp-stream` — absolute, no `$HOME`/cwd
   dependence (the 2026-09-16 standing rule). `seat_mute` parses the session's
   stream jsonl: `t:"start"` adds the item to a set, `t:"end"` discards; any
   unmatched start → turn in flight → exit 1 (NOT mute) before answers are
   judged at all. Malformed lines are skipped; an unreadable stream sets
   `inflight=False` and falls back to the pre-existing answer-based judgment —
   never worse. The mute semantics are otherwise unchanged (too-few answers →
   not mute; all-stall-marker tail → mute).
3. **The suite's in-flight cases are the row's scenario, not a stub**: mute5
   holds THREE stall markers in history (old logic: mute) plus a stream whose
   newest item is an unended start → asserts NOT mute; mute6 (turn ended)
   asserts still mute — the guard does not over-fire; mute7 (garbage line plus
   a parseable unended start) asserts the guard survives a corrupt line.
4. **Direct probes of my own** (sandboxed `POLLER_SOURCE_ONLY=1` source +
   crafted fixtures, six seats): 3 stall markers + unended start via the
   **POLLER_STREAM override** → NOT mute (the override is honored at call
   time); 3 stalls + empty stream file → MUTED (empty stream falls back to
   answers); 3 stalls + end-without-start only → MUTED (a stray end cannot
   fake in-flight); 3 stalls + two completed turns + one unended → NOT mute
   (set semantics survive interleaving); empty history + missing stream → NOT
   mute; 3 stalls + missing stream file → MUTED (pre-existing heuristic
   intact). All six as designed.
5. **Transient-failure disclosure, tested**: kiln disclosed one unreproduced
   115/1 run at ~09:3x under possible concurrent suite load. I ran the suite
   four more times (one in the declared check, three consecutively just now):
   **116/0 every time**. Unreproduced in nine total runs across two seats. If
   it recurs, the FAIL line names the case.

## Observations (recorded, not defects)

- A crashed turn whose `start` never gets an `end` leaves an unmatched item,
  so that seat reads in-flight until an end appears or the stream rotates:
  the mute heuristic stays suppressed for it. This is fail-OPEN (a healthy
  seat is never falsely muted — the exact harm the row exists to prevent);
  the cost is that a genuinely dead seat may keep receiving verification
  routes. If that ever shows up in practice, the fix is a stream-side
  end-on-crash write, not a change to this guard's judgment order.
- The guard keys on the stream surface being written by the worker; the live
  poller picks it up on its next managed restart (kiln's note).

## Result

Row D-4: the amended check passes with real coverage, the guard implements
the row's rule (never judge a seat with a turn in flight; blocked ≠ broken),
and my independent probes agree with the suite. VERIFIED PASS.
