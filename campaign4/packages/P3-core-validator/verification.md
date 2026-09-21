# P3-core-validator — repair2 (v3) independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; repair2 completed 17:55:21Z; pass deadline
  2026-09-21T18:53:39Z
- **Supersedes** v2 FAIL `1e0abdfca6a512b07f4078a7bc7fc99cc0798d19f02b2b22d7eb56896206c19b`
  (archived at `campaign4/p3-attempt-history/postrepair-v2/`).
- **Authority:** contract `bc88adf2…` @ `fa6af8b0`; frozen P2 r2.1 spec
  `5bfbb071…`; prospective allocation `allocation-extension-1.md`.

## Verdict

**PASS.** The v2 defect is corrected exactly as required, all four earlier
defects remain fixed, the required evidence cases pass, and no new defect was
found. All checks were derived independently from the pinned specification and
run in fresh `/tmp` state.

## Artifact hashes (recomputed on disk)

v3 tree manifest (sorted per-file sha256 over `src/`, `tests/`, `fixtures/`,
`README.md`, `implementation-report.md`; 33 files):
`15e7fbc53a9279814b583554bb77bc7c8346723226dfda405dc2a193773ceed6` — matches
the supplied v3 manifest.

| Source | sha256 |
|---|---|
| `src/lifecycle.py` | `815b10c531fb3ffc77a67deeb91b7725b2ae9f6142f7cba5f6970be967997991` |
| `src/store.py` | `5ec562c2cf27ccaf3cc61b083e112ae07da1fddcbcb8255ea7823af029f33836` |
| `src/validator.py` | `78076f8995cf9bcbea395b9f95d3a3680ff0da39f6da948669b7643a4d2a7388` (unchanged from v2) |
| `src/cli.py` | `c382d20017ff3713aeb7cf00e59b09ed161754410c52f8b42b5274ee8a8367e5` |
| `tests/test_lifecycle.py` | `63dfde2f68790b2181f11a325d780e32f628b6f01fe9acfb0b3fb4265d29afba` |
| `tests/test_validator.py` | `85fee4c04813ef76942feed72999c0f2eab1dbcc9447e87c267965d367ad96f4` |
| `fixtures/schema.json` | `965546c83585336d29b33ed97f73b729058a61dd03e2c243ba8320a41e14ef45` |
| `README.md` | `3c0850db9bed894ad19ec537eae444ca8bf9bd2b023a97f00b668aa49b0d2938` |
| `implementation-report.md` | `3b1c5d500bd1edc4f84a7b09b9d196f37db63e62250a692d5b91ec678d522eee` |
| v2 archive manifest | preserved under `p3-attempt-history/postrepair-v2/` |

## (a) v2-fails / v3-passes reproducer

Scenario: worker `start` deadline `17:10Z`, publication `17:05Z`, verifier action
`vf1`/owner `corvid`/deadline `17:25Z`, validation at `17:15Z`.

- **v2 (archived, byte-exact):** `INVALID E_OVERDUE_ACTION` — reproduced by
  importing the archived v2 `src/` and replaying the same events.
- **v3:** snapshot `in_flight = [{phase:CHECKING, action_id:vf1,
  owner:corvid, deadline:17:25Z, dispatch_receipt:acknowledged}]` and
  `validate` → **`ACTIVE`**. The worker attempt's flight is cleared on
  publication (`src/lifecycle.py:219`) and the verifier's own bounded action is
  recorded (`:221–228`); a completed attempt is never reported in flight.

## (b) Verifier expiry faults correctly

Same package validated at `17:30Z` (past the verifier `17:25Z` deadline) →
`INVALID E_OVERDUE_ACTION`. Dropping the deadline is not sufficient and was not
done; the verification stays bounded.

## (c) Reopened store reproduces both outcomes

Closing and reopening the SQLite store reconstructs the same `in_flight`
entry (`vf1`/corvid/17:25Z/acknowledged) from the ledger: `ACTIVE` at `17:15Z`
and `E_OVERDUE_ACTION` at `17:30Z` both reproduce.

## (d) Blocked verification resumes the same action/allocation

CHECKING → `interrupt` (`remaining_verifier_s=600`) → `resolve` returns to
`CHECKING` with the **same attempt number**, the **same flight**
(`vf1`/corvid/17:25Z), and the block cleared — no new worker dispatch or
attempt.

## (e) Publication without a dispatched verifier = bounded handoff

Publishing with `handoff_deadline:17:20Z` yields `in_flight` with
`action_id:None`, `owner:"duty"`, `deadline:17:20Z`, `dispatch_receipt:None`,
and validates **`ACTIVE`** at `17:15Z` — explicitly owned and bounded, not an
unbounded-silence ACTIVE. A publication with neither a verifier action nor a
bounded handoff is rejected `E_BAD_ALLOCATION` (`src/lifecycle.py:229–237`).

## (f) Regressions still hold

- Base suite: **40 passed** in fresh `/tmp` state (was 32); fake clock, no
  sleeps. A passing count was accepted only alongside the independent checks
  above. `validator.py` is byte-unchanged from the v2 run in which D1–D4 were
  separately confirmed; `lifecycle.py`/`store.py` changes are confined to the
  flight-rotation fix.
- **D1–D4:** unchanged code paths confirmed by the 40 tests plus the v2
  independent checks (20-min recovery rejected `E_ALLOC_EXCEEDED`; overdue
  ledger work `E_OVERDUE_ACTION`; unacknowledged successor
  `E_DANGLING_SUCCESSOR`; bare terminal rejected, hold → ACTIVE,
  `close`/`record_terminal` → REST).
- **Tern omission** → `INVALID E_MISSING_DISPOSITION`; **legitimate rest** →
  `REST` with no action; **`ACTION_DUE`** exactly once per trigger id; chain
  live `ACTIVE` / two-successors `REST`.
- **Atomic publication** (temp, fsync, `os.replace`, after commit); restart
  reconstruction; duplicate event delivery ignored; crash-after-durable-start
  reconciles the same action with executor run count 1; acknowledged vs
  intended delivery distinct.
- **No live effects:** `src/` contains no `subprocess`/`os.system`/`popen`/
  `signal`/`systemctl`/kill/stop/wake call; the fake executor and caller `now`
  remain the only execution/clock paths. Stdlib-only.

## Note

`README.md`/`fixtures/schema.json` document the verifier flight, the bounded
handoff and the allocation ceilings consistent with the corrected behavior.
No new defect was found; the v3 revision is ready for Tern's acceptance.
