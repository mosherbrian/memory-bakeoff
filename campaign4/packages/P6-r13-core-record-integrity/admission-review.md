# P6-r13-core-record-integrity — admission review (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r13-admission-1`, start `20:43Z`, deadline `20:58Z`
- **Brief:** `P6-r13-core-record-integrity/package.md` sha256
  `e56ab4ea8c67…` @ `9fd2497`
- **Scope:** read-only admission + pinned executable cases. No source, no
  candidate, no live effect.

## Verdict

**ACCEPTED (bounded).** The contract is the already-authorized first integrity
repair in the disposition order, all pins resolve, the authorized surface is
exactly `store.py`, `lifecycle.py`, `ingress.py` in a local manifest-bound R11
copy, and the required semantics are implementable while retaining stdlib core
and the public trusted-ingress boundary. Two bounded obligations are pinned:
(a) cases A–D must be run against the **actual R11 baseline bytes**, not only
P5-r2 (R11 `ingress.py 4d12429f` differs from P5-r2 `c9327f85`, but still
contains the `grant_ref` strip and adds `HostClock.now`); (b) falsification of
`record_terminal`'s transaction must be genuine, not a setUp failure. Conditional
kiln release follows only after this admission and the pinned cases.

## Pin resolution (all resolve)

- Diagnostic matrix + R12 acceptance commit `bccd688d0b64…`; matrix
  `campaign4/code-review-regressions/matrix.md` sha256 `3d160ecf…` (9 reproduced,
  #5 untested); probes `code-review-regressions/probes/probe_core.py`.
- Input review `c464709`; disposition `abb0f90`; this package `9fd2497`.
- R11 accepted source `924d21a`, acceptance `5eaa055`, final 42-gate
  `da3ddf79f572` (`candidate-review-routing-repair.md`); candidate dir
  `../P6-r11-case-observer-continuation/candidate/`.
- Original core `P5-r2 80092f92…` (`store.py dafaeb33`, `ingress.py c9327f85`,
  `lifecycle.py 7ebaf466`) + its 83 tests; `P3-r3 d27d5be` core + 59 tests
  (`packages/P3-r3-authoritative-claims/tests`).
- R11 copy bytes: `store.py dafaeb33` = P5-r2 (identical), `lifecycle.py
  7ebaf466` = P5-r2 (identical), `ingress.py 4d12429f` ≠ P5-r2 `c9327f85`.
  `HostClock.now` present at `ingress.py:139-146`; `_ATOMIC_FORMS`/`grant_ref`
  strip present at `:454,468`. So #2/#6/#10 target identical bytes; #7/#5 must
  be reproduced on the R11 ingress.

## Pinned executable cases (contract requirements, not code-fitted)

Run `probe_core.py` on immutable P5-r2 originals **and** the R11 baseline; record
module `__file__`/hashes in-test to prove which bytes ran. Public reachability
via `Driver`/`ingress` with trusted actors; internal-API checks labelled
internal. No authority bypass.

**A (#2) — projection consistency under rollback.**
- A1 pair-duplicate: build CHECKING; `store.record_terminal(verdict, decide)`
  where `decide.event_id` is already committed → `E_DUP_EVENT`; assert zero new
  rows, `verdict_id ∉ seen_events` (no phantom), lifecycle unchanged.
- A2 existing-event collision (duplicate within the pair / first element) →
  same invariants.
- A3 transaction failure injection: force the second `_insert` to fail; assert
  full rollback of rows and projections.
- Old-fails: phantom id retained, same-store retry raises `E_DUP_EVENT`, verdict
  never persists. New-passes: retry **same store** with a fresh valid decide
  persists exactly once; reopened store agrees; prior committed IDs still dedupe;
  valid atomic verdict+disposition remains one transaction.

**B (#6) — first disposition immutable.**
- Apply/ingress a valid terminal DECIDE, then a distinct later DECIDE → reject
  with a deterministic error and **zero** state/row change (through ingress and
  replay/reopen); exact same committed event replay is idempotent (not error,
  not overwrite); AMEND behavior unchanged and not co-opted.
- Old-fails: second decides overwrites (`first → second`); new-passes: preserved.

**C (#7) — exact atomic shapes.**
- `decide + grant_ref` rejects before any row/cache/state mutation; valid
  `hold + authorized grant` and valid `decide` still commit with trusted
  stamping/attribution; mixed, unknown and malformed payloads fail closed; every
  supported atomic form covered (not only the supplied specimen); no silently
  discarded fields.
- Old-fails: `decide+grant_ref` accepted, grant dropped; new-passes: rejected.

**D (#10) — instant-based deadline ordering.**
- Just-before / equal / after the boundary; UTC offsets (`+02:00`) and
  fractional seconds; equivalent encodings make equivalent decisions;
  naive/malformed values reject deterministically (never crash, never string
  compare). Exercise through an accepted ingress grant → execution → publish,
  plus a low-level invariant; reopened behavior identical; no clock/skew policy
  change, no host-adapter import into core.
- Old-fails: `+02:00` deadline accepted 30 min past the instant; new-passes:
  rejected per instant rule.

**E (#5) — unresolved, classify truthfully.**
- Public atomic event/phase matrix incl. `accept`-on-COMPLETE and other alleged
  non-terminal-maker + decide/hold combinations. A supplied atomic op is wholly
  applied or deterministically rejected before mutation — never accept-and-drop.
- Expected: the original `accept` path rejects `E_TERMINAL` → record **NOT
  REPRODUCED**, not a weakened guard. If another reachable silent-drop
  reproduces, fix within the three authorized modules with old-fails/new-passes;
  otherwise deliver the evidence and mark remaining uncertainty precisely. No
  speculative new accept-on-terminal semantics.

## Gate and outputs (blocking)

- Retained P5-r2 83 + P3-r3 59 core tests adapted to run against the NEW core
  (with recorded module paths/hashes; no accidental PYTHONPATH/import-cache
  substitution), plus the R11 42-case candidate gate on NEW composed bytes and
  the new regressions; known ~14m suite + fast core. Any semantic conflict with
  an old assertion returns Tern — no silent skip/delete.
- Concrete old-fails/new-passes for A–D; independent corvid mutation per family
  not supplied by kiln; E classified.
- Manifest/copy descriptors accurate, no self-hash; parent paths/hashes
  recorded; source-change table and limits; claim binds exact final bytes and
  results; unresolved failures/timeouts named; complete command + rc recorded,
  no retry-until-green.
- Source stays local/stdlib; R11 rejection/routing/observer behavior and public
  ingress protections hold. Host-only issues #1/#3/#4/#8/#9 are **not** fixed or
  certified here; the live-release hold persists.

## Bounds

ONE corvid admission+case-pinning ≤15 m (this); conditional ONE kiln ≤45 m, ONE
independent corvid ≤30 m on its own clock. Ceilings `1025worker/765verifier` →
`1070worker/795verifier`. Prior unused R12 diagnostic time cancelled, not
transferred; prior spent allocation preserved. Candidate-only, zero
live/preparation. Expiry/FAIL/INCOMPLETE returns Tern with partial bytes; no
clock reset.

## Effect

Admission **ACCEPTED (bounded)** with the pinned cases and obligations (a)/(b).
No implementation or release is conferred. Returned to cairn/Tern.
