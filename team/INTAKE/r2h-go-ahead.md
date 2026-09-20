# R2H day 0 — GO

**Brian: GO. Day 1 counts. Start whenever you like.**

Receipt received 2026-09-17, dated `2026-09-17T18:46:49Z`, verified by
`team/tools/check_r2h_smoke_receipt.py` (exit 0).

## What was checked, and not taken on trust

The hard gate was **re-derived** from the receipt's own fields rather than read
from its `verdict` line, because a receipt that reports its own verdict is the
same shape as a row that declares itself done:

| check | result |
|---|---|
| pi_ran | true |
| nudge_delivered | true |
| recall_registered | true |
| store_unmodified | true |

All four true, so the gate passes. The store hash is **byte-identical before and
after** — `77dac2dd2f0282f1…` both sides — so the read-only promise is proved,
not asserted. That is the failure mode the smoke exists to catch, and it did not
happen.

**No warnings at all.** `recall_invoked`, `store_named` and `prior_id_surfaced`
are all true as well. Those three are the query-match-dependent ones the runbook
says to report rather than retry; on this run there is nothing to report. That
is a cleaner day 0 than the protocol requires.

Incidental: pi took 283 s and exited 0, against a real project store
(`b210998cf496924f.db`) on the work machine.

## What day 1 needs from you

One line each morning, in the shell you launch pi from, before working:

    eval "$(python3 /path/to/r2h_deploy.py flip)"

Then work normally. Days are counted by flips, not calendar dates, so a missed
morning costs nothing — run it when you remember. `r2h_deploy.py status` shows
progress. Close on your own timing with `r2h_deploy.py close`.

## The one thing still unresolved, and it needs a decision before day 10

The close bundle's arm-stripped slice goes to a **blind** rater, and **Verity is
furloughed**. No live seat can take it if that seat has seen the arm map, so a
successor has to be named before day 10 — not on day 10. Carried on QUEUE row
D-10 so it cannot be forgotten the way the receipt was.

## Why this took asking

`R2H-RUNBOOK.md` step 6 promised a one-word go-ahead and routed questions to
GiLMore, with the rating to Verity. The 2026-09-15 furlough removed GiLMore,
Verity, Assay (who wrote `r2h_deploy.py`) and Alice (who verified it), and no
QUEUE row carried the obligation — so the promise outlived every seat holding
it. `team/INTAKE/` and row D-10 exist so the next thing Brian hands the fleet is
picked up by the board rather than by whoever happens to remember.
