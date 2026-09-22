# P6-r2.1-event-handoff — Stage B candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one 20-minute candidate pass (grant 40/40)
- **Authority:** contract `71b455c2…` @ `e9993e7f`; admission-review
  `615e25bd…`; ruling `TURN-END-HANDOFF-RULING-20260922.md` @ `883107e`.
- **Mode:** candidate check only — **no live effect**; all injections used
  fakes/injected collaborators.

## Verdict

**PASS** for the Stage A candidate. The runtime turn-end path is event-driven
with persisted cursors and reconciliation; completion claims are route-free and
reject worker-supplied routing/authority; a validated end drives the next
authorized dispatch through the ledger plus a durable outbox that acknowledges
only after delivery; failed/cancelled ends produce owned recovery, not success;
deadlines remain backstops. 130 candidate tests + 59 core pass, D2/D3/D4 are
retained, and no duplicate method bodies or plan placeholders remain.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/turn_handoff.py` | `db77cfffaf76950b5959b3e4c54c868a667c6578e7f933a06a4ae06d4e6bcc53` |
| `src/host_adapter.py` | `2211751ad8fcecb1588622572e44d8bf8a11c2ed6deb54d6092c9025913f6c5e` |
| `src/harness.py` | `e2c7bc66638645d78b2f430a7b0869501c5360cf48075a1d0110bef7d4895170` |
| `src/ingress.py` | `4d12429f1edd5d0f421db9321cba38a824f6ad80b30e67a510a294d1e921ff6b` |
| `src/driver.py` | `cf29d87119f40f77aa00ecd861493dc59bc06130b2dc7444e1e965be393ade64` |
| `tests/test_event_handoff.py` | `3a9e5aa1a17f4acaf897c17929fc234735d878b3b50419ed6d400dca3b177af4` |
| `tests/test_host_execution.py` | `cb3d2ec92e6fd1cda34899f30b45f4ab1f27439cac848937c54051db2c78558c` |
| `fixture-plan.json` | `4352f14dca7060bd461b1507251ba6ef3b1c0a287f3a3379e7608639b69652d5` |
| `host-inventory.json` | `31b090c8c851a139abb58c1827960b9a4758f9aa951bab33e03567f01e257f28` |
| `implementation-report.md` / `interface.md` | `00d10a37…` / `c89b0b2d…` |
| route-free claim sample | `completion-claims/ex-p6r21-stageA-1.json` `4c731d2b…` |

## Commands and results

```bash
cd campaign4/packages/P6-r2.1-event-handoff
PYTHONPATH=src python3 -m pytest tests/ -q        # 130 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```

## Expected/observed (my unshared injections, fakes only)

| Family | Case | Observed |
|---|---|---|
| route-free claim | forged `verifier`/`destination`/`next_task`/`actor`/`deadline` | `E_FORGED_ROUTE` |
| route-free claim | package mismatch / missing required / empty artifacts | `E_CLAIM_MISMATCH` / `E_CLAIM_INCOMPLETE` / `E_CLAIM_INCOMPLETE` |
| event-driven end | valid end + claim + verify_spec | `dispatched-next`; ledger flight `a-v1`, phase CHECKING; outbox pending |
| duplicate end | same end replayed | `duplicate-end-ignored`; no new launch |
| failed end | `outcome=failed` | `owned-recovery`, `escalated-owned`; phase stays RUNNING (no fake success) |
| artifacts | claim hash not bound at dispatch | `E_ARTIFACT_MISMATCH` |
| outbox | ack before delivered / after delivered | `pending` / `acked`; pending cleared only after delivery |
| outbox restart | reopen with no pending | `reconcile_outbox` returns `{}`; pending intents resend under the **same** identity (worker test) |
| watcher | append + truncation + partial/corrupt line + missing file | `ok` → `truncated-reset` (re-reads from 0, corrupt line skipped) → `rotated-missing` |
| observer | unbound/missing source | `E_UNBOUND`/owned fault, never idle |

## Structural / retained

- **No live effect in this check:** the transport/timer/observer production
  paths exist and are injectable (`subprocess` with a bounded runner, real
  `systemd` unit identity, `systemctl` verbs) but were never enabled or
  executed; `build_adapter` fails closed in live mode without a plan hash and
  non-empty allowlist; `harness` main refuses `--live` without both.
- `fixture-plan.json` contains no unresolved angle-bracket placeholders;
  runtime IDs come from a bound setup manifest.
- No duplicated method bodies in `turn_handoff.py` (203), `harness.py` (125),
  `host_adapter.py` (754); D2/D3/D4 tests retained (10 + 14); 107 prior P5/P6
  regressions retained within the 130.

## Observations (non-blocking)

- The terminal-rest branch of `run_handoff` closes via
  `terminal_close` (verify_pass + decide) and therefore requires the completion
  to have been published (phase CHECKING) first, as the worker's supported
  sequence does. Calling `terminal_disposition` directly from RUNNING fails
  ledger-authoritatively (`E_PHASE_MISMATCH`), which is correct fail-closed
  behaviour rather than an invented success. Worth documenting explicitly in
  `interface.md`.
- `outbox_send` has a `TypeError` fallback that retries `transport.send` with a
  reduced argument list; it did not trigger with the fake transport, and the
  production path uses the full signature.

## Readiness

Candidate PASS; Stage C remains held pending Tern's signed exact `fixture-plan`
hash. No live effect, service installation, seat action, global wrapper change,
host clock change, historical edit or script retirement occurred.
