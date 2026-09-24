# P12-cutover-postreview-1 (independent, read-only)

Owner: corvid. Package `P12-cutover-1` → first production package
`P12-production-handoff-1`. Read-only; no code/edit/install/resend.

## Actual switch (verified against signed pins)

PASS capture/switch/handoff all PASS (`cutover-p12cutover1/results.tsv`, `cutover-signature-1`).
PASS installed binary = `97a57db1…` (signed `product_sha256`).
PASS config = `84e1c9cf…`; 4 units byte-equal to the release
(`agent-loop@.service 7f70ee57…`, `liveness@.service 71c42358…`,
`liveness@.timer 502745ac…`, `liveness-failed@.service 8ce59448…`).
PASS new owner: `agent-loop@campaign4.service` enabled+active,
`agent-loop-liveness@campaign4.timer` enabled+active on the :00/:30 calendar.
PASS `OnFailure=agent-loop-liveness-failed@campaign4.service`; handler unit file
exists.
PASS old owners off: `openwork.timer`/`coax-dry.timer`/`shadow-watch.timer`
disabled+inactive; callbacks drained (switch result); one owner.

## First production package (closed)

PASS worker `ex-…-w1` and verifier `ex-…-v1` claims filed; verifier artifact
`operator-handoff-verification.md` `87bbc0e0…`.
PASS authoritative ledger: `P12-production-handoff-1` step `closed`, phase
`COMPLETE`, verdict `PASS`.
PASS no duplicate dispatch/effect: exactly two outbox records (w1, v1), each with
one `outbox-sent` receipt; both seats responded; no resend.

## Outbox reconciliation (2 pending entries, no mutation)

- The two `outbox-pending:*` entries are the **worker and verifier dispatch
  records** (`ob-d80cf5417bb7b467` w1, `ob-566494c115c0daef` v1). Each has an
  `outbox-sent` receipt (`msg-…-w1-1`, `msg-…-v1-2`) and the corresponding seat
  **answered** (both claims exist), and the package is **closed/COMPLETE/PASS**.
- Therefore `status.outbox_pending = 2` is **stale display/bookkeeping**, not a real
  pending effect: the dispatches were delivered and completed, but the outbox
  entries were not marked settled (the package closed via the decision path before
  the outbox drain ran for them). **Operational implication:** `outbox_pending` may
  overstate outstanding work after a closure; it does not indicate an undelivered
  effect and **no resend is warranted**. No mutation performed.

## Rollback posture

PASS rollback timer retired (no active rollback/`p12cutover*` timer or unit).
PASS captured rollback materials usable: `cutover-p12cutover1/pre/` holds
`state.tsv` (old owners enabled+active, campaign4-watch transient active),
`registry.json`, `timers.txt`, `units.txt`, `units-prev*`, `wake-send.txt` — enough
for exact captured-state restore.

## Known limits / handoff

PASS operator handoff and manifest match the host (independent 17/17 verification,
`operator-handoff-verification.md` `87bbc0e0…`); the five live-acceptance limits
(a)–(e) are recorded.

## Verdict

**PASS** — the qualified cutover is installed and single-owner, the first production
package is accepted/closed from the authoritative ledger, the two outbox entries are
stale bookkeeping (no resend), and the rollback timer is retired with usable
captured materials. No concrete defect; no automatic repair or rollback.
