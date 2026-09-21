# P6-live-recovery — Stage B independent candidate check

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21/22; one 20-minute candidate pass (P6 verifier grant 55m:
  20+20 candidate + 15 live witness)
- **Authority:** contract `174377f1…` @ `91f19cf3`; admission-review `ffed97d9…`
- **Mode:** candidate check only — **no live effect**; I executed no host
  script and collected no credentials.

## Verdict

**PASS** for the Stage-A candidate. Pure/injected tests pass, accepted P5/core
semantics are unchanged, the host-interface assumptions are read-only and
hash-captured, the effect allowlist is confined to fixture-owned resources,
identity/receipt/timer/rollback behaviour is implemented and exercised, and the
fixture is feasible. One bounded forward item must be closed before Stage C
Tern's signed release: `fixture-plan.json`'s `commands` are a dry-run descriptor
rather than exact executable commands.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/host_adapter.py` | `f2f361b88664b54a8c3ea836cea484e37b24f957bfe9194e513d24f555497899` |
| `tests/test_host_recovery.py` | `bd739c77a36030088467a5deafb7b00170470d69eed3a78a6d271f4b2f65b382` |
| `fixture-plan.json` | `f6659330abf66defb46ebcd19c8344c4b83f33cf730d1327d26718ddb130cde0` |
| `host-inventory.json` | `e304039fcbaa73bad733fad36c27cac878101ceb91328935b08c8db993963083` |
| `retirement-matrix.json` | `c05c79277ccc7d6ac27e495ecee4b7378f72edd4f8d8d63707fe513971e09cf4` |
| `rollback.md` | `36b54eebcad712fa891dcbeae3e087290bfb427a8c90e0ad5d54ec464081da03` |
| `implementation-report.md` | `8093d6fff9e5464606d017b52c5050d6c64626011e979e4aeca622064b6c4558` |
| `interface.md` / `README.md` | `b3cea34e…` / `621f72cd…` |

## Commands and results

```bash
cd campaign4/packages/P6-live-recovery
PYTHONPATH=src python3 -m pytest tests/ -q        # 97 passed (83 retained + 14 host-recovery)
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```

## Accepted semantics unchanged

The copied core is **byte-identical** to the verified P5-r2 tree — `driver.py
80d770db…`, `ingress.py c9327f85…`, `store.py dafaeb33…`, `lifecycle.py
7ebaf466…`, `validator.py dcecfc1d…` — so no accepted semantic change was made
or needed; the new machinery is confined to `src/host_adapter.py`. All seven P5
test files are byte-identical (`test_ingress`, `test_repair_p5`,
`test_repair2_atomic`, `test_atomic_authority`, `test_durable_events`,
`test_rehearsal`, `test_repair`), preserving 83 P5 regressions.

## Host-interface assumptions (read-only, hash-captured)

`host-inventory.json` records `~/.config/agent-deck` and hashes of `wake`
(`fd31cb61…`), `campaign4-pause` (`6638568b…`), `campaign4-watch`
(`6c00cc3e…`), `openwork` (`02940149…`), `acp-go` (`5fb78d08…`),
`acp-go-controller` (`51eadff0…`), plus ACP history/session directories and
observed unit states. Collection was declared read-only
(`sha256sum`/`file`/`systemctl list-units`/`ls`), no script executed, no
credentials collected, host clock read only. Consistent with the retirement
ruling: `wake` in scope as transport (global behaviour unmodified),
`campaign4-pause` unchanged emergency actuator.

## Effect allowlist and grants

`fixture-plan.json` confines the fixture to `p6-fixture-recovery-1`:
`/tmp/p6-fixture-ledger.db` (disposable, never the campaign ledger),
`p6-fixture-worker`/`p6-fixture-verifier` seats in the campaign4 profile, and a
single one-shot relative `p6-fixture-recovery-1.timer`; the existing four
campaign seats are explicitly never stopped or repurposed. Candidate effects
are therefore allowlisted to fixture-owned seats/files/units/ledger; shadow
comparison is read-only. Candidate verifier budget 20m is within the P6 grant.

## Identity, receipts, timers, rollback

- **Receipts/cursor:** `capture()` persists 5-tuple-keyed receipts
  (package/attempt/action/event/execution) plus a durable `host-cursor`; artifact
  payloads are recorded, never trusted as completion; `reconcile_send()` treats
  queued/sent as `hold-for-receipt`, explicit `failed` as `owned-failure` with
  deadline fallback, and unknown as `hold-for-reconciliation` (no blind retry).
- **Identity:** equality-only execution IDs, no suffix inference; late results
  from non-current executions are retained as stale evidence and never applied;
  same-action resume keeps action/attempt and records the `resume` relationship;
  genuine replacement commits the `supersedes` note and new registration
  together before any external effect (per the action-identity ruling).
- **Timers:** `arm_from_ledger()` derives remaining authorized duration and
  raises an owned fault when expired/malformed; `fire()` rejects
  stale/early/cancelled against the authoritative ledger deadline, not the
  timer's own copy.
- **Rollback:** `rollback.md` orders disable-candidate-effects → reconcile
  action/execution IDs and timers → restore exactly one owner, then delete
  fixture artifacts; no restore-then-disable and no indefinite dual controller.
  Stage A demonstrates only the injected reconcile paths (no live rollback).
- `src/host_adapter.py` imports only `json` and `validator`; a source scan finds
  no subprocess/socket/signal/os.system/popen/requests/urllib/time.sleep/while
  True and no `agent-deck` execution; no duplicated method bodies (259 lines).

## Bounded forward item (must close before Stage C)

`fixture-plan.json`'s `commands` field is a **dry-run descriptor**
(`print('fixture dry-run descriptor; not executed in Stage A')`), not the exact
executable fixture commands. Stage A requires proposing "exact … commands", and
Stage C is gated on Tern signing this exact plan hash, so a placeholder cannot
be meaningfully signed. The IDs, seats, units, ledger path and cleanup are
concrete and allowlisted; only the command text must be made exact and re-hashed
before Tern's release. This is a plan-completeness item, not a candidate-code or
accepted-semantics defect.

## Readiness

Candidate PASS; live fixture not yet runnable. Remaining gates: this PASS,
exact `fixture-plan.json` commands, and Tern's explicit signed release of the
exact fixture-plan hash (Tern's gate, not Brian's), then cairn's one ≤15m
fixture with corvid's ≤15m live witness. No live effect occurred during this
check.
