# P6-r2.1-event-handoff — repair candidate recheck

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤20-minute candidate recheck
- **Authority:** contract `71b455c2…` @ `e9993e7f`; `director-repair-decision.md`;
  bound `4c7d8b2f2f5602` (= repaired `src/harness.py`
  `4c7d8b2f560297a3c95e7e88ac4901c18cee2d8584710cf6bf978efda48241a1`).
- **Preserved:** first review `candidate-review.md` (`3ac2c5a0…`) untouched.
- **Mode:** candidate check only — **no live effect**; all injections via
  injected collaborators.

## Verdict

**FAIL** — one bounded defect in the exact Stage C fixture plan. D1–D4 code
behaviour is corrected and independently exercised through the connected
harness and injected production branches, and 135 candidate + 59 core tests
pass. But the plan's `run` step invokes `harness.py … --live run`, and `run` is
not a harness subcommand (`timer-callback` / `setup` / `run-fixture`), so the
exact plan fails with argparse `invalid choice: 'run'` before any connected
fixture executes.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/harness.py` | `4c7d8b2f560297a3c95e7e88ac4901c18cee2d8584710cf6bf978efda48241a1` |
| `src/turn_handoff.py` | `a17043549103dbbea8638d8642a3e2af7c455c07703d88c9aad80052ad5ed488` |
| `src/host_adapter.py` | `69c921b44c1f0ab4a3d55a467bd99719c177bb75844d423e3207b691693ee4d4` |
| `tests/test_event_handoff.py` | `870f1565da0cf92a603329087af63389e3709abac4aea7b14cb3729891892dae` |
| `fixture-plan.json` | (recomputed; carries the defect below) |

## Commands and results

```bash
cd campaign4/packages/P6-r2.1-event-handoff
PYTHONPATH=src python3 -m pytest tests/ -q        # 135 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
PYTHONPATH=src python3 src/harness.py --help      # {timer-callback,setup,run-fixture}
PYTHONPATH=src python3 src/harness.py --db … --manifest … --claims … --qid P6H run
#   error: argument cmd: invalid choice: 'run'
```

## D1–D4 verified corrected (connected branches, injected)

| Family | Case | Observed |
|---|---|---|
| D1 | connected `run_handoff` on a bound end + claim file + real artifact | `transition-committed`; ledger phase CHECKING, flight `a-v1` |
| D1 | plan setup/assertions/cleanup | `setup` subcommand valid; assertions non-trivial with failing exits; cleanup verifies each step; no `ITEM-FROM-TURN-END`, no `\|\| true` |
| D2 | non-end turn / unbound stream / stale execution | `E_NOT_END` / `E_UNBOUND_TURN` / `E_STALE_TURN`, phase unchanged, no `turn-seen` written |
| D2 | artifact mutated on disk | recompute detects → owned recovery (no invented success) |
| D2 | worker-supplied terminal disposition | rejected (`E_STALE_TURN`/`E_FORGED_DISPOSITION`); `_close_verify` needs director-authorized disposition |
| D3 | `drive_next` crash after intent/seen | first call raises (simulated crash); **retry rolls forward** → `transition-committed`, CHECKING (no stuck RUNNING, no false duplicate) |
| D3 | outbox acked then reconcile | transport calls 1→1, no resend |
| D3 | outbox pending (one send) then reconcile | 1→1, `held-awaiting-receipt` (no unconditional second send) |
| D4 | partial tail then completed rewrite | held `partial-tail-held`; completed record emits exactly once |

## The defect (bounded)

`fixture-plan.json` `run` step ends `… --qid P6H --live run`, but the harness
subcommands are `{timer-callback,setup,run-fixture}`. Running the exact plan
command yields `argparse: error: argument cmd: invalid choice: 'run' (choose
from 'timer-callback', 'setup', 'run-fixture')`, so Stage C would fail before
constructing the connected fixture — the same "plan string vs connected branch"
gap the repair was meant to close. **Required correction:** change the plan's
`run` token to `run-fixture` (and re-hash the plan); no code change is needed
for the harness itself, and the plan hash must be re-signed by Tern.

## Structural / retained

- 135 candidate tests (initial 130 plus new authority/crash/partial cases) + 59
  core pass; changed tests carry explicit rationale for the repaired boundary.
- No duplicated method bodies in `turn_handoff.py`, `harness.py`,
  `host_adapter.py`.
- No live effect in this check: production transport/timer paths remain
  injectable and fail closed in live mode; I did not execute `run-fixture`,
  `setup`, the wake script or any host process.

## Limitations

Simulated/injected evidence only; the defect is a plan-command finding confirmed
by running the plan's own command string in injected mode. Stage C remains HELD.
