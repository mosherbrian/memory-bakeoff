# P3-r3-authoritative-claims — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; pass deadline 2026-09-21T20:06:39Z
- **Authority:** admitted contract `d6bb0260…` @ `7afd0752`; pinned r2 at
  `624dedcb…`; frozen P2 r2.1 `5bfbb071…`.

## Verdict

**PASS.** Both supplied authority failures reproduce false-valid on pinned r2 and
fault deterministically on r3; my unshared missing-fact and receipt-forgery
cases all fault; a genuine store-backed terminal decision is representable and
returns REST; all 54 prior regressions plus the five repaired probes are
retained. No crash and no silent REST/ACTIVE on malformed or forged input was
observed.

## Artifact hashes (recomputed on disk)

r3 tree manifest (sorted per-file sha256 over `src/`, `tests/`, `fixtures/`,
`README.md`, `implementation-report.md`; 39 files):
`07214e9c51fa5a590baed376089dad8949d6fa1963b09db2a9e30b99e17de091` — matches.

| Source | sha256 |
|---|---|
| `src/validator.py` | `dcecfc1d95a75c30a9ecca9a80df6418f930e03d4525fc2b5f38ab31997666c5` |
| `src/lifecycle.py` | `7ebaf466dd47e760b401fa0b1d8c2c2d8a1fd26549b0b91a0bfdbb47f498c03f` |
| `src/store.py` | `96f0d9d82aebc428b6fa06c664694f93ed66303bf442715c3b2b0ef8c23ae58a` |
| `tests/test_claims.py` | `5f7be3be263dc4ce0860ddcdfd5c30017741e65847dc1af7d652ae9933a25664` |
| `tests/test_repair.py` | `7449236162abb364f92273edb51acaeed31b110c3a933fa4d1cea8324c78fc5e` |
| pinned r2 `src/validator.py` @ `624dedcb` | `2e8f9e117db158bd455cec78fe1a83c902f01bcff4d62ac3656b6dc1c4222a47` (immutable) |

Full suite: **59 passed** in fresh `/tmp` state (54 carried + 5 claims); fake
clock, no sleeps. A test count alone is not acceptance.

## Supplied probes: r2 false-valid vs r3 INVALID

Run with the same payloads under fresh interpreters, importing the pinned r2
tree and the r3 tree:

| Case | Pinned r2 `624dedcb` | r3 |
|---|---|---|
| `invented_decision_reference` | `REST` | `INVALID E_MISMATCH` |
| `forged_handoff_ack_satisfies_successor` | `ACTIVE` | `INVALID E_MISMATCH` |

## Unshared missing-fact and receipt-forgery cases I added

Handoff / flight:

| Case | Result |
|---|---|
| handoff, ledger has no receipt, snapshot claims `acknowledged` | `INVALID E_MISMATCH` |
| handoff, ledger owner present, snapshot owner nulled | `INVALID E_MISMATCH` |
| handoff, ledger deadline present, snapshot deadline nulled | `INVALID E_MALFORMED` |
| flight, ledger receipt `intended`, snapshot claims `acknowledged` | `INVALID E_MISMATCH` |
| flight, ledger has no receipt key, snapshot claims `acknowledged` | `INVALID E_MISMATCH` |

DECISION:

| Case | Result |
|---|---|
| ledger task present, DECISION entry omitted | `INVALID E_MISSING_DISPOSITION` |
| DECISION entry `action_id` nulled | `INVALID E_LEDGER_INCOMPLETE` |
| DECISION forged `owner` | `INVALID E_LEDGER_INCOMPLETE` |

No exception escaped; all malformed/missing facts produce deterministic INVALID.

## Genuine representability and controls

- **Store-backed terminal decision:** admit → authorize → start → publish(verify)
  → atomic `record_terminal(verify_pass + decide question_answered)` yields a
  real store-derived snapshot validating **`REST`**; the same holds after
  closing and reopening the SQLite store.
- **Genuine `ACTION_DUE`:** a real due blocked trigger returns `ACTION_DUE`
  once; with the trigger id reported fired it returns `REST`.
- Five repaired probes (from the initial check) remain INVALID; genuine
  REST/ACTIVE preserved.

## Retained regressions

All 54 carried tests pass, covering true REST for all three kinds, historical
successor chains, verifier flight and expiry (`E_OVERDUE_ACTION`), bounded
handoff, atomic publication/restart, allocation ceilings (`E_ALLOC_EXCEEDED`,
`E_BAD_ALLOCATION`), no-duplicate execution, runtime-type/UTC checks, and the
v2→v3 flight transition. No live effects: `src/` contains no
`subprocess`/`os.system`/`popen`/`signal`/`systemctl`/kill call; imports are
`json`, `os`, `sqlite3`, `argparse`, `datetime`, `re`, `sys` plus local modules.

## Limitations and non-certifications

- Verification is against the pinned r2 and r3 source trees and the supplied
  probe payloads; I did not perform live adapter/watcher integration (out of
  contract scope).
- I certify only what I observed above; I make no claim beyond the executed
  cases. No new defect was found. Ready for Tern's acceptance.
