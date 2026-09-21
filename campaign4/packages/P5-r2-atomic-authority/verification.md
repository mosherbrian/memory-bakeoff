# P5-r2-atomic-authority — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; one 15-minute pass (P5-r2 verifier grant 30m)
- **Authority:** contract `e09c313c…` @ `7b5772e4`; admission-review
  `e5589e87…`; parent `P5-clock-ingress` @ `88f2c18` (rejected ingress
  `371b189d…`).

## Verdict

**PASS.** The mixed `hold+decide` forged-authority breach is rejected
deterministically before any mutation; each supported atomic form has one
unambiguous validation/stamping path; both legitimate atomic close forms and a
genuine bounded hold work with trusted attribution/time; mixed, unknown,
malformed and unauthorized forms leave no partial rows and no lifecycle change,
including after reopen. D1/D2/D3 and 83 local + 59 core regressions hold; no
duplicated methods; no live effects.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/ingress.py` | `c9327f855ee0bddde5414e1e51cdb9c36139bca902de0da58f2b05d39fa1c599` |
| `tests/test_atomic_authority.py` | `dc0377afea08206297fdb3c078dcaec06039127b1f8151d0257ac0ebcd026f1b` |
| `fixtures/atomic-cases.json` | `c8f091670957ae084fe18a8dcda4b4c65da191fab522bff240b05470ef6f6ec1` |
| `fixtures/probe-parent-evidence.json` | `03c4c37b7ca79beed855f0324738b83290e4b007fa341570e3c8fd04f47ad84b` |
| `implementation-report.md` | `dd16ccc04c068713429c6bf3c68a0004851db48e4008925511d674358088bbc9` |
| `interface.md` | `99e6e9e75ee8ea9541cef7b0e90b7356dfed6a8a89c3117c76bb2d63e813ec7e` |
| `README.md` | `61ea99be663d5e5107aea2c3f09875ff13bc9c0e65ad90242027cc4050305501` |
| `src/driver.py` / core copies | unchanged (`80d770db…` etc.) |

## Commands and results

```bash
cd campaign4/packages/P5-r2-atomic-authority
PYTHONPATH=src python3 -m pytest tests/ -q        # 83 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
PYTHONPATH=src:tests python3 director-mixed-atomic-probe.py        # REJECTED E_MIXED_ATOMIC, []
PYTHONPATH=<parent>/src:<parent>/tests python3 director-mixed-atomic-probe.py  # ACCEPTED forged (reproduced)
```

## Expected/observed

| Case | Expected | Observed |
|---|---|---|
| mixed probe on pinned parent | forged commit | `ACCEPTED`; `mixed-d` stored with actor kiln/director, `at=2099-01-01`, no receipt |
| mixed probe on repaired | rejected, no writes | `REJECTED E_MIXED_ATOMIC`, `[]` rows |
| `record_terminal` genuine | commit both, trusted | COMPLETE+disposition; both rows; both `_trusted`, `at==recorded_at` |
| `append(atomic=decide)` genuine | commit both, trusted | COMPLETE+disposition; both rows |
| `append(atomic=hold)` authorized | bounded hold | COMPLETE held; decision_task set; snapshot carries DECISION in-flight |
| mixed `hold+decide` (both key orders) | reject before mutation | `E_MIXED_ATOMIC`; 0 rows; phase CHECKING |
| unknown key / empty / non-dict / decide non-dict | reject | `E_BAD_ATOMIC`; 0 rows |
| forged sub actor / hold with actor | reject | `E_FORGED_ATTRIBUTION`; 0 rows |
| decide without trusted actor | reject | `E_UNTRUSTED_ACTOR`; 0 rows |
| hold deadline 2099 without grant | reject | `E_DEADLINE_UNAUTHORIZED`; 0 rows |
| atomic pair revision mismatch | reject | `E_BAD_ATOMIC`; 0 rows |
| reopen after rejected mixed | no partial rows/history preserved | state CHECKING, 0 rows for both ids |

## Structural / retained

- One unambiguous atomic path: `_ATOMIC_FORMS` plus `_check_atomic` rejects any
  shape other than exactly `{hold}` or `{decide}` (with optional `grant_ref`)
  before `store` is touched; only then are `_stamp_atomic_decide`/
  `_check_atomic_pair` (decide) or `_grant_cover` (hold) applied.
- No duplicated method bodies (`ingress.py` 628 lines, AST scan clean); only
  `src/ingress.py` calls `store.append`/`store.record_terminal`.
- D1/D2/D3 tests retained (83 = 77 prior + 6 atomic); 59 accepted core pass;
  REST/INVALID/ACTION_DUE and no-duplicate dispatch retained.
- No live effects: no subprocess/socket/signal/os.kill/os.system/popen/requests/
  urllib/time.sleep/while True in `src/`; stdlib only.
- `fake.py` remains the internal test-only helper and is not an accepted ingress
  route; unchanged (`fe7d4ef7…`).

## Limitations

Simulated evidence only; no live adoption or host clock change. No repair
requested; PASS for Tern's boundary decision.
