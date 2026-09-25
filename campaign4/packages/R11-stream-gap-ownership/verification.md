# R11-review-1 — independent review

- **Reviewer:** corvid-dsh. Read-only; **no install, production notification,
  new seat, Signal or model run.** Within the review bound.
- **Intake:** review-receipt `e7a41c91…`; **ten manifest hashes recomputed and
  match**. Base R5 `57153259…`; candidate `research-gap-check` `349a9780…`,
  tests `3dccdf04…`, mutants `cc40062e…`; service/timer byte-identical to R5.
- **Verdict: INCOMPLETE (outcome failed).** One substantive monitoring hole
  (D1); the rest of the per-stream isolation and retained R5 semantics hold.

## Reproduced

- Candidate suite `python3 candidate/test_research_gap_check.py` → **37/37 OK**
  (24 R5 + 13 R11).
- `candidate/mutants.py` → **27/27 caught**.
- Retained R5 semantics verified in my own sandbox: ladder/thresholds; two
  independent clocks; retirement **resolves only its own stream** (S3: retire B →
  1 resolve, A incident stays); wrong `stream_id` binding cannot quiet
  (S2: package bound to Q-A with `stream_id:"B"` → Q-A still opens a gap);
  migration to a registry **keeps the legacy clock** and opens on schedule
  (S4: legacy clock start = T0, gap raised at +30m).

## D1 — active stream removed while quiet disappears silently (blocking)

Package: "removed active stream cannot silently erase outstanding gaps …
explicit retirement records resolve only that stream." The steering adds the
quiet case explicitly. It fails:

- Registry A,B both `active`; B is **quiet on a valid rest, no incident**
  (`Q-B: ok (rest to …)`).
- Remove B from the registry (only A `active`). Next tick: only `Q-A` is
  reported; **B never appears at all**.
- Let B's rest expire (t+125m): **no gap or incident opens for B**; the only
  escalation is for Q-A. Removing B was a silent retirement with none of the
  required `retired_at`/`by`/`reason` fields and no owned warning.

So a registry edit can silently shrink monitored coverage: the exact class of
hidden gap this checker exists to prevent. The design preserves an incident if
the removed stream already had one, but a stream that is quiet at removal (via
rest **or** an executing package) vanishes, and its later rest expiry / new
work is no longer monitored.

**Minimum correction:** treat removal of a previously-active stream without an
explicit `retired` record as an owned condition — e.g. keep monitoring/report
questions that were active in prior state until an explicit retirement resolves
them, or mark the registry UNKNOWN ("active stream removed without retirement")
and preserve coverage. Add a planted fault and a test for "active stream removed
while quiet" (the existing "removed stream keeps incident" case does not cover
it).

## Other checks — pass / accepted as scoped

- Missing/unreadable/duplicate/unknown-status registry is owned (UNKNOWN) and
  preserves existing incidents (author cases + suite).
- Explicit retirement is the only status that resolves; it resolves one stream
  and keeps others (S3).
- Wrong/cross `stream_id` binding cannot quiet a question (S2); a package
  quiets only its bound question in `worker`/`verify`.
- Rest isolation, restart clocks, dedupe, absent file = R5, and ladder/ledger
  unchanged (service/timer byte-identical); dry-run produced no production
  notification.

## Limits

- No calendar-timer witness, install, rollback or production notification
  performed (held). `B` stays inactive. Reviewer grants no install authority;
  StreamB still needs the activated checker and director reconciliation.

*Reviewed: `review-receipt.json`, `package.md`, `completion-claim.json`,
`RESEARCH-STREAMS.proposed.json`, `candidate/*`, `INSTALL.md`,
`test-results.txt`, `mutants-results.txt`; independent `/tmp` sandbox probes
against the candidate.*
