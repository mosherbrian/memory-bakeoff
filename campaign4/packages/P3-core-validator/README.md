# P3-core-validator — deterministic lifecycle core (prototype)

Python 3 standard library only (`sqlite3`, `json`, `argparse`, `unittest` —
no network, no third-party packages). Implements the frozen P2 r2.1
specification (`campaign4/packages/P2-r2-boundary-amendment/` at commit
`5bfbb071e6efdb6f15de1c582295363a94cd08c7`): lifecycle transitions with
repair exhaustion and phase-preserving blocked verification, idempotent
replay-safe fake dispatch, one durable SQLite event store, atomic derived
snapshots, and the versioned terminal-boundary validator.

## Layout

- `src/lifecycle.py` — pure transition function `apply(state, event, now,
  budget)`; role permission table; deterministic `E_*` error codes. No I/O.
- `src/store.py` — `Store`: SQLite ledger (WAL), idempotent append,
  atomic `record_terminal` (verdict + disposition in one transaction),
  atomic `publish_snapshot` (temp file, fsync, rename, after commit),
  restart rebuild from ledger, persisted ack table.
- `src/fake.py` — `FakeExecutor` + `dispatch` (durable start before run,
  redelivery returns the same action, executor runs exactly once) and
  `reconcile_after_crash` (same action, never attempt+1).
- `src/validator.py` — `validate(snapshot, ledger, now, triggers_fired)` →
  `ACTIVE` / `REST` / `INVALID` / `ACTION_DUE`. Chain following, overdue
  actions, exactly-once trigger reporting (caller-held set).
- `src/cli.py` — `apply` (with `--decide FILE` / `--hold DEADLINE` for the
  D4 atomic terminal rule), `close` (verdict + disposition, one transaction),
  `snapshot`, `validate` subcommands over explicit paths. Never wakes/stops/
  signals, never creates agents, never writes campaign state.

## Run

```bash
cd campaign4/packages/P3-core-validator
python3 -m pytest tests/ -q
python3 -m src.cli apply --store /tmp/ledger.db \
  --event fixtures/events/rest-answered.jsonl   # one JSON object per use;
                                                # see tests for jsonl driving
python3 -m src.cli snapshot --store /tmp/ledger.db --out /tmp/snap.json
python3 -m src.cli validate --store /tmp/ledger.db \
  --snapshot /tmp/snap.json --now 2026-09-21T17:15:00Z
```

`apply` takes a single JSON event file. A terminal-verdict event needs a
same-transaction disposition (`--decide`) or bounded hold (`--hold`), or use
`close --verdict V --decide D`. Tests drive one-event files generated from
`fixtures/events/*.jsonl` into fresh temp stores (`close`-pairing verdict +
decide lines; the omission fixture inserts its final bare event as raw
pre-core state to reproduce the historical shape).

## Allocations (D1)

Per-question budget: attempts, repairs, `verifier_s`, and per-pass ceilings
(`passes.verify.max_s`, `passes.controller_recovery.max_s`). Verifier events
carry integer `elapsed_s`, enforced against the pass budget, which cannot
exceed the per-pass ceiling. Controller recovery is a duty-only `recover`
event from BLOCKED and is hard-capped at 600 s per pass — no budget or
cumulative ceiling overrides it (the recorded 20-minute archive-recheck
shape is rejected with `E_ALLOC_EXCEEDED`). `new_allocation` grants must be
`{"grant_s": positive int, "granted_by": "tern"}` within the per-pass
ceiling; free-form values are rejected with `E_BAD_ALLOCATION`.

## Runtime JSON types and error codes

Authoritative registry: `fixtures/schema.json`. Summary:

- `apply` out: `{"ok": bool, "outcome": str, "duplicate": bool}` or
  `{"ok": false, "code": E_*, "detail": str}`.
- `validate` out: `{"verdict": ACTIVE|REST|INVALID|ACTION_DUE,
  "code"?: E_*, "detail": str, "action"?: {"type": "owner-reconcile",
  "owner": tern|corvid|kiln|cairn, "trigger_id"?: str,
  "package_id"?: str, "bounded"?: bool}}`.
- Timestamps are RFC3339 UTC strings; the core compares them
  lexicographically. Tests use fixed strings (fake clock), never sleeps.
- Transition rejections and validator faults share the `E_*` registry
  (see `schema.json`); `INVALID` is a validation fault, never a lifecycle
  terminal and never permission to dispatch.

## Design answers to named risks

- Terminal rows (7/9a/13/14/15) commit only with a same-transaction
  disposition (`close`, or `apply --decide`) or a bounded row-17 hold
  (`apply --hold`); bare terminal commits fail `E_MISSING_DISPOSITION`.
  A held verdict validates as pending decision work (ACTIVE), never as rest
  and never as the omission fault.
- Flight rotates at publication: the completed worker attempt never
  survives into CHECKING. Either the verifier's own bounded action
  (`verify: {action_id, owner, deadline}` on `publish`) or an explicitly
  owned bounded handoff (`handoff_deadline`, owner duty/director) is
  recorded — unbounded silence is unrepresentable (`E_BAD_ALLOCATION`).
  Verifier flight and allocation survive BLOCKED/resume and ledger replay.
- In-flight snapshot entries carry full action identity
  (`action_id`, `owner`, `deadline`, `dispatch_receipt`); overdue ledger
  work validates `E_OVERDUE_ACTION`.
- Lifecycle `BLOCKED` (active, resumable) and the `blocked` boundary
  disposition (parked question) are distinct types and code paths.
- `successor_opened` follows links to acknowledged bounded work or a rest
  leaf; unrelated busy seats/packages never satisfy a link.
- A due blocker trigger yields one bounded owner-reconciliation action per
  trigger id; after that the package rests, and the action cannot suppress
  alarms, invent successors, or restart terminals.
- No model-identity proof is ever claimed: attribution is the
  launcher-recorded actor on the ledger event, per P1's trust qualification.
