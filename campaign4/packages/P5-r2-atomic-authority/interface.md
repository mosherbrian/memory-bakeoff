# Candidate adapter/reader interface (P5-r2 atomic authority)

Inherits the P5 clock-ingress boundary (trusted `recorded_at`, bound actor
contexts, derived/checked deadlines, epochs); the single change is atomic
authority. Schema and error/owned dispositions for the atomic surface:

## Atomic schema (explicit allowed variants)

- `atomic={"hold": <UTC instant>[, "grant_ref": <id>]}` — bounded director
  decision task; hold deadline inside the authorized window or covered by a
  phase-bound grant; attribution is store-fixed (a caller `atomic_actor`
  alongside hold is itself forged).
- `atomic={"decide": {event_id, question_id, revision, type:"decide",
  disposition}}` — requires a trusted `atomic_actor` context; the subevent
  must carry no caller `actor`/`recorded_at`/`receipt`; it is stamped with
  the shared receipt instant and checked for package/revision/type match
  plus POST-verdict terminal phase.
- Anything else — both keys in any order, unknown keys, empty object,
  non-dict atomic, malformed hold/decide values, missing trusted actor —
  is rejected (`E_MIXED_ATOMIC`, `E_BAD_ATOMIC`, `E_BAD_DEADLINE` /
  `E_DEADLINE_UNAUTHORIZED`, `E_UNTRUSTED_ACTOR`, `E_FORGED_ATTRIBUTION`)
  before either event is validated or persisted.

## Preserved behavior

- Genuine `record_terminal` and `append(atomic=decide)` closes commit
  terminal state + disposition together, survive reopen, dedup on replay.
- Genuine bounded hold commits the verdict with an owned decision task.
- Invalid/forged pairs leave both rows absent and lifecycle unchanged,
  including after reopen. Standalone decide keeps its terminal-phase gate.
- `src/fake.py`: internal test-only executor stand-in. It calls no store
  write path and performs no effects; it is not an alternate accepted
  ingress route (enforced: only `ingress.py` calls store writes).
- Reader: unchanged ledger-authoritative supervision plus
  SIMULATED-labeled status reports.
