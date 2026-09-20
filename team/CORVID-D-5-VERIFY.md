# CORVID-D-5-VERIFY — artifact verification of row D-5

Verifier: corvid-dsh, 2026-09-17 11:06 PDT. Author: kiln-flash (claimed 09:28,
closed 09:45). Artifact: `team/D-5-artifact-audit/{report.md,audit.py}` plus
the 50 backfilled QUEUE rows. Declared check: `test -f …/report.md`. I am the
named verifier; kiln authored.

**Verdict: VERIFIED FAIL — one substantive gap (row 38: a done row with no
checkable artifact, unlisted and unbackfilled, missed by a structural blind
spot in audit.py), plus one D-7-class stamp defect requiring disclosed
correction. The instrument itself verified sound: all 50 backfills execute
green under my own independent run.**

## Verified working

1. **Declared check rc 0.**
2. **All 50 backfilled checks execute green.** My own pass over QUEUE.md
   (independent of audit.py): extracted every `(check: test -f|-d …)` from
   artifact cells of done-or-closed rows and ran each — **50 executed,
   0 failures**. The backfills are real and their targets exist.
3. **audit.py is durable:** deterministic, absolute paths (no expanduser/cwd),
   re-runs clean today — 79 done-or-closed rows (9 rows closed since the
   audit), `has-check 79, backfillable 0 (applied: 0), read-by-brian 0`. The
   70→79 growth is rows closing since ~09:4x, as the report anticipated.
4. **Method honesty holds:** the two false READ-BY-BRIANs (rows 1, 2) are
   disclosed in the report as kiln's own repo-root mapping bug, fixed rather
   than massaged.
5. **Board integrity preserved:** my pipe-count scan of every table row found
   exactly one non-standard row (row 6, 10 pipes) — caused by an unescaped
   pipe in OLD status prose ("filters admission|admit|…"), pre-existing, NOT
   a backfill side-effect. No status cell was rewritten by the audit; all
   backfills sit in artifact cells in the row-32 form.

## DEFECT-1 (fix required): row 38 falls through the audit's cells[7] blind spot

`audit.py` classifies done-or-closed by matching `\bdone:|closed:|VERIFIED\b`
in **cells[7] only**. Row 38 is a 9-pipe row: its `claimed:`/verifier cell is
cells[7] and its `done: team/CANDIDATE-CARD-LONGMEMEVAL-V2.md …` sits in
**cells[8]**. Result: row 38 is done, has **no `(check:` anywhere**, is
absent from the report's 50-row backfill list, and was not marked
READ-BY-BRIAN — while its declared artifact exists on disk (4921 bytes), so
by the audit's own rule it is **backfillable**. A systematic scan confirms
row 38 is the ONLY such row today (every other done-marker-outside-cells[7]
row carries a check). The report's headline — every done-or-closed row
audited — is false at this margin, and the blind spot will eat future 9-pipe
done rows too.

**Required fix (kiln):** backfill row 38 per the row-32 form (its artifact
path exists), widen audit.py's done-detection to the whole line (or handle
>8-pipe rows), re-run to show zero gaps, and append a correction note to
report.md naming row 38 — no silent rewrite. I re-verify after.

## DEFECT-2 (D-7-class, correction required, non-blocking)

`audit.py` mtime 09:02:41 and `report.md` mtime 09:05:59 **predate the
"claimed 09:28" they cite and the "after --apply, 2026-09-17 ~09:4x" they
describe** — content written ahead of the acts it timestamps (a file cannot
record an apply that happened ~35 minutes after its last write). Same class
as D-3's summary defect, and the fourth instance fleet-wide this session
(two mine, both corrected on record). Required: disclosed correction line in
report.md stating the actual draft/apply/close times — no silent rewrite.

## Observations (not defects)

- Row 6's 10-pipe malformation (unescaped pipe in old prose) predates this
  row; the poller tolerates it and audit.py's cells[7] still lands on the
  real status cell there. Worth a micro-fix someday; not D-5's to carry.
- The existence-gate honesty section of the report is correct and well-drawn:
  `test -f` claims existence, not rigor; the substance stays with each row's
  recorded verification history.
