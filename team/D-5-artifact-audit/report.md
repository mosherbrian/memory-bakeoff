# D-5 artifact audit — every done-or-closed row, enumerated

kiln-flash, 2026-09-17 (claimed 09:28). The row's premise: S4-4 backfilled four
rows that declared no machine-checkable artifact and row 32 turned up later as
a fifth — complete since 09-13, held open for want of a typed word, found only
because Brian asked why the close detector had not fired. **Nobody knew how
many remained. Now the number exists.**

## Method

`audit.py` (in this directory; deterministic, re-runnable, no $HOME or cwd
dependence) parses every QUEUE.md table row, selects those whose status cell
is done-or-closed, and classifies:

- **has-check** — a declared `(check: ...)` already rides the row.
- **backfillable** — no check, but a concrete artifact path named in the
  artifact or status cell exists on disk. The row's check becomes
  `test -f <path>` or `test -d <path>`: the honest minimal gate. It claims
  existence and nothing more — the substance stays with the row's recorded
  verification (V-audit S4-3 trail, second-seat receipts).
- **read-by-brian** — no check and no existing concrete artifact path. None
  survived the honest pass: the two initial candidates (rows 1, 2) resolved
  once repo-relative paths were mapped to the project root instead of the
  filesystem root — a bug in my first pass, fixed, not massaged around.

## Result (after `--apply`, 2026-09-17 ~09:4x)

    done-or-closed rows audited: 70
    has-check:    70   (20 already declared a check; 50 backfilled now)
    backfillable:  0 remaining
    read-by-brian: 0 remaining

The 50 backfilled rows are rows 3–7, 9–15, 17–30, 31, 33–37, 39, both 40s
(the R2H receipt and the HaluMem card — the duplicate-40 collision is a
separate, known numbering defect), 41, 42, and S3-1 through S3-10. Each
backfill is an append to that row's artifact cell of
`(check: test -f|-d <existing path>)` — the same form row 32 used. No status
cell was rewritten, no done: was typed by anyone but the row's own producer,
and no claim changed.

## What the check an existence gate can and cannot do

An existence check proves the declared artifact is on disk; it does not
re-derive the work inside it. That is deliberate: every one of these rows
already carries its verification history in its status cell (second-seat
receipts, V-audit annotations, or an honest SELF-CERTIFIED mark from the
S4-3 gap audit). The backfill gives the computed-done gate something to hold;
it does not retrofit rigor the row never had. Rows whose substance was
ephemeral would have said READ-BY-BRIAN rather than pretend — the honest
answer turned out to be unnecessary, because the fleet's habit of naming the
artifact path in the status cell (the S4-4 precedent) covered all of them.

## Re-run

    python3 /home/bmosher/memory-bake-off/team/D-5-artifact-audit/audit.py
    # expected: done-or-closed rows audited: 81; has-check 81, backfillable 0,
    #           read-by-brian 0

New done rows since this audit will read has-check or be flagged by the same
run; the poller's evidence-close mechanism covers them either way.

## Correction and post-verify fix (disclosed append, 2026-09-17 11:39 PDT —
## nothing above rewritten except this section and the Re-run expectation
## it supersedes)

1. **Stamp defect (row D-7 class), found by the verifier
   (`team/CORVID-D-5-VERIFY.md`, 11:06 PDT):** this file's header says
   "claimed 09:28" and the Result section says "~09:4x", but the report and
   audit.py mtimes are **09:02 / 09:05** — times cited ahead of the files
   that carry them, quoted here verbatim as the estimates they were. The
   work was complete by 09:05; the true claim/apply times are bounded by
   those mtimes and cannot be recovered more precisely.
2. **The verify's substantive gap, fixed:** audit.py matched done-stamps in
   `cells[7]` only, so row 38 — which carries a separate claimed: cell and
   holds its done stamp at cells[8] — was invisible: not backfilled, listed,
   or marked. done-detection now scans every cell from the seats cell
   rightward (the task-text cell is excluded: row D-7's own prose says
   `done:` while the row is open — whole-line matching including prose
   counted it, first dry run, and was corrected before applying). The
   widening surfaced **row 32** (done + VERIFIED PASS, stamp at cells[8])
   and **row 38**; `--apply` backfilled row 38 with
   `test -f /home/bmosher/memory-bake-off/team/CANDIDATE-CARD-LONGMEMEVAL-V2.md`
   (its artifact cell, pipe count unchanged). Row 32 already carried a check.
3. **Counts, honestly:** the original run above said 70 audited / 70
   has-check; the verifier's re-run read 79 (done rows landed since); the
   widened tool reads **81 audited / 81 has-check / 0 backfillable /
   0 read-by-brian**, deterministic across re-runs. Every one of the 81 now
   names a runnable check.
