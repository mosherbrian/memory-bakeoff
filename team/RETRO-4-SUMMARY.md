# RETRO-4 SUMMARY — end of Sprint 4 (trust-then-instrument)

**Aggregated:** Cairn 2026-09-16 ~17:2x PDT · **Filed:** 3/3 seats
(cairn-pi, kiln-flash, corvid-dsh — the kept roster) · **Ordered by:** Brian

## Headline (Brian's)

The S4-12 zeros were a **ROUTING failure**, not a measurement failure and not
"corvid erred / kiln erred": `team/ECOSYSTEM-MAP.md` — written 2026-09-13,
three days BEFORE S4-12 — already recorded `pi_lcm_store_reader` raw 0.0 vs
`pi_lcm_store_reader_toollevel` 0.2227, and claude-mem hit@5 0.208 (default
90-day window) vs 0.958 (window off), plus claude-mem "refuses raw". S4-12
cited none of it. **Recorded knowledge was unreachable at the moment of use** —
the same failure the bake-off exists to study. S4-14 confirmed the ruling:
both zeros were configuration artifacts (claude-mem 30/30 on the vendor's
actual chroma policy; pi-lcm 7/30 on the tool-level path).

## Convergent across all three seats

1. **Certified the artifact, skipped the source of record.** Kiln: verified
   the S4-12 zeros were *honestly measured* without asking whether the
   configuration was the vendors' real path — "honest-zero verification is not
   validity." Corvid: called SWE-chat's vocabulary "overstated" from the
   paper's Table 2 without opening the card that states it outright; the
   withdrawn claim then sat unstruck in the summary for three days. Same class,
   two seats: check the primary source before certifying.
2. **The poller is the shared churn.** Kiln: three defect classes diagnosed,
   rebuilt on rowcheck gating, 11 phantoms after the rebuild — fix incomplete.
   Cairn: snapshot-stale wakes on completed rows; the dead-engine wedge
   orphaned five verdicts (one-shot hops consumed, status-word heuristic
   misfired). Both name it as the sprint's largest non-work cost.
3. **Second-seat independence caught what the author cannot see.** Alice's
   co-sign caught the A1 error; kiln's verification caught the summary residue
   — both in work Corvid authored. Corvid's keep, confirmed by the other two
   seats' closes.
4. **The computed-done gate earned its keep.** Kiln's keep; it closed row 32
   on evidence this sprint (declared check passes, status cell never said
   done — the row-42 class) and turned queue honesty from prose into a machine
   property.

## Divergent / seat-specific

- **Cairn (conductor):** filed S4-5/9/12 handoff receipts as verification —
  the conductor dispatches the work, so it is not an independent check; they
  are NOTES. "I acted right and claimed a status I did not have." Keep:
  measure before dispatching; the machine's evidence beat status-text reading
  every time.
- **Corvid:** parity probe built-but-unwired with no consumer (churn); muse
  lane calibration → ideation → leakage probe all landed (closed).
- **Kiln:** every closing row gated by its declared check, not a word — the
  doer side ran clean once the gate existed.

## Carried forward

- Brian's publish call on the corrected +80.739% table (page sent 14:4x).
- Poller payload staleness — MOSTLY FIXED this sprint, not carried as
  builder's work: the chain message pasted 120 chars of the row's previous
  cell and 120 of its current one; both halves truncated at the same length,
  so the change usually fell past the cut and they printed identically, and
  the reader answered "stale phantom" eleven consecutive times. Messages no
  longer quote the row at all: they name it, say what is wanted, and say
  explicitly that they are not quoting it, so the reader goes and looks. The
  PAYLOAD staleness is gone. RESIDUAL (open — mitigated, not eliminated):
  the headline class ("row X is now done") can still age inside a queued
  prompt; the message tells the reader to trust the row over the message.
- Resolved this sprint: the GATE/SPRINT-CLOSE log re-firing on
  evidence-closed rows (69 duplicate lines). Found by cairn reading the
  poller's own log rather than being told — recorded as a method that worked;
  fixed with a log_once helper keyed by row (logs only when that row's text
  changes; six tests, 90 assertions green, verified silent in effect).
- Restart-actor question: the poller was cleanly restarted (systemctl
  stop/start, no crash) at 16:39:59 and 16:52:31 with no actor identifiable
  from the journal — the question is who or what issues those stops, because
  an unattributed restart authority over the fleet's only driver is a control
  gap unless it is a known component.
- Standing rule (QUEUE protocol header): a row that re-measures anything must
  cite the prior measurement or state in writing that none exists.
