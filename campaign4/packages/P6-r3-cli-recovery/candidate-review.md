# P6-r3-cli-recovery — Stage B candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one 20-minute candidate pass (grant 40/40)
- **Authority:** contract `467c3f4d77a5…` @ `a35eace`; admission-review
  `cfaa5f71…`; pinned `cli-acceptance-cases.md` `b3422cfd…`
- **Bound:** `39c52dd2bc19…` = `src/driver.py`
  `39c52dd2bc1906fd90ac6dee4535eda5e02252450d35d33a11aec9417885f36e`
- **Mode:** candidate check only — **no live effect**; OS boundary injected with
  PATH shims (wake/systemd-run/systemctl record calls, touch nothing real).

## Verdict

**PASS.** The exact CLI now runs the connected recovery graph with injected OS
boundaries: it binds session/stream from explicit evidence, sends the authorized
worker and verifier wakes, subscribes to the stream (an end appended after start
is observed), validates the route-free claim and recomputed artifact, commits
the ledger transition, writes `latency.jsonl`, exits 3 on no-end, and fails
closed on plan/allowlist/clock violations. 150 candidate + 59 core tests pass.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/driver.py` | `39c52dd2bc1906fd90ac6dee4535eda5e02252450d35d33a11aec9417885f36e` |
| `src/harness.py` | `5b36775b64760438216bcbe379e4284f367c009c40ea07bbb16fe7de21dff759` |
| `src/turn_handoff.py` | `1505dd97bab5c68c39eba1b3e060306aa10a54af8ecdb6754d815c494c228cc9` |
| `src/host_adapter.py` | `69c921b44c1f0ab4a3d55a467bd99719c177bb75844d423e3207b691693ee4d4` |
| `tests/test_cli_acceptance.py` | `e040a17a5d06e7480d039bb7655e6b4dabb54b4b68f9ad93cff89faa5e3e0aa1` |
| `fixture-plan.json` | `8889df11e2db859a981701005e0e6d57ffa9d2a9f35667dc99a1f5c36089401e` |
| `implementation-report.md` / `interface.md` | `599d530d…` / `6527771c…` |
| `host-inventory.json` | `ac6d9f5994401b41e90b126a0919b759ef6cc4661e6010626ad59db0c3efc46f` |

## Commands and results

```bash
cd campaign4/packages/P6-r3-cli-recovery
PYTHONPATH=src python3 -m pytest tests/ -q        # 150 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus my own black-box runs of the exact CLI (`harness.py setup` /
`run-fixture`) as a subprocess with PATH shims and a background stream producer.

## C1–C12 expected/observed (my independent CLI runs)

| Case | Expected | Observed |
|---|---|---|
| C1 host clock on live | fake clock forbidden | `build_adapter(live=True, clock=FakeClock())` → `E_DISABLED`; live path constructs `HostClock` |
| C2 worker send | CLI sends the worker wake | injected `wake` shim trace contains `CALL wake p6-fixture-worker …` |
| C3 subscribed end | end appended after start is observed | background producer appended `start`/`end` after CLI launch; CLI detected it and committed |
| C4 session from evidence | setup needs explicit session/stream | setup without `--session` fails; with `--session sess-evid --stream-key sk-evid` the manifest carries exactly those |
| C5 no-end | nonzero exit + failure sample | `run-fixture` with no source → **rc 3**, `owned-failure`, zero-signal latency row written |
| C6 latency writer | rows with real fields; zero cannot pass | `latency.jsonl` written with 2 rows (`action/dispatch_at/detected_at/committed_at/outcome`) |
| C7 deadline derivation | from trusted start, not literal `01:00Z` | `run_fixture` computes `verify_deadline = trusted_now + duration_s` |
| C8 closed graph | worker→verifier→director | wake trace shows worker **and** verifier seats; ledger `admit,authorize,start,publish,verify_pass,decision_task,decide`; outcome `terminal-rest` |
| C9 fault matrix | owned recovery, no routing | missing claim (end, no claim file) → `owned-recovery`/`escalated-owned`, latency sample written |
| C10 cleanup | verifies before reporting | plan cleanup runs `systemctl show …ActiveState` (inactive) and archives `fixture.db/manifest/latency` before deleting; assertion checks `rollback-report.json` exists |
| C11 plan/allowlist binding | fail-closed on mismatch | wrong `--plan-hash` refused; non-allowlisted seat refused; live requires plan+hash+allowlist |
| C12 retained/reopen | no duplicate effects | 150 tests retain D1–D4 and 135+59 semantics; CLI reopen tests present |

No retroactive PASS is claimed: the present plan's `run-fixture` provenance
remains unreconciled; I verified the **present bytes** only.

## Observations (non-blocking)

- Configuration faults (`E_UNBOUND` from `setup`, `E_PLAN_MISMATCH` /
  `E_DISABLED` from `run-fixture`) raise `OwnedFault` out of `main` as an
  uncaught traceback with exit 1, rather than the docstring's clean exit 2
  (usage) / 3 (owned failure). They still fail closed; a small `try/except` in
  `main` printing the owned code and returning 3 would match the documented
  contract. Not a behavioural breach.
- The cleanup `rollback-report.json` content remains static strings, but it is
  now gated by preceding unit-state and archive/identity commands, addressing the
  earlier "unconditional reconciled" finding at the plan level.

## Limitations

Simulated/injected evidence only; the injected OS boundary proves the CLI
composition and call/ledger/latency observables, not live host behaviour. Stage
C remains HELD pending Tern's signed exact-plan hash. No live effect, service
installation, seat action, global wrapper edit, host clock change, research or
script retirement occurred.
