# P6-r10-live-recovery-matrix — live failed-verification review (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r10-failed-review-1`, deadline 10m from wake
  (`campaign4-p6r10-failedreview-deadline.timer` → 17:22:36Z)
- **Grant:** `live-failed-1-release.json` (Tern `stagec-task`, signed
  `17:09:32Z`, valid until `17:17:00Z`)
- **Evidence:** `live-failed-1/`, `live-failed-1-disposition.md`,
  `live-execution-failed-1/`, `/tmp/p6r10-live-failed-1/`
- **Scope:** read-only chronology / source path / claim presence / expiry-vs-
  premature / quiet-rest structure. No retry, no send, no source edit.

## Disposition (one)

**INCOMPLETE — honest owned failure, not a PASS.** The run exited
`E_NO_ONSET` after a **premature 8 s observation exit while 172 s of the signed
worker grant and the 17:17 stop remained**, not after grant expiry. The real
worker then completed at **17:10:55Z (~19 s after delivery)** — after the tool
had already returned — so `corrupt-after-worker` never fired
(`artifact_control: null`), the verifier was never dispatched (`sends 1/0`),
and no corruption was evidenced. Root cause is a bounded **composition defect**:
the grant-preserving reattach exists only in the `positive-handoff` branch;
`failed-verification` (and `quiet-rest`) require the first run to commit but
have no reattach. Smallest demonstrated correction: route
`failed-verification` and `quiet-rest` through the same
`_grant_remaining_s`-bounded reattach that `positive-handoff` already uses
before their checks. No retry under this grant.

## Checks

- **Chronology:** arm `17:10:24Z` (`corrupt-after-worker`, `induced: true`) →
  worker delivered `17:10:28Z` (`started`) → applied receipt written
  `17:10:36.6Z` → `run.out` `E_NO_ONSET`; late worker claim written
  `17:10:55.8Z` (~19 s post-delivery). Gate PASS was minted before arm; run was
  single. All within `start_not_after 17:11:00Z`.
- **Source path (confirmed):** `case_entry.py` `positive-handoff` alone takes
  the reattach branch on `decision != committed` with
  `reason == "no-end"` and `_grant_remaining_s(...) > 0`
  (`case_entry.py:1128-1172`); `lost-completion` has its own reattach
  (`:1173-1211`). `failed-verification` (`:1212-1216`) only forbids any
  `COMPLETE` and then falls through to the fault-case onset/timecheck path —
  no reattach. On a first-run `owned-failure/no-end` it therefore cannot reach
  its intended corrupted-artifact rejection.
- **Claim presence:** at run exit `claims/` and `art/` were empty; the worker
  claim `ex-bb8f65c1bd5f.json` (`outcome: completed`, `out.bin` sha256
  `c16a40a4…`) and `art/out.bin` exist only in `/tmp/p6r10-live-failed-1/`
  and were written after the run returned. The package archive
  `live-failed-1/failed-verification/{claims,art}/` is **empty**: cairn must
  archive the late bytes before the automatic `17:18:56Z` cleanup, and they
  stay late evidence only, never a new observer run or backdated success.
- **Expiry vs premature:** grant `duration_s 180`, `wait_s 8`, `stop_by
  17:17:00Z`. Exit at ~8 s (17:10:36) is **premature observation truncation**,
  not expiry: the observed worker end arrived at 17:10:55, squarely inside the
  grant. `E_NO_ONSET` is the downstream consequence (fault case with no
  independent onset), not the primary cause.
- **Effect absence:** `faults/failed-verification.applied.json`
  `artifact_control: null`, one delivery (worker), `transport_states
  {"msg:msg-p6c-h3w-1":"sent"}`, `committed_actions []`, `latency.jsonl` a
  single zero-signal `no-end-failure` row. No corruption applied, no verifier
  send; the release's expected "independent rejection of tampered artifact"
  was never reached.
- **Quiet-rest structure:** `quiet-rest` (`:1268-1295`) likewise requires
  `out.decision in ("transition-committed","terminal-rest")` for the setup run
  and has **no** grant-preserving reattach, so it shares the same limitation —
  an 8 s slice will fail its setup commit for any worker slower than 8 s. It
  should not be released as executable until the same correction lands.
- **Pins/hashes:** signatures `91be794b…`, config `02146996…`, plan
  `f71e598b…` recompute equal to `live-failed-1-release.json`; binding
  `dca68487…`; `case_entry.py` `9a1bb23c…` and `fixture_control.py`
  `f89b03fd…` unchanged; composition manifest rehashed **29/29 clean**.
  `simulated: false`, `induced: true`, no emulator path in the live procedure.
- **Cleanup/exit:** automatic `campaign4-p6r10-failed-prep1-cleanup.timer`
  still armed (`~17:18:56Z`); `p6-stagec-h3.timer` backstop still armed.
  No explicit process exit code archived (release condition 3); `run.out`
  records the `E_NO_ONSET` error only. Never reconstruct a missing rc.

## Effect

`P6r10-live-failed-1` is **INCOMPLETE**: real seats, real worker completion,
but the case's own rejected-completion property was not exercised because a
fault case without the `positive-handoff` reattach exits on the 8 s slice and
then fails onset. Smallest correction is bounded and local (extend the
existing reattach to `failed-verification` and `quiet-rest`); no test/live
retry, no source edit here. Late claim/artifact must be archived before
cleanup. Returned to Tern.
