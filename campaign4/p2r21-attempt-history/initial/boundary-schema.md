# Terminal boundary schema — controller state interface (r2.1)

This is a state interface for the controller, not bespoke gate-writing. One
authoritative location: the controller event ledger. The JSON below is a
versioned derived projection (`state.json` shape replaces the provisional
unversioned string-map). Field requirements are exact; validation is
mechanical except where marked judgment.

## Structure

```json
{
  "schema_version": 1,
  "ledger_revision": 42,
  "generated_at": "2026-09-21T16:30:00Z",
  "in_flight": [
    {
      "package_id": "string, required",
      "phase": "enum ADMISSION|REGISTERED|RUNNING|CHECKING|REPAIR_ALLOWED|BLOCKED|DIRECTOR_DECISION, required",
      "action_id": "string, idempotency key, required",
      "owner": "enum tern|corvid|kiln|cairn, required",
      "deadline": "RFC3339 UTC, required",
      "dispatch_receipt": "string, acknowledged-delivery id, required"
    }
  ],
  "terminal": {
    "<package_id>": {
      "state": "enum COMPLETE|EXHAUSTED|TERMINATED|SUPERSEDED, required",
      "disposition": {
        "kind": "enum successor_opened|question_answered|budget_spent|blocked, required, no other value",
        "successor_id": "required iff kind=successor_opened, must resolve to a known package",
        "reason": "string, required for all kinds",
        "evidence_refs": ["artifact hashes / decision refs, required for question_answered and budget_spent"],
        "allocation_ref": "required iff kind=budget_spent",
        "blocker": {"id": "string", "owner": "enum", "wake_trigger": {"event_id": "string?", "revisit_at": "RFC3339?"},
                    "resumption": "string, what reopens work"},
        "note": "forbidden iff kind=blocked describes lifecycle BLOCKED: a blocked disposition parks the question, never mutates a terminal revision"
      },
      "decided_by": "const tern, required",
      "decision_ref": "string, required",
      "reason": "string, director prose, required"
    }
  }
}
```

`wake_trigger` requires at least one of `event_id`, `revisit_at`.
`decided_by` is always `tern`; any other value is malformed.

## Validation rules (in order)

1. Parseable JSON, `schema_version` == 1 (supported), `generated_at` valid.
   Else INVALID `malformed-state`.
2. `ledger_revision` >= last seen; projection covers the full known package
   inventory — an empty `terminal` map alongside known terminal packages is
   INVALID `ledger-incomplete`. An empty declaration never hides known
   terminals.
3. Every `terminal` entry carries all required fields for its kind
   (field matrix above). Missing disposition, free-text `kind`, or absent
   `successor_id`/`allocation_ref`/`blocker` where required → INVALID
   `missing-disposition` (a state fault even with fresh file activity).
4. Every `successor_opened.successor_id` resolves: the successor shows
   acknowledged bounded in-flight work, or chains through terminal successors
   to in-flight work or a rest leaf. Missing/never-dispatched/broken
   reference → INVALID `dangling-successor`. Cycles → INVALID
   `successor-cycle`. An unrelated busy seat/package (no acknowledged action
   for the linked id) does not satisfy the link.
5. Every `in_flight` deadline > now; any overdue action → fault
   `overdue-action` even if files are fresh. `dispatch_receipt` must be an
   actual acknowledged delivery, not a written intention.
6. Only a fully valid declaration with no outstanding/overdue action and all
   chains ending in legitimate rest suppresses the generic silence ladder.
   Before a valid `blocked` trigger/revisit deadline, rest must not enter
   that ladder. Stale file activity satisfies nothing.
7. Terminal state without disposition in underlying/legacy state → flag
   INVALID immediately; never infer intention.

## Examples

**Valid — successor chain at rest through two completed successors:**
`terminal: {P2-r1: {state: EXHAUSTED, disposition: {kind: successor_opened,
successor_id: P2-r2}, ...}, P2-r2: {state: SUPERSEDED, disposition: {kind:
successor_opened, successor_id: P2-r2.1}, ...}}`, `in_flight: [P2-r2.1
CHECKING …]` → VALID `successor-chain-live`. When r2.1 later closes
`question_answered` with evidence, the chain ends at a rest leaf → VALID
`rest`, no permanent alarm.

**Valid — each rest kind:** `question_answered` with evidence_refs + reason
no successor warranted → VALID rest. `budget_spent` with allocation_ref +
decision not to extend → VALID rest (no claim on campaign budget).
`blocked` with blocker id/owner/wake_trigger + resumption → VALID parked
rest; silence ladder suppressed until the trigger.

**Invalid — missing disposition (the actual r1 omission shape):**
`terminal: {P2-r1: {state: EXHAUSTED}}` (no disposition key) with fresh file
activity elsewhere → INVALID `missing-disposition`, wake Tern. Fresh activity
does not satisfy rule 3.

**Invalid — claimed-but-absent successor:** `successor_opened` naming a
never-dispatched id → INVALID `dangling-successor`.

**Invalid — unrelated in-flight work:** `successor_opened: P2-r2` while the
only live seat works an unrelated package with no acknowledged r2 action →
INVALID `dangling-successor` (rule 4).

**Invalid — malformed/absent:** unparseable bytes, `schema_version: 99`,
absent file, or `terminal: {}` with known terminals → INVALID
(`malformed-state` / `unsupported-version` / `absent-state` /
`ledger-incomplete`); report the state problem as well.

**Invalid — stale activity + expired deadline:** fresh mtimes but an
`in_flight` deadline 20 min past → fault `overdue-action`; activity
satisfies nothing (rules 5–6).

**Invalid — cycle:** A → `successor_opened` B, B → `successor_opened` A →
INVALID `successor-cycle`.

**Invalid — interrupted atomic publication:** `state.json` half-written
(parse fails) or `ledger_revision` behind the ledger with a committed
terminal missing → INVALID `malformed-state` / `ledger-incomplete`;
rebuild from the ledger; the old snapshot authorizes nothing.
