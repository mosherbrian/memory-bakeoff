# P6-r13 amendment-1 — admission (worker/verifier independence at ingress)

- **Reviewer:** corvid-dsh
- **Action:** `P6r13-amendment1-admission-1` (separate reader ≤10 m)
- **Brief:** `amendment-1-worker-verifier-independence.md` sha256
  `ecf50fc7bf85…`; finding #11 addendum `e48f3bd`.
- **Scope:** read-only admission + pinned cases. No source edit, no authorship.

## Verdict

**ACCEPTED (bounded).** Finding #11 is a real core-integrity blocker on the
same boundary the accepted R13 work touches, and the amendment's scope
(identity from trusted-ingress provenance + accepted publish/attempt ledger
events, not a caller-supplied `worker_seat`) is sound and confined to the
already-authorized `lifecycle.py`/`ingress.py`/`store.py`. Three bounded
obligations are pinned: **(a)** strict serialization — the original R13 attempt
must end and its bytes/claim be captured before amendment execution; **(b)** the
final amended bytes must actually run the **full** retained suites (P5-r2 83,
P3-r3 59, composed R11 42) plus the new cases — the initial claim left the slow
R11 tests "unresolved"; **(c)** public-path evidence only (no `Driver.verify`-
only test, no hand-seeded `worker_seat`) and no self-hash manifest.

## Pin resolution

- Finding #11 addendum commit `e48f3bd` ("finding 11, self-verify guard never
  fires"); original review `c464709`. Original core P5-r2 `80092f92`; R11
  baseline `924d21a`; R13 original admission `ad68796e…`/pinned-cases
  `6f4718d2…`.
- Initial R13 candidate captured: new bytes `ingress fe7f528d…`, `lifecycle
  5a41d291…`, `store b72d4fb3…`; claim `ex-p6r13-initial-1.json`
  (`COMPLETE-candidate`, A–D old-fails/new-passes, E NOT REPRODUCED). Preserve
  untouched; this amendment does not retro-claim #11.
- R11 `lifecycle.py:244/255` still compares `event.actor.seat ==
  state.worker_seat`, which no transition sets — guard never fires. Confirmed
  same class as #2/#5/#6 (silent).

## Pinned cases (#11 + retained)

Run old-fails on P5-r2 `80092f92` **and** the captured R13 initial candidate;
new-passes on the amended candidate. Record module `__file__`+hashes in-test.

**I. Author-is-not-verifier (public trusted ingress):**
1. Publish as a real producer via trusted ingress (e.g. `kiln`/worker), then
   `verify_pass` and `verify_fail` from the **same principal** (same seat,
   role relabelled verifier) → reject before any row/cache/state/atomic
   mutation. Old-fails: first reaches `COMPLETE`+disposition.
2. Same, with `atomic={hold}` / `atomic={decide}` on the rejected verdict →
   **zero** writes (no verdict row, no disposition, no cache), and identical
   after reopen/replay.
3. Role-swap and adversarial claimed `worker_seat` override must not defeat the
   rule; identity is the producing principal, not seat name / filename / role
   string / hardcoded kiln-corvid pair.
4. Missing/corrupt producer provenance: verdict cannot silently pass; recover
   only from authentic prior ledger events or fail closed with an owned explicit
   error.
5. Distinct legitimate verifier still reaches its correct state/disposition.

**II. Identity lifecycle:**
6. Repair attempt / new revision / new producer binds its own actual producer:
   new producer cannot verify its own work; an earlier producer is not forever
   barred from verifying unrelated later work solely by history.
7. Worker identity is preserved after its flight is cleared/replaced by the
   verifier flight; persist/replay/reopen reconstructs identity **without tests
   seeding `worker_seat`**.
8. Wrong revision/action references reject; no stale identity carries across.

**III. Constraints:** changes only in the three local modules + tests/docs/
manifests; `HostClock.now` and all A–E checks (atomic shapes, UTC instants,
immutable disposition, rollback) preserved; stdlib-only; no host-adapter/core API
bypass; no new general role-policy framework.

## Gate (blocking)

- Original A–E + these #11 cases on final frozen bytes; retained P5-r2 83 and
  P3-r3 59 core tests adapted to the **actual new local modules** and the
  composed R11 **42**-case gate; imports/hashes recorded (no accidental
  PYTHONPATH/import-cache substitution); no skipped failures; manifest
  descriptors accurate with no self-hash; provenance/claims updated
  mechanically.
- Independent corvid per-family mutations; a test that only asserts a function
  exists is no evidence. The initial attempt's "slow-or-hang, out of changed
  boundary" R11 items must be genuinely run or explicitly re-declared with a
  concrete blocker (not silently carried).

## Serialization / allocation

- Original attempt finishes through its original bound or FAIL; its output/claim
  pinned first, its timer retired and kiln idle before amendment execution.
  Never overlap; if original verification already began, let it finish, then
  start this admission. Cancel unused original verifier grant if undispatched and
  report it separately (no quiet reclaim).
- New: reader 10 m (this) + ONE kiln ≤30 m + ONE corvid ≤30 m; ceilings
  `1070worker/795verifier` → `1100worker/825verifier`; conditional Tern release
  only after unchanged amendment ACCEPTED and cases pinned; candidate-only, zero
  live/preparation; expiry/FAIL/INCOMPLETE returns Tern with partial bytes.

## Go conformance handoff

`~/projects/loop/conformance` is read-only external evidence/tooling: inspect
without editing, do not adopt recorded old Python behavior as an oracle. At
acceptance publish the full new source commit and behavior-change list
(#2/#6/#7/#10, #11; #5 truthful status) for Brian's independent Go re-recording.
A Go/Python disagreement is a finding, not automatic correctness. Live hold and
known host-timing findings unchanged.

## Effect

Admission **ACCEPTED (bounded)** with obligations (a)–(c). No implementation or
release conferred. Returned to cairn/Tern.
