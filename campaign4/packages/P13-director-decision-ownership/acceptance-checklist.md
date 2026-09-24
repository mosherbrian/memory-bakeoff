# P13 — preregistered acceptance checklist (corvid, before author)

Pinned before author dispatch. Each item is a concrete check with a required
outcome. DRY/command-printing cannot establish behavioural PASS. A failed required
wait/assertion yields FAIL/INCOMPLETE, never hidden behind rc 0. Reproduce the
baseline on pinned `8ad12b86`/`97a57db1` before any fix.

## Pins / general

- [ ] Contract `package.md a72fb97c…` (`da00b2d8`); all 7 `input-pins.json` hashes;
      base source/binary; no new dependency/research/general workflow engine.
- [ ] Freeze `internal/core`, `internal/py`, `conformance/cases`; unfreeze only loop
      decision ownership + necessary CLI/status/timer/host escalation adapter,
      tests, docs.
- [ ] Retain conformance 125, adjudicated host parity, loop tests, existing mutation
      coverage; report new mutants and survivors honestly on the **shipped** binary.
- [ ] Baseline reproduced: decision silence on `97a57db1` before edits.

## Requirement 1 — decision deadline/identity

- [ ] At entry into decision, persist a **trusted deadline + incident identity**
      bound to project/package/verdict/action and principals; arm a **real absolute
      UTC calendar timer**, `AccuracySec=1s`.
- [ ] Default window **1800 s**, configurable positive bounded value; validation and
      migration documented.
- [ ] Reopen recovers **missing timers without moving the original deadline**;
      `decide` cancels future rungs; a **stale callback after close is harmless**.
- [ ] No worker rerun, verdict rewrite, or timeout masquerading as a terminal
      decision.

## Requirement 2 — ladder and stopped-run recovery

- [ ] At deadline remind director; **+300 s** still unresolved notify duty; **+600 s**
      still unresolved notify Claude via the escalation ledger **plus** `notify-claude`.
- [ ] Stage boundaries **persisted before delivery**; checks also recover lost
      callbacks.
- [ ] Works while `run` is **intentionally stopped** via the independent timer and
      outside check; stop stays quiet absent outstanding obligations.
- [ ] Transport failure is **owned**, never counted as acknowledged/delivered; bound
      and principal checks kept.

## Requirement 3 — ack / expiry / resolution (stable key)

- [ ] Claude response is explicit, incident-bound and durable: ack names **owner,
      next action, response deadline ≤15 min**, or relays an authorized decision.
- [ ] **Ack is not decision/closure.**
- [ ] Expiry while unresolved **re-raises the SAME stable escalation key** through
      the existing recurrence path; **no indefinite ack renewal** that suppresses
      Brian.
- [ ] A **timely actual decision resolves** the incident and prevents a later page;
      **forged/stale/wrong-principal** response refused.
- [ ] One unshared negative per new authority/boundary (e.g. ack-without-decision,
      wrong-principal, expired ack, resolution-after-expiry).

## Requirement 4 — escalation-watch reuse / durable registration

- [ ] `escalation-watch` reused unchanged (shared global config untouched): default
      **grace 45 min + 15 min interval + timer/transport latency**, measured
      separately; **no 10 min Signal delivery claim**.
- [ ] Stable mapping to escalation ledger **IDs/keys**; `notify-claude` rc 0 is **not**
      an ack and its ledger write is best-effort → **durable registration verified**.
- [ ] Unavailable Claude/ledger/pager behaviour documented and owned; **no credentials
      in evidence**; external host/user-manager availability limits retained.

## Requirement 5 — logical stage / status

- [ ] **One logical stage per incident** across callback/check/restart/concurrent
      decision; intents/receipts persisted.
- [ ] Failed send retried **bounded**; ambiguous delivery explicit; **at most one
      labelled repeat** per ambiguous stage then owned unresolved; no duplicate
      decisions/cancels/dispatches; D3 incident identities retained.
- [ ] Status exposes **deadline, rung, owner, ack/response deadline, unresolved
      delivery, evidence links**.

## Checks / live boundary

- [ ] New tests + **unshared mutations** for: deadline/restart, early/stale
      callbacks, concurrent close/rung, forged/rebound principals, missing/failing
      transport, ack-not-decision/expiry/recurrence, resolution before page,
      stopped-run recovery, crash before/after send, exactly one logical stage.
- [ ] **Real separate-process calendar witness** including `daemon-reload` and
      restart, on **isolated unit names/ledger/adapter sinks**, full ladder with
      shortened explicit fixture-only intervals.
- [ ] **Actual escalation scripts** against isolated `HOME`/state + **stub
      ticket/notify sinks**; **never page Brian** for a synthetic fault.
- [ ] Live 20 min: fresh isolated fixture principals, real decision timer + actual
      notification to the designated fixture director/duty and a labelled Claude
      **test** notification; Signal captured by a test sink; one overdue decision,
      bounded ack, resolve/quiet, restart no duplicate; corvid reviews exact raw
      evidence. Tern signs exact binary/plans/identities/absolute bounds before live
      effects.
- [ ] **No real Signal test or production install** until separately explicit
      authority.
- [ ] Held promotion 10 min: installs exact reviewed binary with snapshot, rollback
      to `97a57db1`, reconciles existing decision packages; does **not** reset an
      existing decision deadline or resend work; Tern signs promotion separately.
- [ ] Release/routing general registration is a **deferred scope limit** — do not
      fake a worker package for a director approval; explicit director-owned release
      receipts and independent deadline notifications during this round.
