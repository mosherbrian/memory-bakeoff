# P3-r2-ledger-authority — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; pass deadline 2026-09-21T19:30:18Z
- **Authority:** admitted contract `9212426b…` @ `0b00ea3f`; frozen P2 r2.1
  `5bfbb071…`.

## Verdict

**PASS.** The ledger-authority gap is closed, both supplied defects now fault
deterministically without weakening any earlier validation, all required
regressions hold, and no new defect was found. All checks were derived
independently from the pinned specification and run in fresh `/tmp` state; a
test count alone was not treated as acceptance.

## Artifact hashes (recomputed on disk)

Tree manifest (sorted per-file sha256 over `src/`, `tests/`, `fixtures/`,
`README.md`, `implementation-report.md`; 35 files):
`85ce2c03009ea1cdb2792834a53478b49f2f3987fc847586054218eeaec23e44` — matches.

| Source | sha256 |
|---|---|
| `src/validator.py` | `6ea9ba8145fb704c6662168cbb4c948ef3791f897a8b8f73684ef058a5c1e157` |
| `src/store.py` | `96f0d9d82aebc428b6fa06c664694f93ed66303bf442715c3b2b0ef8c23ae58a` |
| `src/lifecycle.py` | `815b10c531fb3ffc77a67deeb91b7725b2ae9f6142f7cba5f6970be967997991` (unchanged from v3) |
| `src/cli.py` | `c382d20017ff3713aeb7cf00e59b09ed161754410c52f8b42b5274ee8a8367e5` |
| `tests/test_authority.py` | `a24fff360f34758da2927930ec24f68485f21e32e3676596d4db17de77e84f01` |
| `tests/test_lifecycle.py` | `63dfde2f68790b2181f11a325d780e32f628b6f01fe9acfb0b3fb4265d29afba` |
| `tests/test_validator.py` | `85fee4c04813ef76942feed72999c0f2eab1dbcc9447e87c267965d367ad96f4` |
| `fixtures/director-probes.json` | `7f01ad2f585a14e5c7687bb907336deee92abd55ec6a8a405113f2fcb9054745` |
| `README.md` | `3a8812e304faf6b3e0ce956a4aff5be1c5c788fc7c45f446318dc88499df6c0e` |
| `implementation-report.md` | `e03192f2341e347ca721e3ff4a9f64e39e3da37b82d266c71322d7faf1322c73` |

## Supplied defect cases (director-probes.json)

Both are fixed. Run against r2 with the exact probe payloads:

- `active-inventory-omitted` → `INVALID E_LEDGER_INCOMPLETE` ("ledger-active
  work-r1 missing from projection"); v3 gave `REST`.
- `projection-invents-terminal-disposition` → `INVALID E_FABRICATED`
  ("terminal done-r1 disposition invented"); v3 gave `REST`.

## Independent unshared mutations (one per family)

Built a real store-derived snapshot (active `work-r1` RUNNING with an
acknowledged flight, plus a closed terminal `done-r1` with a
`question_answered` disposition), then mutated the projection:

| Family | Mutation | Observed |
|---|---|---|
| Inventory | drop active `work-r1` from `in_flight` | `INVALID E_LEDGER_INCOMPLETE` |
| Inventory | fabricate unknown `ghost-r1` in flight | `INVALID E_FABRICATED` |
| Disposition | change terminal `disposition.reason` | `INVALID E_MISMATCH` |
| Disposition | hide terminal disposition | `INVALID E_MISSING_DISPOSITION` |
| Action | forge flight `owner` | `INVALID E_MISMATCH` |
| Deadline | extend flight `deadline` | `INVALID E_MISMATCH` |
| Ack | downgrade `dispatch_receipt` | `INVALID E_MISMATCH` |

Unmutated baseline validates `ACTIVE`; ledger view exposes `receipt`, `flight`
and `handoff`, so the comparison is against authoritative facts, not projection
content. Full suite: **49 passed** in fresh `/tmp` state (40 carried + 9
authority), fake clock, no sleeps.

## Regressions still correct

- **v2→v3 flight regression:** CHECKING carries the verifier action
  (`vf`/corvid/19:20Z/acknowledged) → `ACTIVE` at 19:00Z; at 19:25Z →
  `E_OVERDUE_ACTION`.
- **Pending bounded handoff:** publication with `handoff_deadline` yields
  `owner:"duty"`, bounded deadline, `dispatch_receipt:None` → `ACTIVE`.
- **Genuine rest, chains ending in rest, `ACTION_DUE`, omission, verifier
  expiry:** exercised by the 49-test suite (`rest-answered`,
  `rest-blocked-parked`, `rest-budget`, `chain-live`/`chain-rest`,
  `trigger-due`, `omission` via the legacy path, `flight-rotate`).
- **Atomic publication/restart, budget enforcement, no-duplicate dispatch:**
  all pass in the suite; `record_terminal` remains the atomic close path.
- **UTC-instant timestamps:** `_instant()` parses/compares aware datetimes and
  rejects malformed/offset-invalid values (`E_MALFORMED`), not string order.
- **No live effects / stdlib only:** `src/` contains no
  `subprocess`/`os.system`/`popen`/`signal`/`systemctl`/kill/wake call (only
  comments/docstrings); imports are `json`, `os`, `sqlite3`, `argparse`,
  `datetime`, `re`, `sys` and package-local modules.

## Note

Both supplied defect cases are resolved by tightening validation (ledger
authority), not relaxing it; no earlier accepted regression was weakened.
Ready for Tern's acceptance.
