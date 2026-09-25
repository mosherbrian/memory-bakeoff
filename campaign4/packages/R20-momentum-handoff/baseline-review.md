# R20 baseline review — corvid-eval, read-only

- **Verdict: INCOMPLETE** — structure and coverage disclosure are honest, but one
  verified future-window leak corrupts the headline dropped-handoff count, and the
  filed evidence cannot reproduce the rest/registry/status-dependent metrics.
- **Reviewer:** corvid-eval; qid R20-baseline-review-1; receipt 19:29:00Z, deadline
  19:39:00Z. Only this file written; no production change, no network/services/Signal.
- **Intake:** `baseline-claim.json` sha `2a57aae4e1c7…` matches receipt; **all 10
  `files_sha256` recomputed equal**; contract pin `f6934033…` unchanged.

## Verified defects (bounded, reproducible)

1. **Future-window leakage inflates dropped handoffs.** At window end `19:00:00Z`,
   `R19-PY2-T` (start `18:56:32Z`) had a 5-minute budget, i.e. deadline `19:01:32Z`,
   and had **not** timed out; its in-window event sequence is only admit/authorize/start.
   `measure.py` classifies drops from `agent-loop status` captured at ~19:27Z, so the
   post-window `step="timed-out"` marks PY2-T dropped, and `REPORT.md`/claim headline
   report **"2 dropped … 0.9 per 10"**. Correct in-window unique drop is `R19-PY2-C`
   (interrupt `18:51:40Z`) only → **1/22 = 0.45/10**; PY2-T must be right-censored at E.
   This is exactly the leakage the receipt flags (`PY2-T deadline 19:01:32 outside 19Z`).
2. **Metrics are not reproducible from the filed artifacts.** Persistent outputs capture
   only `events-window.json` and `escalations-window.json`; the script re-reads mutable
   `REST.jsonl`, live `git` registry history, and live `agent-loop status` at run time.
   No REST/registry/status snapshot or their hashes are filed, so (a)/(c)/(d) cannot be
   recomputed by a reviewer and drift as the sources change. `baseline-receipt.json`
   required a "source manifest and redacted local snapshots"; it is absent.
3. **(d) does not match its preregistered definition.** Package formula (d) is *confirmed
   transport delivery*, separated into attempted/queued/unconfirmed and channels. The
   script counts every indexed ledger row in-window and explicitly notes "channel delivery
   is not recorded"; the `kind=research-gap` absence is then used for a zero claim. That
   zero is not established from a source with known coverage, and ledger rows are notices,
   not confirmed deliveries.
4. **REST rest is an unfaithful approximation.** 50 in-window A/B rows were consumed by
   union with no latest-row/supersession or receipt-validity semantics (stream A intervals
   verifiably overlap; e.g. many rows nest inside `08:26Z→15:00Z` and duplicate R18 rows at
   `18:38:24Z`/`18:38:49Z`). The report must not imply this equals what the live R11/R18
   checker called valid rest; as written it is a superset credit that can only understate
   stall.

## Confirmed sound / disclosed

- Window is exactly 24h; coverage honestly reports the 378-minute loop-record gap and the
  `01:17:36Z` first event; registry changes at `15:42:11Z` (A) and `16:28:53Z` (A+B) are
  captured. Test pages are excluded; ticket files T-103/T-104 exist in-window.
- The 583/1349-minute stream-A figures are labelled **upper bounds** because out-of-loop
  work is uncounted and pre-registry A activity is assumed. **On the instruction: these do
  not evidence actual stall and must not be reported to Brian as such.** The cleaner
  "after first loop event" 206 min is still not verified inactivity (out-of-loop work and
  the idle-evening assumption remain), so even it is not an observed stall measure.

## Required minimal corrections before implementation release

1. Classify in-window drops/censoring from window-bounded evidence only: PY2-T pending at
   E; restate headline as 1/22 (0.45/10).
2. File redacted, hash-pinned snapshots (or commit SHA + byte hashes) for REST, registry
   git revision, status, and escalations, sufficient to recompute metrics.json offline.
3. Recast (d) as ledger notices with explicit unconfirmed-delivery status, or obtain
   confirmed-delivery coverage; drop the unsupported "no stall escalations" zero.
4. Relabel the R11/R18 rest columns as approximations lacking latest-row/validity
   semantics, or implement those semantics.

*Reviewed read-only: baseline-claim.json, baseline-receipt.json, baseline-review-receipt.json,
admission-disposition.json, package.md, baseline/REPORT.md, baseline/measure.py,
baseline/out/*, baseline/out-sens/*, REST.jsonl, agent-loop campaign4.db (read-only),
escalations.jsonl, support-tickets/*, RESEARCH-STREAMS.json history.*
