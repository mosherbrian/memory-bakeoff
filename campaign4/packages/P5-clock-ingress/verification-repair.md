# P5-clock-ingress — post-repair verification (repair-1)

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; one ≤20-minute post-repair pass (remaining P5 verifier grant)
- **Authority:** contract `ca8a9e05…` @ `ec332546`; `director-repair-decision.md`;
  archived initial `p5-attempt-history/initial/` (25-file manifest).
- **Preserved:** initial PASS `verification.md` (`33ae853d…`) untouched; this is
  the post-repair verdict.

## Verdict

**FAIL** — one bounded defect in the repaired terminal route. D1 (attribution),
D2 (deadline/phase authority for start, verify, handoff, hold and wrong-phase
grants) and D3 (unique epoch, backward-UTC reconciliation) are all corrected and
independently reproduced; the 69 local + 59 core tests pass with no live
effects. But the accepted terminal write route `TrustedIngress.record_terminal`
(used by `Driver.terminal_close`) rejects a legitimate verdict+disposition
commit, so the "terminal routes" requirement is not met.

## Bound hashes (recomputed)

| Artifact | sha256 | matches |
|---|---|---|
| `src/driver.py` | `80d770db9d8de374be69a0ef13a802f19c599efc442a7d03f0a16f3e89e2f9eb` | bound |
| `src/ingress.py` | `ba66ec02ba4b8bfa0d8efc032d471939b9544c3e714069170f55634bf1d5daa8` | bound |
| `tests/test_ingress.py` | `129825f4dc7c746852caccbbff7e018eb12f456d432f514ef34993233dd09c9e` | bound |
| `implementation-report.md` | `df3961c0f29c5f8752f7951ce4076da3e1cfa11c88a8ff44f8e657825eb1296a` | bound |
| `interface.md` | `8dff6d373009c8ff79387ae1b28af25eb4ee2d71e140c5ce353764d0717d47d4` | bound |
| `tests/test_repair_p5.py` | `a4a69e12444f908e51d0877b6385650f7caf3245b2570690344a25d8f9423116` | new |

Archived initial manifest: **25/25** files hash-exact.

## Commands and results

```bash
cd campaign4/packages/P5-clock-ingress
PYTHONPATH=src python3 -m pytest tests/ -q        # 69 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
PYTHONPATH=src python3 director-probes.py         # all four corrected
PYTHONPATH=<archived-initial>/src python3 director-probes.py      # all four FAIL
```

## D1/D2/D3: archived initial FAIL vs repaired corrected

`director-probes.py` on the archived initial reproduces every recorded failure
(caller actor accepted → `admitted`; grantless 2099 verifier deadline accepted
→ `checking` with flight deadline 2099; CHECKING grant accepted for a start
without a hint → `running`; `restart_epoch_reused: true`). On the repaired tree:

| Probe | Repaired |
|---|---|
| caller actor | `E_FORGED_ATTRIBUTION` |
| ungranted 2099 verifier deadline | `E_DEADLINE_UNAUTHORIZED` |
| wrong-phase grant, no hint | `E_GRANT_MISMATCH` |
| restart epoch reused | `false` |

Unshared mutations I added, all fail-closed as required:

- **D1:** forged reader and forged director claims → `E_FORGED_ATTRIBUTION`;
  untrusted/missing trusted `actor` → `E_UNTRUSTED_ACTOR`; forged `decide` actor
  in `record_terminal` and in an atomic `decide` subevent →
  `E_FORGED_ATTRIBUTION`.
- **D2:** start with no duration/grant → `E_NO_AUTHORIZATION` (fallback
  removed); `phase_hint` → `E_FORGED_HINT`; nested verify 2099 without grant →
  `E_DEADLINE_UNAUTHORIZED`; a distant deadline covered by a real pinned
  `verify` grant → accepted; distant handoff without grant → rejected.
- **D3:** two lifetimes with identical clock values → different epochs; a
  backward-UTC reopen quarantines writes with `E_AMBIGUOUS_RESTART` (owner
  `cairn`), and writes resume after `reconcile_clock` with the flight deadline
  unchanged.

No alternate public write path: only `src/ingress.py` calls `store.append` /
`store.record_terminal`. No duplicated method bodies; no live effects.

## The defect (bounded)

`TrustedIngress.record_terminal` (`src/ingress.py:514–525`) stamps the verdict
and decide events through `_stamped`, which calls
`_check_phase("decide", qid, rev)` (`src/ingress.py:296–306`) against the
**pre-verdict** ledger phase. From `CHECKING` the actual phase is not in
`TERMINALS`, so a legitimate atomic close is rejected:

```
terminal_close ERR: E_PHASE_MISMATCH decide not allowed in actual phase CHECKING
phase: CHECKING
```

`Driver.terminal_close` (`src/driver.py:415–423`) routes through this method, so
the accepted terminal write route cannot perform the very commit it exists for
(verdict CHECKING→COMPLETE + director disposition in one transaction). The
worker's 69 tests exercise `record_terminal` only on the forged-actor path
(which fails earlier at `_bind_actor`), so the legitimate path is unexercised.

**Required correction:** validate the `decide` event against the phase it will
actually see inside the atomic transaction (post-verdict terminal), or exempt
the atomic subevent from the pre-transaction phase check and rely on the store's
atomic validation/rollback — without weakening D2 authority. Re-hash and
re-verify; no accepted-core change needed (ingress/driver-local).

## Limitations

- Simulated evidence only; no live adoption or host clock change.
- Initial PASS preserved; initial archive untouched. This verdict concerns the
  repaired bytes above only.
