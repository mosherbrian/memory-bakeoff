# Tern ruling: retirement is part of P6 cutover, not P5 acceptance

No live script retires automatically when P5 lands. P5 is trusted clock ingress
with fake external effects; it does not implement reliable ACP completion
capture/delivery, actual systemd timers, real stop, or Signal notification.
A lifecycle terminal transition is not the campaign-wide pause protocol.

Put the replacement/retirement matrix and executable rollback plan in a
separately admitted P6 integration/cutover contract after P5 acceptance. Do not
amend in-flight P5. This ruling defines required scope; it grants no live writes,
retirement, migration, worker effort or test Signal today. Tern owns allocating
and opening P6 at the eligible boundary without another sponsor prompt.

| Existing mechanism | Disposition after P5 | P6 target / retirement condition |
|---|---|---|
| campaign4-watch | Retain interim backstop | Retire mtime/string-map work-state policy and its scheduling only after live ledger/ACP supervision and independent controller-health backstop are proven and cut over |
| Hand-armed systemd-run deadlines | Retain until adapter proven | Retire seat-authored timer policy/commands; software owns one-shot timer creation, identity, reconciliation and cancellation. systemd remains infrastructure |
| Hand-typed control rows / receipts | Retain host-generated compact path | Retire as authoritative writer when trusted ingress is active; TSV/status becomes derived read-only output, historical files retained |
| campaign4-pause | Retain hard-stop actuator | Existing script continues as named external adapter; pure lifecycle terminal state does not stop seats or deliver Signal. Replacement is out of P6 unless separately justified and admitted |
| wake | Retain transport | In P6 adapter scope for delivery/receipt/failure/restart tests; replacement/reimplementation out of scope. Queued/started is delivery acknowledgement, never completion |
| acp-go-controller / acp-go | Retain launch/model wrappers | No replacement supplied by P3/P4/P5; model pins and runtime launching remain necessary |

Interpret the blank item 2 in Brian's question as wake, based on its explicit
no-live-adapter context. It is neither silently retired nor permanently beyond
integration: reuse it behind a narrow host-side adapter with durable action
identity and bounded errors. Do not modify its global behavior for other seats.

## P6 acceptance and retirement evidence

- Inventory exact scripts, hashes, timer/service units, entrypoints and callers;
  map every external effect to one owner. No claim that line count/test count
  establishes replacement. Pin accepted core and deployment/clock amendments.
- Demonstrate a harmless authorized fixture with live worker→verifier→director
  handoffs and source-side durable completion/failure capture. Reconcile a
  deliberately lost completion wake from trusted session/event evidence and
  hashes; do not wait for the worker deadline. Set a concrete healthy-host
  detection/owned-receipt target (proposed <=10s) and measure actual latency.
  Reproduce today's three missed-handoff shapes and explicit dead-turn failure.
  Do not claim simulation tests already prove these live delivery properties.
- Inject process restart, crash between dispatch/delivery/ack, queued wake,
  duplicate/reordered/stale events, early/removed deadlines, lost timer and host
  restart. Prove no blind redispatch, no duplicate acknowledged effects, current
  deadline enforcement, and owned bounded ambiguity. Check stopped/failed jobs
  as well as happy paths. A busy unrelated seat cannot hide an integrity fault.
- Prove legitimate REST remains quiet and missing/invalid state cannot. The
  independent supervisor-health backstop must detect a dead controller even if
  its event loop/ledger reader is broken; do not replace an independent backstop
  with the same process it supervises. Test backstop escalation with recorded
  fake notification targets; real all-seat stop/Signal test requires explicit
  package authorization, since it can stop the director and notify Brian.
- Use a shadow comparison with exactly one side allowed to cause live effects;
  candidate shadow cannot wake/stop/signal. At bounded cutover disable the named
  legacy work-state supervisor/timer writers before enabling candidate effects.
  Verify actual unit state and caller paths, not just a retirement document.
  No indefinite parallel active controllers. Retain only the deliberately
  independent health watchdog with clearly distinct authority.
- Freeze rollback artifacts and command plan. Rollback first disables candidate
  effects, reconciles in-flight identities/receipts and outstanding timers, then
  restores one authoritative path; never blindly resumes both. Never delete old
  evidence or require a retrospective log migration to make the cutover work.
- Corvid independently witnesses effects, failures, latency, quiet rest and
  rollback; Tern signs acceptance and retirement receipts specifying what was
  actually disabled and what remains. If a gate fails, old path remains sole
  authority and retirement is not claimed.

This is a retirement decision, not a promise that every shell script must vanish.
Keep narrow transport/launch/stop primitives where they serve the accepted
architecture; remove duplicated scheduling and state authority once replacement
has demonstrated it. Cairn still owns duty recovery; no polling model loop.
