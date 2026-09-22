# P6-r11-case-observer-continuation — admission review (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-admission-1`, start `2026-09-22T17:20Z`, deadline
  `2026-09-22T17:30Z` (`campaign4-p6r11-admission-deadline.timer`)
- **Brief:** `P6-r11-case-observer-continuation/package.md` sha256
  `a966c15176c7c2089c74ef952dd4233f3b01fd291243e333ce06568970e7344e`
- **Scope:** independent admission + pinned checklist; read-only, no edits to
  the brief or parent, no implementation, no launch/send.

## Verdict

**ACCEPTED (bounded).** All named pins resolve, the evidence base is real, and
the minimal change directly targets the demonstrated r10 composition defect
(observer truncation in `failed-verification`/`quiet-rest`) with a change
confined to `case_entry.py`; the harness/host_adapter/core copies stay
byte-identical. The five blocking checks, the test-first baseline reproduction
requirement, and the stdlib/candidate-only bounds are sufficient and are pinned
below. R10 cleanup is independently confirmed complete before this starts, so
there is no race. Admission confers no candidate or live release; Tern releases
kiln only after the baseline acceptance cases are pinned and the unchanged
contract is ACCEPTED.

## Pin resolution

- **R10 terminal:** commit `5826c330` ("Close incomplete r10 matrix and preserve
  late evidence without retroactive success") resolves; `terminal-disposition.json`
  (state `EXHAUSTED`, matrix failed-verification INCOMPLETE, quiet-rest /
  lost-completion / queued-ambiguous-restart NOT_EXECUTED) is present.
- **Prior findings:** `live-review-failed-1.md` sha256 `ebb6ff9d4f77…` and
  `control-feasibility-review.md` sha256 `04b6501f26bf…` match the brief's pins.
- **Source baseline:** commit `f1d7c86`; `composition-manifest.json` sha256
  `161afac5…` (29 entries); on disk `case_entry.py` `9a1bb23c…`,
  `r3harness/harness.py` `d7b4e517…`, `r3harness/host_adapter.py` `231f45f0…`
  — all recomputed equal.
- **Candidate gate:** `candidate-review-verification-completion.md` sha256
  `77d5b03ec040…` = the 34-test full gate pinned in `0252499`/`ea94d16`; live
  positive `live-review-3.md` `89f28ccb…` in `0a77303`.
- **Governing:** `4be99bf` recovery, `84f094e` identity, `883107e` turn,
  `650830c` clock, `b2384d7` retirement, `7abab5f` portability,
  `58704e9` LIVE-AUTHORITY — all resolve.
- **Retained r9 inputs:** `amendment-2-host-timer.md`,
  `amendment-2-admission-review.md`, `amendment-2-checklist.md`,
  `repair-3-authorization.md` present (timer authority/reconcile/two-DB
  callback requirements carried).
- **R10 cleanup (no race):** `live-failed-1-late-evidence/` archive-receipt
  (`17:18:03Z`, claims/art/onsets hashes, evidence-only meaning) filed; the two
  r10f1 IDs are **ABSENT** from the live registry and no `p6-stagec`/`p6r10`
  timers remain. Only the r11 admission timer is armed.

## Accepted correction to the r10 review (carried, not hidden)

The brief correctly notes the r10 review's "~19 s post-delivery" is a mislabel:
`17:10:55.8Z` is **19 s after the observer exit (`17:10:36.6Z`)** and
**27 s after delivery (`17:10:28Z`)**. The substantive r10 finding is unchanged
(premature 8 s exit while the 180 s grant was live; worker completed late;
tamper/verifier never exercised). Admission accepts the brief's chronology.

## Bounded note (risk already bound by a check, not a rejection)

`failed-verification` requires the post-commit tamper to land **after** the
worker handoff durably commits and **before** the verifier's recompute. A shared
reattach must therefore still allow the deliver loop to observe the late commit
and apply `corrupt-after-worker` ahead of the verifier dispatch. Blocking check 2
binds this ("actual post-commit before-verifier tamper with distinct hashes,
verifier rejection"), so it is an implementation obligation for kiln, not an
admission defect. No change is authorized to `harness.py`/`host_adapter.py`
without concrete evidence returned to Tern first.

## Pinned checklist

Every item is required; a skipped failure, repeated-until-green run, unreported
timeout, or rc-only claim is a FAIL. Corvid tests/reviews on frozen final bytes.

1. **Baseline reproduction first (pre-implementation).** Corvid pins exact CLI
   acceptance cases that reproduce BOTH branches on the immutable baseline with
   **worker > 8 s and verifier > 8 s**, using intercepted external collaborators
   on the real production paths (no `--simulated`), demonstrating the original
   8 s truncation while the valid grant had not expired. Worker fixes must not
   silently edit these expectations.
2. **Failed-verification after repair.** Delayed worker AND delayed verifier
   produce durable handoff; actual post-commit *before-verifier* tamper with
   distinct before/after hashes; real verifier rejection; `accept-open` / never
   `COMPLETE`; exactly one worker and one verifier send. Require
   artifact/claim/ledger evidence, not final rc; an `induced:true` label alone
   is not proof. Preserve real-case onset requirement; no fake clock. Missing
   onset or unapplied corruption stays INCOMPLETE.
3. **Quiet-rest after repair.** Delayed setup genuinely completes; observation
   and reopen yield `duplicate-end-ignored`, no new dispatch, no false alarm.
   Reopen tested in worker and verifier phases; original deadlines preserved;
   grant expiry and stricter outer stop return bounded failure/INCOMPLETE, never
   a fresh interval or task; one-shot callback cannot duplicate.
4. **Full gate retained.** The retained 34-test gate plus new cases, on the same
   changed entrypoint, remains green; positive slow-turn and the timer
   canonicalization / reconcile / two-DB callback guarantees retained. Corvid
   adds an unshared delayed/expiry case and checks the whole gate on frozen
   final bytes.
5. **Manifest/provenance.** Complete manifest (29 inherited entries + declared
   new files), no stale R3 copy hashes and no self-hash; original provenance
   preserved; mechanical hash refresh only; no fabricated receipt or successful
   late timing. Exact diff, candidate plan, and proposed live commands for the
   two cases described without signatures or fresh prep. Code stays stdlib.
6. **Bounds.** ONE kiln ≤ 40 m and ONE corvid ≤ 30 m; ceilings
   `925worker/670verifier`; actual test runtime must fit or it is honest
   INCOMPLETE; no repair grant, no automatic extension, no deadline reset. R10
   unused grants cancelled and not transferred. Corvid's implementation pass
   gets its own host-stamped start/deadline; at expiry stop/preserve and return
   Tern; no implementation by the verifier.
7. **Scope.** Candidate-only; no fixture launch, host timer/service, live send,
   research/shadow/adoption/retirement, multi-project/scope expansion, main-seat
   reset, shared wrapper/credential or live-service change. The two missing
   controls (lost-completion, queued/ambiguous) remain blocked and OUT. R10
   matrix stays incomplete; earlier positive witness unchanged.

## Effect

Admission **ACCEPTED** with the pinned checklist and the two bounded notes
(r10 chronology correction; failed-verification tamper-ordering obligation).
No implementation or live release is conferred; Tern proceeds to conditionally
release kiln. Returned to cairn/Tern.
