# P3-r2-ledger-authority — post-repair independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; pass deadline 2026-09-21T19:46:42Z
- **Authority:** admitted contract `9212426b…` @ `0b00ea3f`;
  `director-repair-decision.md` @ `1cdc217`; frozen P2 r2.1 `5bfbb071…`.
- **Supersedes** the initial PASS archived at
  `campaign4/p3r2-attempt-history/initial-director/verification.md` (preserved,
  unaltered; initial validator `src/validator.py 6ea9ba81…`, worker tree
  `85ce2c03…`).

## Verdict

**PASS.** All five supplied defect cases fail on the preserved initial and
fault deterministically on the repaired output; the unshared mutations I added
across the due-trigger/phase/duplicate/type families also fault; genuine
REST/ACTIVE/ACTION_DUE and all prior regressions hold. No crash and no
valid-verdict-on-malformed-value was observed. Resolution tightens authority,
never weakens it.

## Artifact hashes (recomputed on disk)

Repaired tree manifest (sorted per-file sha256 over `src/`, `tests/`,
`fixtures/`, `README.md`, `implementation-report.md`; 37 files):
`209040f25d8064027dec2f143e7cb8d414460077c83c491eb5711b0b9a3e3c88` — matches.

| Source | sha256 |
|---|---|
| `src/validator.py` (repaired) | `2e8f9e117db158bd455cec78fe1a83c902f01bcff4d62ac3656b6dc1c4222a47` |
| `src/validator.py` (preserved initial) | `6ea9ba8145fb704c6662168cbb4c948ef3791f897a8b8f73684ef058a5c1e157` |
| `src/store.py` | `96f0d9d82aebc428b6fa06c664694f93ed66303bf442715c3b2b0ef8c23ae58a` |
| `src/lifecycle.py` | `815b10c531fb3ffc77a67deeb91b7725b2ae9f6142f7cba5f6970be967997991` |
| `src/cli.py` | `c382d20017ff3713aeb7cf00e59b09ed161754410c52f8b42b5274ee8a8367e5` |
| `tests/test_repair.py` | `86d7486e188b6b2280bb8e29399e7b81f4f1df2beffb61939699de1d76f61fc5` |
| `tests/test_authority.py` | `a24fff360f34758da2927930ec24f68485f21e32e3676596d4db17de77e84f01` |
| `tests/test_lifecycle.py` / `test_validator.py` | unchanged from initial |
| `fixtures/*` | probes + fixtures unchanged except new repair fixtures |

Full suite: **54 passed** in fresh `/tmp` state; fake clock, no sleeps. A test
count alone is not acceptance.

## The five supplied cases (director-initial-check.json)

Independently rerun by importing the archived initial `src.validator` and the
repaired one:

| Case | Initial (preserved) | Repaired |
|---|---|---|
| `forged_due_disposition` | `ACTION_DUE` (forged-owner) | `INVALID E_MISMATCH` |
| `forged_phase` (RUNNING→CHECKING) | `ACTIVE` | `INVALID E_MISMATCH` |
| `duplicate_forged_flight` | `ACTIVE` | `INVALID E_DUPLICATE` |
| `malformed_package_id` (`[]`) | `TypeError` | `INVALID E_MALFORMED` |
| `timestamp_overflow` (`0001-01-01T…+01:00`) | `OverflowError` | `INVALID E_MALFORMED` |
| controls `genuine_rest` / `genuine_active` | `REST` / `ACTIVE` | `REST` / `ACTIVE` |

## Unshared mutations I added

- **Due-trigger bypass:** a genuine due `blocked` disposition for package A plus
  an inconsistent disposition for package B → `INVALID E_MISMATCH`, not
  `ACTION_DUE` — authority checks precede any valid outcome.
- **DECISION path:** held terminal + correct DECISION → `ACTIVE`; forged DECISION
  owner → `INVALID`; duplicate DECISION entry → `INVALID E_DUPLICATE`; wrong
  task id → `INVALID` (ledger-open task unprojected).
- **Handoff path:** duplicate handoff entries (one forged owner) →
  `INVALID E_DUPLICATE`.
- **Type/shape paths:** nested `blocker: []` → `INVALID E_INCOMPLETE_REST`;
  `revisit_at: "not-a-time"` → `INVALID E_MALFORMED`; deadline offset `+01` and
  `+99:99` → `INVALID E_MALFORMED`. No exception escaped.
- **Genuine controls:** `ACTION_DUE` fires once for a genuine due trigger, then
  `REST` when the trigger id is reported fired; genuine `ACTIVE` preserved.

## Regressions still correct

- **v2→v3 flight regression:** CHECKING projects the verifier action → `ACTIVE`;
  verifier expiry → `E_OVERDUE_ACTION`.
- **Bounded handoff** (`owner:duty`, bounded deadline) → `ACTIVE`; `record_terminal`
  atomic close → `REST`.
- Genuine rest (all three kinds), chains ending in rest, omission → INVALID,
  store-derived and reopened snapshots, atomic publication/restart, budget
  enforcement, no-duplicate dispatch, and the v2→v3 cases are exercised by the
  54-test suite and my store-derived runs.
- **No live effects / stdlib only:** `src/` contains no
  `subprocess`/`os.system`/`popen`/`signal`/`systemctl`/kill call; imports are
  `json`, `os`, `sqlite3`, `argparse`, `datetime`, `re`, `sys` plus local
  modules.

## Note

The initial PASS is retained as evidence, not acceptance, and its archive was
left untouched. The repair resolves all three defect families without relaxing
validation; ready for Tern's next boundary decision.
