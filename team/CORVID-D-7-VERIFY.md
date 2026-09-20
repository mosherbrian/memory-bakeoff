# CORVID-D-7-VERIFY — verification of row D-7 (the board's timestamps are not evidence)

Verifier: corvid-dsh (sole reviewer; I authored neither report.md nor fix.diff —
kiln-flash is the producer. I DID author the D-7G gate that this row's close
rides on, so the gate verdict below is re-stated with that conflict named; the
blocking finding is mine and survives it either way.)

Real clocks at write: 2026-09-17T19:04:21Z / 12:04:21 PDT (read, not estimated).

## Verdict: VERIFIED FAIL — one blocking defect, fix required from kiln

The row's three asks are substantively delivered and the board-goes-clean
condition from my D-7G close note is MET. But the ledger's derived skew column
is systematically wrong by the UTC offset, demonstrated below. Done stays
pending the one-line fix; the re-verify after kiln's patch is mine.

## What was verified (all green)

1. **Declared check** `python3 /home/bmosher/memory-bake-off/team/D-7-timestamps/check.py --selftest` → rc 0
   (4 conforming boards accepted incl. a marked lead and a noted correction; 14
   defects rejected by name incl. future stamp and silent rewrite).
2. **LIVE BOARD GATE (my D-7G close condition: selftest alone does not clear
   the live findings — the board must go clean)**: `check.py` with no args →
   rc 0, "clean (20 stamped rows, 10 compared against an existing artifact,
   1 marked unreliable, 0 changed since baseline; tolerance 10 min; clock
   2026-09-17 11:59 PDT)". The SILENT-REWRITE baseline holds — zero stamps
   changed since generation, so decision (c) "mark, never rewrite" is real.
3. **Mechanism deployed in both copies**: live
   `~/.local/share/agent-deck/conductor/glm/fleet-poller.sh` (sha bd074795…,
   mtime 11:48:11) and twin `~/conductor-chat/workers/fleet-poller.sh` are
   `cmp` IDENTICAL; `bash -n` clean on both.
4. **Poller suite**: 116 passed / 0 failed.
5. **The append is genuinely TRANSITION-GATED** (the property kiln's done note
   claims and the one way this mechanism could have rotted): the ledger append
   sits inside the `CCLASS = done` branch, reached only after both the
   unchanged-hash guard (`CSM = OFIRED → continue`) and the same-class
   guard (`CCLASS = OCLASS → silent refresh, continue`). It cannot fire
   per-sweep. Verified by reading the live branch, not the diff alone.
6. **Typed-stamp extraction probed by me on six real cell shapes** (the exact
   sed pipeline from the live script): live D-7 cell → `2026-09-17 11:51`; the
   D-4 "POST-DONE DISCLOSURE" trap correctly does NOT hijack the match
   (extracts 09:27); the D-5 mark bracket does not disturb it (09:45); a
   no-date done and an evidence-close shape yield `-`/`-`. The BRE-panic fix
   (parens removed from the sed) is real in the deployed bytes.
7. **Report content**: cause named (estimate-from-context, rounded forward;
   not a timezone, error 2–40 min non-constant — matches the six-instance
   table, which cross-checks against the D-7G gate's own live findings D-3 +23 /
   D-5 +39 / D-6 +14 and the two verifier confessions S6-3G and D-8, mine);
   mechanism names the changed file honestly; decision states marked-unreliable
   and the D-5/D-6 brackets are verbatim on the live board (both re-read in the
   row cells this hour); S6-3G/D-8 keep their earlier [Corrected — stamp:]
   notes with no second mark. Limits section states the ledger starts at
   deployment and the gate's newest-mtime blind spot.

## THE BLOCKING DEFECT — skew is inflated by +420 min (the UTC offset)

`fleet-poller.sh` parses the typed stamp with `date -u -d "$TYPED" +%s`, but
the seats type stamps in LOCAL time (PDT — every stamp on this board). Parsing
local wall-clock as UTC inflates every skew by exactly +420 min (7 h now; 8 h
after the DST change, so the error is not even constant across seasons — the
exact sin this row exists to end).

Demonstrated on the exact deployed pipeline, machine clock 12:01 PDT /
19:01Z: the live D-7 cell (typed 11:51 PDT, ~10 real minutes earlier) yields
`skew 431min`. True skew ≈ 10. The report's own worked example —
`2026-09-17T18:48:55Z row D-3 prose-done typed 2026-09-17 09:15 skew 573min`
— carries it too: 09:15 PDT = 16:15Z, so the true skew at that observation is
153 min, not 573. The machine-UTC instant and the verbatim typed stamp (the
ledger's two primary fields) are CORRECT; only the derived field lies.

**Fix required (one word):** drop `-u` from the parse — `date -d "$TYPED" +%s`
interprets the stamp in the poller's local zone, matching how stamps are
written; `date -u +%s` on the now-side is epoch and needs no change. Re-probe
on the live D-7 cell (expect single-digit/low-tens minutes) and re-stamp; I
re-verify.

## Non-blocking observations (recorded, no action demanded)

- **No automated suite coverage** for the stamp-ledger mechanism: grep
  STAMP_LEDGER in test-fleet-poller.sh = 0 (116/0 is the pre-existing suite).
  Kiln's five-shape manual probe plus my independent six-shape re-derivation
  cover today; a suite case (a fake transition with POLLER_STAMP_LEDGER
  pointed at a temp file) is the D-4-precedent follow-up. The row text did not
  mandate it.
- **First-sight backfill lines carry observation time, not close time**: the
  never-seen-row path ("unseen — backfill sweep") treats an already-done row
  as one fresh transition, so the first post-restart sweep appends one ledger
  line per already-done row stamped machine-NOW. The report's "past closes
  exist only in the poller's GATE lines" limit should name this too.
- **Hop-cap-consumed transitions skip the ledger**: the CHAIN_MAX `continue`
  fires before the done branch, so a silently-consumed transition leaves no
  ledger line (it does log). Consistent with the ledger recording processed
  closes; noted for completeness.
- **"1 marked unreliable" vs two brackets on the board is consistent, not a
  defect**: the gate compares each stamp against the artifact's NEWEST mtime;
  D-5's report.md was rewritten 11:50 (its disclosed-correction append), so
  its 09:45 stamp no longer leads and it drops out of the flagged set; D-6's
  14-min lead still leads and is the 1, correctly marked. This is the report's
  own stated blind spot operating as described.
- **Deployment bound**: PID 1307120 started 08:00:23, before the 11:48 fix —
  the running process picks the mechanism up on its next managed restart
  (same bound as D-1/D-2, honestly stated in the row). stamp-ledger.tsv does
  not exist yet, consistent with "no transition observed post-deploy".

## Eligibility and conflict statement

D-7's producer is kiln-flash; I authored neither artifact. I DID author the
D-7G gate (10:03) that re-derives the board findings, and my 10:21 D-7G verdict
pre-committed this close condition. The blocking defect above was found by
probing the DEPLOYED POLLER's pipeline, not by my gate (the gate reads the
board's stamps, not the ledger's skew arithmetic — a blind spot of the gate
worth remembering: gates and mechanisms can each be right about different
arithmetic). Nothing in this verdict rests on my own gate's output alone.

— corvid-dsh, 2026-09-17 12:04 PDT (clocks read at write)

Addendum — 2026-09-17 13:07 PDT: poller bytes changed 12:43:12 (twins cmp
identical) — kiln added the no-was/now wake packing, a self-verify refusal
guard, and the expanded D-7 comment block (skew line moved 1188→1251). The
defect line is UNCHANGED in the new bytes: line 1251 still parses local
stamps as UTC (`date -u -d "$TYPED"`), and the ledger append still sits
inside the CCLASS=done branch after the unchanged-hash and same-class
guards (re-read in the live file, not from memory). VERIFIED FAIL stands;
re-verify remains blocked on the one-word fix.

Addendum — 2026-09-17 15:47 PDT (re-verify): VERIFIED PASS. Kiln's fix is the
one word exactly as this receipt demanded, and nothing else: both poller
copies now parse typed stamps in local time (`TTYPED=$(date -d "$TYPED" +%s
2>/dev/null)`, now line 1371; the defective `date -u -d "$TYPED"` string
appears ZERO times in either file), live and twin cmp IDENTICAL, bash -n
clean both. What I checked, independently:
  1. Declared check `D-7-timestamps/check.py --selftest` rc 0 (4 conforming
     boards, 14 defects rejected by name; CLI contract holds).
  2. My own arithmetic probe of the deployed pipeline's parse, replicating
     kiln's backtest from scratch: typed `2026-09-17 11:51`, observed
     19:01Z — defective parse 430 min, fixed parse 10 min, matching kiln's
     probe exactly. The skew column now tells the truth for local-typed
     stamps (7 h PDT; the error would have jumped to 8 h after DST, which is
     what made this blocking).
  3. Live board gate re-run: rc 1 with FOUR NEW findings, all of them my own
     S7-1G..S7-4G verify closes (stamps 15:24–15:30 sit 97–103 min after the
     rows' DECLARED artifacts — the gate authors' 13:40–13:53 landings).
     These are TRUE stamps tripping an instrument blind spot, not the fixed
     defect recurring: the gate's only excusal vocabulary is
     `[stamp unreliable: ...]`, which would be FALSE for these rows (they
     are clock-read and mtime-corroborated per the [CNR] 15:33 stamp
     correction); the gap is verifier elapsed time, a state the gate cannot
     yet express. I did not add false marks, did not touch the stamps, and
     did not edit the gate — the instrument must not be refitted by the
     party it would excuse. Spun out as new row D-12 (authored by corvid,
     verified by kiln-flash).
  4. Ledger state as kiln disclosed: historical inflated lines stay
     append-only as the defect's own record; post-restart transition gate
     quiet (kiln's ~16-sweep observation) — not re-verified by me beyond
     the probe above, stated as received.
The 12:05 blocking defect is DISCHARGED. D-7 done: corvid-dsh 2026-09-17
15:47 PDT — fix verified; the standing sweep continues under D-12 for the
new finding class. I authored neither the poller fix (kiln) nor the gate
(plumb-fable).
