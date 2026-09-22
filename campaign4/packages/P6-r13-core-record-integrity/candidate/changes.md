# P6-r13 changes (local R11 copy; injected effects only)

Parent: `../P6-r11-case-observer-continuation/candidate/src/r3harness/`
(`store dafaeb33`, `lifecycle 7ebaf466`, `ingress 4d12429f`).
`HostClock.now` preserved. No other production module touched.
- `store.py` (A/#2): `append` already published projections post-commit;
  `record_terminal` moved the `E_DUP_EVENT` pre-check before the transaction
  and publishes both ids only after commit. Rollback leaves zero new rows,
  no phantom seen ids, unchanged lifecycle; same-store retry with fresh
  decide persists exactly once; reopened store agrees.
- `lifecycle.py` (B/#6, D/#10): distinct later DECIDE on a decided revision
  rejects `E_ALREADY_DECIDED` before mutation (AMEND branch untouched; exact
  replay idempotent via store dedupe). New `_parse_instant` normalizes
  `Z`/offset/fraction encodings; deadline ordering compares instants with
  equal-not-expired boundary; naive/malformed now or deadline rejects
  `E_BAD_DEADLINE` (never crash, never string-compare).
- `ingress.py` (C/#7): `decide+grant_ref` rejects `E_BAD_ATOMIC` before any
  row/cache/state mutation; valid `hold+grant` and valid `decide` retain
  trusted stamping; mixed/unknown/malformed fail closed.

E (#5): matrix evidence shows `accept`-on-non-COMPLETE rejects
(`E_BAD_TRANSITION`/`E_TERMINAL`) and malformed atomics reject
(`E_MIXED_ATOMIC`/`E_BAD_ATOMIC`) — original accept-and-drop NOT REPRODUCED;
no new accept-on-terminal semantics added.

Limits: host-only #1/#3/#4/#8/#9 untouched; live-release hold persists;
stdlib-only; no dependency/clock-policy change.

## Amendment-1 (#11) worker/verifier independence — lifecycle.py only

- `new_revision` gains `producer_seat: None`. PUBLISH binds
  `st["producer_seat"]` from the trusted-ingress actor provenance of the
  actual artifact-producing event; caller `worker_seat` claims ignored.
  Repair re-publish rebinds; new revision starts None.
- New `_require_distinct_verifier`: VERIFY_PASS/FAIL reject `E_SELF_VERIFY`
  when verdict seat == bound producer (seat equality only — role relabel
  never defeats it); missing producer fails closed `E_UNKNOWN_PRODUCER`
  (replay of authentic ledger events re-runs PUBLISH, recovering it).
- Removes the dead `state.get("worker_seat")` comparison no transition set.
- store.py / ingress.py unchanged by this amendment (ingress already binds
  actors from trusted context and rejects claim actors).

## Metadata completion-2 (no production/test/plan change)

- composition-manifest.json: refreshed stale `lifecycle.py` (5a41d291… →
  ea61a75c…) and `changes.md` entries to disk bytes.
- manifest.json: removed impossible self-entry; `new_lifecycle` now
  ea61a75c… (amendment-1 bytes); consolidated redundant `amended_lifecycle`
  key; all file entries recomputed from disk in acyclic order.

## Completion-3 (descriptor + origin checks; production Python frozen)

- R3_REVISION.json: refreshed all copy_sha256 from disk (parent hashes
  retained); corrected false identical=true on ingress/store/lifecycle
  (copy != parent after R13 fixes). Only those three flags changed.
- test_r13_record_integrity.py / test_r13_identity_independence.py: origin
  assertions now canonical resolved-file equality (plus .pyc collapse);
  added alias/parent/lookalike negative-control test per file. No
  behavioral assertion changed.
