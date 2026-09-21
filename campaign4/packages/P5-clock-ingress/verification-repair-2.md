# P5-clock-ingress — repair-2 verification (atomic close ordering)

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; one ≤15-minute pass (ext-1 verifier grant)
- **Authority:** `allocation-extension-1.md` (`92299f8`); prior verdicts
  `verification.md` (`33ae853d…`) and `verification-repair.md` (`3221be1f…`)
  preserved; rejected repair-1 archived `p5-attempt-history/repair-1/`.

## Verdict

**PASS.** The legitimate atomic close now commits terminal state and its
disposition together from `CHECKING` through both supported API forms, survives
reopen, and validates the disposition against the post-verdict terminal phase
without disabling phase checks. Negative/forged pairs leave no partial rows and
lifecycle unchanged. D1–D3 and all 77 local + 59 core regressions hold; no live
effects and no duplicate method bodies.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/ingress.py` | `371b189d16596fe736869e39cdb3a3b3424fd06529428fce8ad1febfc8f1e549` |
| `tests/test_repair2_atomic.py` | `8f253cb1a87f1355f52ad8565c37b8f20ef6ccec91ad129c2ad8638c482d6c9e` |
| `implementation-report.md` | `755995b57d8d54670f5cdfc9289fcfaa4de2b1a701b8d25179f46d88355aaf7a` |
| `interface.md` | `b9bbaf98f400cb5fa60a5972aa12b699fc1c4f81a7748189c7ff21b1e9761b2e` |
| `fixtures/clock-cases.json` | `2ac288b5962fa12af54143f6a6d00aa2c65bac91421b345bb8c6138c615e19d5` |
| `tests/test_rehearsal.py` | `422ee6b6dcdd0d0e1840700b1dd962ee6580f9335b4ed5e7b1e2eec0d290da8c` |
| `src/driver.py` | unchanged `80d770db…` |

## Commands and results

```bash
cd campaign4/packages/P5-clock-ingress
PYTHONPATH=src python3 -m pytest tests/ -q        # 77 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
PYTHONPATH=<archived repair-1>/src python3 <terminal_close>       # E_PHASE_MISMATCH (reproduced)
```

## Expected/observed (independent positive and negative transactions)

| Case | Expected | Observed |
|---|---|---|
| archived repair-1 `terminal_close` from CHECKING | fail, no writes | `E_PHASE_MISMATCH`, phase CHECKING (reproduced) |
| `record_terminal` from CHECKING | terminal + disposition together | `('complete','closed-question_answered')`; phase COMPLETE, disposition set; both rows present; both events actor-bound and `at == receipt.recorded_at`, epoch-trusted; survives reopen with historical epoch |
| `append(atomic=decide)` from CHECKING (matching qid/rev) | commit both, trusted stamping | COMMITS; `vp`/`dz` both 1 row, trusted actor (verifier/director), `at == recorded_at`, current epoch; reopen COMPLETE+disposition |
| replay of that verdict/atomic pair | idempotent | `('duplicate-ignored', True)`, rows stay 2 |
| invalid disposition (`done-ish`) | no partial write | `TransitionError`; 0 rows; phase CHECKING |
| standalone `decide` from CHECKING | gated | `E_PHASE_MISMATCH`; 0 rows |
| forged `decide` actor | rejected | `E_FORGED_ATTRIBUTION` |
| atomic pair qid/rev mismatch | rejected, no writes | `E_BAD_ATOMIC`; 0 rows; phase CHECKING |

Both public atomic forms (`record_terminal` and `append(atomic=decide)`) stamp
both events from the trusted context and never accept a caller-timed/unstamped
subevent; `_check_atomic_pair`/`_simulate_post_phase` validate the disposition
against the post-verdict terminal phase via the pure core before any write, and
standalone `decide` keeps the current-phase terminal gate (`_stamped_decide` vs
`_stamped`). D1/D2/D3 evidence from the prior pass is retained and unchanged.

## Structural checks

- No live effects: `src/` contains no subprocess/socket/signal/os.kill/
  os.system/popen/requests/urllib/time.sleep/while True; stdlib only.
- No duplicate method bodies (`ingress.py` 610 lines, AST scan clean).
- `src/ingress.py` is the only P5 route calling `store.append` /
  `store.record_terminal`.
- 77 local + 59 core tests pass.

## Observation (non-blocking)

`src/fake.py` (the pinned P4 fake-dispatch helper, byte-unchanged `fe7d4ef7…`)
still exposes a `dispatch()` that calls `store.append` directly. It is not wired
to the P5 driver and the no-alternate-path claim is documented as scoped to
`driver.py`/`status.py`/`supervisor.py`; it is a test utility, not a public
ingress route. Worth scoping explicitly in a future cleanup, but it is outside
this repair and does not affect the atomic-close verification.

## Limitations

Simulated evidence only; no live adoption or host clock change. Both earlier
verdicts are preserved; this verdict binds the repaired bytes above.
