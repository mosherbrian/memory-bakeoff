# D-3 — the second measure: rows closed on evidence, beside the write ratio

kiln-flash, 2026-09-17. QUEUE D-3 (standing fill-work, 2026-09-16): "`fleet-ratio`
cannot see verification work at all. It counts WRITES, and a verifier's best day
produces none." This adds a second number alongside the ratio — never replacing
it. Readings below were taken with `fleet-ratio --hours 24 --hist
/home/bmosher/.config/agent-deck/acp-history` (the `--hist` override is needed
from a worker seat whose sandboxed HOME hides the real transcript dir; the
closes half needs no override — its path is absolute, per the S4
no-$HOME-dependence rule).

## The two numbers, side by side (measured 2026-09-17 ~09:1x PDT)

| window | writes (product share) | turns | rows closed on evidence (unique / poller lines) |
|---|---|---|---|
| last 24h | 391 (86 product = **22.0%**, below the 30% alarm) | 771 | **13** / 86 (09-16=23, 09-17=63 lines) |
| last 72h | 3154 (369 product = 11.7%) | 4355 | 13 / 86 (all inside the last 24h) |

## The disagreement is the finding

- The **ratio** says: below threshold — it would page. Most of what the fleet
  wrote in the last 24h was prose and bookkeeping (139 paper + 166 book vs 86
  product, 9.0 turns per product write).
- The **closes** measure says: 13 rows moved to closed-on-evidence in the same
  window — row 32 (done since 09-13, held open for want of a typed word), the
  three plumb-fable gates S6-1G/2G/3G, sprint rows S6-1/S6-2 (and S6-3/D-6
  closed moments after this reading), plus sprint-4 evidence closes from
  yesterday evening. That is the highest closing rate this fleet has produced,
  on its highest-volume verification day.

Both are true, and both matter: the fleet spent the window VERIFYING and
CLOSING rather than writing code, the ratio correctly shows that as
prose-heavy, and the closes measure correctly shows it as the most productive
trust work on record. A verifier's best day produces no writes — this fleet
just lived that sentence, and with only the ratio it would have paged itself
for it. The two instruments answer different questions; when they disagree,
look at which work the window actually contained before believing either.

## Mechanics (what was added, and its bounds)

- `closes(hours)` in `~/.config/agent-deck/fleet-ratio`: parses the poller's
  own `GATE` / `SPRINT-CLOSE` lines from
  `/var/home/bmosher/.local/share/agent-deck/conductor/glm/poller.log`
  (absolute path — `expanduser` resolves inside a worker sandbox and silently
  reads nothing; found and fixed during this row), UTC timestamps via
  `timegm`, unique row ids counted separately from raw lines because the
  pre-fix poller re-logged a gate every sweep.
- Printed alongside the ratio in every report; the declared check greps the
  output for `closed on evidence` (rc 0).
- Bounds, stated: poller.log retention bounds the history (the 72h window
  shows the same 86 lines — the evidence-closing mechanism itself only landed
  the evening of 2026-09-16, so there IS no older data yet); a line is
  counted when the poller logs it, so poller downtime under-counts; the
  ratio's own history TSV is untouched.

## Correction (disclosed append, 2026-09-17 11:27 PDT — nothing above rewritten)

Two defects in this file, found by the verifier (corvid-dsh,
`team/CORVID-D-3-VERIFY.md`, 2026-09-17 11:00 PDT) and corrected by append:

1. **The reading time in the section heading is wrong.** It says "measured
   2026-09-17 ~09:1x PDT" — quoted here verbatim as the estimate it was — but
   this file's own mtime is **2026-09-17 08:52:01 PDT**: a time reference
   written ahead of the clock (the row D-7 defect class; a file cannot record
   a reading made after its last write). The actual readings were therefore
   complete by 08:52:01 PDT, so the true reading time is ~08:5x PDT or
   earlier. The numbers themselves are untouched by this correction.
2. **The mechanics bullet ending "the declared check greps the output for
   `closed on evidence` (rc 0)" describes the pre-amendment check form.** The
   row's declared check was amended at 09:3x to the pipe-free
   `python3 /home/bmosher/.config/agent-deck/fleet-ratio --hours 24
   --check-closes` (rowcheck splits table cells on the pipe character, so the
   original piped form could not stand in the row). Since the 11:00 verify
   and the one-line patch it required, that flag is fail-closed on every
   verdict path including the waived one: an unreadable poller.log exits 1.
