# P6-r13 — pinned executable cases

Pinned by corvid-dsh at `P6r13-admission-1`. Brief pin `e56ab4ea8c67…` @
`9fd2497`; R12 matrix `3d160ecf…` @ `bccd688d`; R11 accepted `924d21a` /
`5eaa055` / 42-gate `da3ddf79…`; P5-r2 `80092f92` (`store dafaeb33`,
`ingress c9327f85`, `lifecycle 7ebaf466`) + 83 tests; P3-r3 `d27d5be` + 59
tests. Authorized surface: local R11 copy of `r3harness/{store,lifecycle,
ingress}.py` only. `ingress.py` R11 `4d12429f` differs from P5-r2; preserve
`HostClock.now`. Run every case on P5-r2 originals **and** the actual R11
baseline; record module `__file__`+hashes in-test. Public path via
`Driver`/`ingress` with trusted actors; label internal checks.

## A (#2) projection consistency under rollback
- A1 pair-duplicate: `record_terminal(verdict, decide)` with an already-committed
  `decide.event_id` → `E_DUP_EVENT`; assert 0 new rows, `verdict_id` absent from
  `seen_events`, lifecycle unchanged.
- A2 existing-event collision (duplicate first/within pair) → same invariants.
- A3 injected transaction failure on the second insert → full row+projection
  rollback.
- Old-fails: phantom seen id; same-store retry raises `E_DUP_EVENT`; verdict
  never persists. New-passes: same-store retry with fresh valid decide persists
  exactly once; reopened agrees; prior committed IDs still dedupe; valid atomic
  verdict+disposition stays one transaction.

## B (#6) first disposition immutable
- Valid terminal DECIDE then a distinct later DECIDE → deterministic rejection,
  zero state/row change (ingress and replay/reopen); exact same committed event
  replay idempotent; AMEND unchanged.
- Old-fails: `first → second` overwrite. New-passes: preserved/rejected.

## C (#7) exact atomic shapes
- `decide+grant_ref` rejects before mutation; valid `hold+authorized grant` and
  valid `decide` commit with trusted stamping; mixed/unknown/malformed fail
  closed; every supported atomic form covered; no silently discarded fields.
- Old-fails: accepted, grant dropped. New-passes: rejected.

## D (#10) instant-based deadline ordering
- Just-before/equal/after; UTC offsets and fractional seconds; equivalent
  encodings equal decisions; naive/malformed reject deterministically. Exercise
  through accepted ingress grant → execution → publish plus low-level invariant;
  reopened identical; no clock/skew policy change or host-adapter import.
- Old-fails: `+02:00` deadline accepted past the instant. New-passes: rejected.

## E (#5) unresolved atomic/phase matrix
- `accept`-on-COMPLETE and other non-terminal-maker + decide/hold combinations:
  wholly applied or deterministically rejected, never accept-and-drop. Expected
  `accept` path rejects `E_TERMINAL` → **NOT REPRODUCED** (do not weaken the
  guard). Any other reachable silent-drop → fix in the three modules with
  old-fails/new-passes; else evidence + precise uncertainty. No new
  accept-on-terminal semantics.

## Gate / outputs
- P5-r2 83 + P3-r3 59 core tests adapted to the new core (module paths/hashes
  recorded; no PYTHONPATH/import-cache substitution); R11 42-case gate on new
  composed bytes + new regressions; ~14m host suite retained.
- Manifest/copy descriptors accurate, no self-hash; parent hashes recorded;
  source-change table + limits; claim binds final bytes/results, names
  unresolved/timeouts; complete command + rc; no retry-until-green.
- Host-only #1/#3/#4/#8/#9 not fixed/certified; live-release hold persists.
- Bounds: ONE kiln ≤45 m, ONE corvid ≤30 m; ceilings 1070/795; candidate-only,
  zero live/prep; expiry returns Tern with partial bytes.
