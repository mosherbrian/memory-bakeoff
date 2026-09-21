# P3-core-validator — post-repair verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; repair completed 17:55:21Z; deadline 2026-09-21T18:25:21Z
- **Authority:** contract `bc88adf2…` @ `fa6af8b0`; frozen P2 r2.1 spec at `5bfbb071…`
- **Supersedes** v1 FAIL `4a7032d5…`.

## Artifact hashes (recomputed on disk)

Worker-output tree manifest (sorted per-file sha256 over `src/`, `tests/`,
`fixtures/`, `README.md`, `implementation-report.md`; 31 files):
`166340443faf2343079c260224d50d899c8a7013d6d13ad3ad4592e654cd2f37` — matches
the supplied v2 tree hash.

| Source | sha256 |
|---|---|
| `src/lifecycle.py` | `763c8afeef2434746141c3abadbfcb7b375f3a681614ac0d8c5b52ef50faee10` |
| `src/store.py` | `f30b47cc0ced9f8f639af9ab1fbf099697712a9a153cd74868fd96f16774a7bb` |
| `src/validator.py` | `78076f8995cf9bcbea395b9f95d3a3680ff0da39f6da948669b7643a4d2a7388` |
| `src/cli.py` | `c382d20017ff3713aeb7cf00e59b09ed161754410c52f8b42b5274ee8a8367e5` |
| `tests/test_lifecycle.py` | `a2d89cd47dc9c8e1150e71096d0348ab6adada2054fc8a9faefb66559bb80981` |
| `tests/test_validator.py` | `11edfd560893c7f58da57b23296009520aa38cd663e01ac02f2c1dcc323b8940` |
| `fixtures/schema.json` | `16bef414c06bf5631b6c31d16eb985f869a3167d2044083555a87597998f9726` |
| `README.md` | `857c68390882dc6a260eccaa67461957533ac5ad88d66a1c8f6ede29195be2b2` |
| `implementation-report.md` | `53a79dbc5072b66b00467b3f7b1a8f83d74e79fbec5477812f2ee8c07b666a46` |

## Verdict

**FAIL** — one bounded defect, newly introduced by the D2 repair. The four v1
defects D1–D4 are corrected and verified; all listed regressions hold. The new
defect is a false-positive alarm on a normal lifecycle state and must be fixed
before this validator can be trusted not to raise false INVALID faults.

## D1–D4 corrections: verified PASS

- **D1 allocation enforcement — PASS.** `apply()` now enforces
  `budget.passes.verify.max_s` and controller-recovery `HARD_RECOVERY_MAX_S=600`:
  reproduced that a `recover` event with `pass_budget_s=1200` (the P2 r2.1
  archive-recheck shape) is rejected `E_ALLOC_EXCEEDED`, a 540 s recovery is
  accepted, a verifier pass past its budget is rejected, a free-form
  `new_allocation="10m"` is rejected `E_BAD_ALLOCATION`, and a malformed grant
  is rejected while a valid `{"grant_s", "granted_by":"tern"}` is accepted.
- **D2 full in-flight identity — PASS for its stated case.** `publish_snapshot`
  now emits `action_id`, `owner`, `deadline`, `dispatch_receipt`; a
  ledger-derived in-flight attempt past its deadline validates `INVALID
  E_OVERDUE_ACTION`, not `ACTIVE`. (But see the new defect below.)
- **D3 successor liveness — PASS.** `_live_ids` requires
  `dispatch_receipt == "acknowledged"` **and** a finite deadline; a
  `successor_opened` naming an in-flight entry with `dispatch_receipt:"intended"`
  and no deadline validates `INVALID E_DANGLING_SUCCESSOR`.
- **D4 atomic terminal + disposition — PASS.** A bare `verify_pass` commit is
  rejected `E_MISSING_DISPOSITION`; `apply --hold` commits a row-17 held state
  that validates `ACTIVE` (not the omission fault); `close`/`record_terminal`
  commits verdict + disposition in one transaction and validates `REST`; an
  expired hold validates `E_OVERDUE_ACTION`.

## The new defect (bounded)

**In-flight identity/deadline is carried from the completed worker attempt into
post-`RUNNING` phases, producing a false `E_OVERDUE_ACTION` during normal
`CHECKING`.**

`lifecycle.apply` sets `flight` on `start` and never clears or rotates it when
the attempt completes at `publish` (`src/lifecycle.py:199–209`); `store.append`
records `flight` only on a `start` event (`src/store.py:142–146`) and
`publish_snapshot` emits it for any non-terminal phase (`src/store.py:256–264`).
So a package in `CHECKING` is projected as an in-flight action whose
`action_id`/`owner`/`deadline` are the **worker's completed** attempt, not the
pending verification pass. Reproduced: start deadline `17:10Z`, publish at
`17:05Z` (on time), `validate` at `17:15Z` returns
`INVALID E_OVERDUE_ACTION` with `in_flight = {phase:"CHECKING",
action_id:<worker-start>, deadline:"17:10Z"}`. In v1 this case validated
`ACTIVE` (no deadline was emitted), so the D2 change regressed it: a validator
invoked during a legitimate in-`CHECKING` window — exactly what startup/recovery
and the backstop do — would alarm `INVALID`/overdue and wake Tern falsely. The
current bounded action in `CHECKING` is the verification pass, which has its own
deadline; that action is never recorded.

**Required correction:** stop carrying the completed attempt's `flight` past
`RUNNING`. On `publish` (attempt end), clear the attempt flight and either
record the verification action/`deadline` explicitly (per r2.1 "each
execution and verification activity also has a deadline") or emit no in-flight
deadline for `CHECKING` until a verification action is recorded, so only a
genuinely in-flight action is ever reported and no false overdue fault arises
in `CHECKING`/post-attempt `BLOCKED`.

## Previously-passing behaviors: still hold

- Base suite: **32 passed** in fresh `/tmp` state (was 26); fake clock, no
  sleeps; a passing count accepted only alongside the independent checks above.
- Tern omission reproduced as `INVALID E_MISSING_DISPOSITION` (via the
  documented legacy-last fixture path); held verdicts validate `ACTIVE`, never
  the omission fault.
- Legitimate rest returns `REST` with no action for all three rest kinds;
  `ACTION_DUE` fires exactly once per trigger id then `REST`; chain-live
  `ACTIVE`, two-successors `REST`.
- No live effects: `src/` contains no `subprocess`, `os.system`, `popen`,
  `signal`, `systemctl`, kill/stop or wake call; only comments mention them.
  The fake executor and caller-supplied `now` remain the only execution/clock
  paths.
- Stdlib-only (`sqlite3`, `json`, `os`, `argparse`, `unittest`); SQLite ledger
  with WAL; atomic snapshot (temp, fsync, `os.replace`) after commit; restart
  reconstruction; duplicate event delivery ignored; crash-after-durable-start
  reconciles the same action with executor run count 1 across a store reopen;
  acknowledged vs intended delivery distinct.
- `README.md`/`fixtures/schema.json` document the new allocations, `held`,
  full in-flight fields and error codes, consistent with the corrected behavior
  except that they do not disclose the stale-flight projection over phases.

## Note

The four named defects are genuinely fixed. The single defect above is a
regression introduced by the D2 correction and is material because it makes the
validator alarm on a legitimate state.
