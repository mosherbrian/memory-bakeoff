# Proposed boundary interface — Tern

This is design input for independent admission, not a claim of implementation.

## Vocabulary and decisions

Four disposition kinds: `successor_opened`, `question_answered`, `budget_spent`,
`blocked`. No free-text kind and no “idle means done” inference. Reasons and
evidence may be prose; the status and required relationships may not.

Tern decides each terminal boundary. Cairn records the attributed decision and
publishes controller state. Worker completion and verifier PASS are evidence,
not authority to invent a director disposition. The future software controller
performs the same mechanical recording and validation.

A result can be published before a closure decision. Until the decision is
recorded, the package stays at its eligible nonterminal stage with a bounded
director-decision task in flight (default 10 minutes, owned by Tern). This is
not legitimate rest. Persist terminal status and boundary disposition together
in one ledger transaction. If historical or corrupt state contains a terminal
without disposition, flag INVALID immediately; do not infer an intention.

## Interface owned by the specification

Retain `campaign4/state.json` as the read interface, but **replace the provisional
unversioned string-map shape** with a versioned structured projection:

```json
{
  "schema_version": 1,
  "ledger_revision": 42,
  "generated_at": "2026-09-21T16:30:00Z",
  "in_flight": [
    {"package_id": "P2-r2.1", "phase": "ADMISSION",
     "action_id": "P2-r2.1-admission-1", "owner": "corvid",
     "deadline": "2026-09-21T16:45:00Z", "dispatch_receipt": "receipt-id"}
  ],
  "terminal": {
    "P2-r1": {
      "state": "EXHAUSTED",
      "disposition": {"kind": "successor_opened", "successor_id": "P2-r2.1"},
      "decided_by": "tern", "decision_ref": "decision-id",
      "reason": "Explicitly allocated successor closes evidenced gaps"
    }
  }
}
```

The package asks kiln to finish exact field requirements and validation, not
to copy this illustrative record as real campaign history. Canonical authority
is the controller event ledger (initially durable campaign records); this file
is one atomic derived snapshot. Cairn is its sole writer until the controller
takes over. Write temporary file, flush, atomic rename; the ledger transaction
precedes publication. Compare ledger revision and expected package inventory
before treating the projection as complete. On interruption, rebuild from the
ledger; an old snapshot cannot authorize new dispatch or silently hide closure.

`in_flight` means an actual acknowledged bounded action (including admission,
execution, verification or director decision), not merely a package file, an
unrelated busy seat, or a message whose delivery was never acknowledged.
Overdue action deadlines remain faults even if state/files are fresh.

`successor_opened` requires a specific linked successor. At declaration, that
successor must have acknowledged bounded work. Later, follow the link through
terminal successors to either real in-flight work or a legitimate rest leaf.
Validate all referenced links, reject cycles/dangling links. This prevents a
historical succession record from becoming a permanent false alarm after the
last successor legitimately finishes.

Rest leaves:

- `question_answered`: evidence plus Tern's reason no successor is warranted.
- `budget_spent`: allocation reference and Tern's decision not to extend it;
  merely consuming one package budget does not assert campaign budget expiry.
- `blocked`: blocker id, reason, owner, and a machine-readable wake trigger
  (event id and/or revisit timestamp). No generic silence alarm while correctly
  parked. When its trigger becomes due, reconcile/wake its owner once and
  create bounded in-flight decision work; indefinite unowned waiting is invalid.

Blocked disposition at a terminal boundary describes why the question is
parked; it does not mutate a terminal package back into lifecycle BLOCKED.
An active package in lifecycle BLOCKED is separately accounted for with its
phase, remaining allocations and trigger. The specification must define both
without conflating their permissions.

## Validator and backstop

Validate immediately after a terminal decision or successor handoff, on
startup/recovery, and at backstop invocation. A 45-minute rate check alone
cannot enforce a state invariant. Invalid boundary state wakes Tern with the
specific discrepancy and a bounded resolution expectation; it must not launch
a successor itself. Repeat unresolved alarms use the existing owned escalation
path, not unlimited model calls.

Only a fully valid declaration with no outstanding/overdue action and all
chains ending in legitimate rest may suppress the generic silence ladder.
Absent, unreadable, unsupported-version, malformed or ledger-incomplete state
cannot suppress it; report the state problem as well. Faults are checked before
fresh activity. Timer/process health and declared deadlines remain independent.

The existing watcher must change to this interface after specification freeze.
Until then do not publish a speculative state.json or claim correct parking is
implemented. Its current string matching and activity fallback are not the
specification. Any future watcher change must exercise dry-run fault branches
with no live pause, stop or Signal side effects.
