# SPRINT-4 ADVISORY — Aletheia (Alice), verifier seat (`worker-glm-dsh`)

**Scope:** one turn, advisory only, no new work. Derived solely from my own
turns today (two sign-offs + findings; all $0). Signing rule: artifact pointer or
"memory only".

## Top 5, ranked

1. **Fix routing precision before adding rows.** Every seat's RETRO-3 names a
   false-wake class still firing: kiln's §7(c) harness-state fingerprint (9 of
   last 13 wakes contentless, `BOARD.md` 2026-09-16 08:2x), title-substring
   mismatches (`verity-flash ← Verity`), stale-claim timers on closed rows.
   Adding Sprint-4 rows on top of this spends the 40-wake/day budget on noise.
2. **Close "green-but-unwired" as a class.** S3-3's 10 green adapter tests hid
   that the adapters are **not wired into `mine.py`** (no `--source`); green ≠
   integrated. Either add a wiring+smoke row or mark such rows explicitly
   "unit-verified, unintegrated" at close. (`ALICE-S3-3-VERIFICATION.md`)
3. **Enforce one-writer-per-row.** The S3-1 collision produced two receipts
   before anything flagged it (RETRO-3). A claim-lock (or a checkpoint that
   rejects a second `claimed:` transition) is cheap and would have caught it.
4. **One artifact, one name, in dispatches.** "section-9" cost me a
   three-target sweep (§9 vs §10 vs QUEUE S3-9). Unify on the QUEUE-row ID or
   the poller §-number; never both loosely. (RETRO-3 §5)
5. **Verifier economics: hash-pin every sign-off.** My §9 sign-off went stale
   three times today as the poller moved 16:21→17:46→17:54→18:50. A revision
   hash on the receipt lets a verifier skip a no-op re-read; I re-derived each
   time because the old hash didn't match. (RD-THREADS, `04048f05…`)

## Two code follow-ups already found, ready when builder unparks ($0, no new work)
- §8 conductor exemption **log repeats every sweep** vs its "logs once" comment —
  one-line guard `[ "$FIRED" != "1" ] && log "..."`. (non-blocking)
- §10 file-leg is verifier-name-scoped, so one verifier's fresh receipt stops
  their **other** rows' clocks; status words stay per-row. Fold or document.

## Cost/shape note for Brian's next-steps decision
Verification was the cheapest ROI today: $0, and it caught three real defects
(double-dollar, the 60 s live spend read, the exemption log repeat). Keep one
verifier + the kept reviewer (Corvid); keep the "no wake without finishable
work" rule. Do **not** buy more pulses — buy routing precision.

— Aletheia (Alice), `worker-glm-dsh`. Advisory only; $0.

## Recommended Sprint-4 shape (advisory, one turn — not a return to work)

**Do not run a build sprint. Run a one-goal consolidation sprint, then stop.**
Justification: Sprint 3 already produced the results (S3-1, S3-2, S3-3, S3-6, S3-8). The
binding constraints are not "not enough measured" — they are (a) the headline window result
isn't yet clean enough to quote, and (b) most verified output is unintegrated. More rows add
to the unintegrated pile.

**The one goal:** *Campaign-1 is externally quotable, or explicitly re-run under a correct
window.* Deliverable: a corrected `WINDOW-REPORT` + a bounds rule that records the window pin
in the same place the run reads it, so the label can't diverge from the pin again.
Fuel: S3-8's F1 — the run pinned `2026-09-16T00:00:00Z` (=17:00 PDT) while §1 said "midnight
local" (=07:00Z); the window closed ~7 h early and ~7 h of local Sep-15 turns are excluded.
That is a one-line-class defect that invalidates any external quote today.

**Ordered moves (only after the goal):**
1. **Integrate or explicitly retire every verified-but-unapplied artifact.** S3-3 adapters →
   wire into `mine.py operator_texts()` + one real-data smoke; poller follow-ups (exemption
   log guard, §10 file-leg scoping, §7(c) non-harness fingerprint) → apply, verify, commit.
   Rule: **no new row while a verified row is unintegrated.**
2. **Routing precision before volume.** Kill the false-wake classes (kiln measured 9 of 13
   wakes contentless); adopt one-artifact/one-name dispatch IDs. Target ≤10% contentless wakes
   under the 40-wake/day budget.
3. **One verifier-of-record per row, hash-pinned.** The S3-8 double-verify I just caused
   (Assay landed first) is the evidence that "duplicate concurrent verification" is a live
   RETRO-3 blind spot, not a hypothetical.
4. **Decide the memory-result's fate — Brian's call, before any more measurement:** publish the
   arm-unfavorable result as-is (+77.4% median tokens, +147.6% wall), test a leaner recall path
   (the `recall/remember/confirm` round-trips are the suspected cost), or gate campaign-2 under
   a correct window. Measuring more before this decision just deepens the pile.

**Keep:** 1 doer + 1 reviewer + 1 verifier; all parked seats stay parked.
**Anti-recommendation:** do not open new evaluation rows or re-widen the fleet this sprint —
that spends the fixed wake budget on noise the routing can't yet deliver.

## HARD BOUNDS (enforced, not prose) — the Sprint-4 / campaign-2 contract

F1 is the proof: a window bound written in prose ("midnight local") drifted from the bound the
run actually used (`00:00Z`), and the report is unquotable. So bounds must be *hard*:

1. **Window (single source of truth).** Bounds are absolute UTC instants declared once at
   gate-open in one machine-read file (e.g. `team/WINDOW-<id>.json`). The human label is
   *derived* from the instants — never typed. §1 of the report is generated from the file.
   The harness **fail-closes** if `--window-end` ≠ the declared instant. Closing before the
   declared end is a hard error (that is F1), not a "close-owner choice".
2. **Time.** The sprint ends at its declared UTC instant regardless of completion. No
   extension, no drift; if unfinished, it stops and reports.
3. **Scope.** ≤1 goal, ≤3 rows, 1 doer + 1 reviewer + 1 verifier. No new evaluation rows.
4. **Wakes.** ≤40 contentless wakes/day fleet-wide; ≤10% contentless per kept lane; a lane over
   the bound pauses until routing is fixed.
5. **Spend.** $0 metered for the consolidation sprint (local only). Any metered wake is a
   per-wake Brian call, not a lane default.
6. **Verification.** One verifier-of-record per row; every sign-off carries the artifact's
   revision hash; a changed revision that a sign-off's hash already covers is not re-verified.
7. **Exit.** Goal met OR any bound hit → stop and report. No auto-continue into a next sprint.
