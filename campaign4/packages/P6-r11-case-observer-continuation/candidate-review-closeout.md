# P6-r11 — closeout verification (metadata correction + unexecuted checks)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-closeout-1`, start `19:08Z`, deadline `19:28Z`
- **Release:** `closeout-verification-release.md` @ `e0847de`; correction
  `director-metadata-correction.json`; preserved base `346a17d`.
- **Scope:** read-only; private intercepted fixtures only. No live
  sockets/timers/services; no candidate/source write.

## Verdict

**INCOMPLETE (bounded).** Checks 1–3 pass and the metadata correction is
verified byte-for-byte, but two of the four required CLI routing negatives
(wrong execution, forged route) could **not** be executed end-to-end within the
bound. They remain explicitly unresolved; acceptance is therefore withheld
pending those two CLI negatives. The prior 38-test PASS-substance is carried by
its explicit pin, not re-run (metadata-only change).

## Check 1 — metadata correction (PASS)

- Compared all 34 candidate files against `346a17d`: **only**
  `candidate/composition-manifest.json` and
  `candidate/src/r3harness/R3_REVISION.json` changed — no executable
  source/test/plan change.
- `R3_REVISION.json`: `turn_handoff.py` now `identical:false`,
  `copy_sha256 2b6aa7ef…` matches the file, `parent_sha256 ecbec310…` matches
  `P6-r5-launch-binding/src/turn_handoff.py`; `harness.py`/`host_adapter.py`
  copy+parent hashes also match.
- `director-metadata-correction.json` binds `new_revision_sha256 81d6fe17…`
  and `new_manifest_sha256 44d119fb…`; both recomputed equal to the files.
- Manifest: 33 entries, **no self-entry**, every path exists with matching
  sha256, `bound_from director-metadata-correction.json`, `baseline 05eba448`.
- Correction is semantic-flag + rebinding only; `source_behavior: unchanged`
  is consistent with the byte comparison.

## Check 2 — QR-WV, expiry, outer stop (PASS)

Candidate-pointed CLI (`candidate/src/case_entry.py`, injected collaborators):

| check | rc | result |
|---|---|---|
| QR-WV (worker 18 s, verifier 18 s) | 0 | `timecheck accept`, sends 1+1, `duplicate-end-ignored`/`terminal-rest` |
| FV grant-expiry (grant 15 s, worker 40 s) | 3 | `E_CASE_FAIL` bounded, **no** accept verdict |
| QR grant-expiry (grant 15 s, worker 40 s) | 3 | `E_CASE_FAIL` bounded, **no** accept verdict |
| FV stricter outer stop (`live_stop_utc` +12 s, worker 25 s) | 3 | `E_CASE_FAIL` bounded, no silent renewed grant |

No early normal truncation and no silent grant renewal observed.

## Check 3 — authenticated-rejection replay/reopen (PASS)

- FV-W first run: rc0 `accept-open`, `verified-rejection` with `expected`
  `46409ea6…` (committed worker hash) and `observed` tampered; 1+1 sends.
- Reopen at the **production reattach CLI boundary** (global options before the
  `reattach` subcommand), same action/execution: rc0
  `{"decision":"duplicate-end-ignored","durable":true,"latency_samples":0}`;
  `msg-counter` unchanged at 2; `verified-rejection:p6c-h3v:exv-…` key still
  present. No duplicate send, no second verdict effect, no repeated escalation.
- Observation: re-running the full `run-case` on the completed suite raises
  `E_APPLY "tamper had no effect"` (the fixture control re-applies
  `corrupt-after-worker` to already-tampered bytes) — a fixture-control replay
  artifact, not a rejection-path defect; the correct reopen boundary
  (`reattach`) is idempotent and no duplicate send occurs. Noted, not waived.

## Check 4 — routing/identity negatives (PARTIAL)

- **Wrong incarnation at CLI: PASS.** Mutated binding `incarnation.ino`,
  re-derived/re-signed, `run-case` → rc3
  `{"error":"E_REBOUND","detail":"worker socket incarnation changed (rebound);
  re-witness required"}`.
- **Wrong execution at CLI: NOT EXECUTED.** `_authenticated_rejection` returns
  `None` for a wrong-execution claim (unit-level), and `validate_claim` is the
  authority gate, but the release requires end-to-end proof through the CLI
  ingestion path. No harness for a forged-execution verifier claim was
  available in-bound.
- **Forged route at CLI: NOT EXECUTED.** Attempted via a forged verifier seat
  emulator; the gate rejected the substituted seat
  (`E_TOOL_CHANGED "seat_emulator.py missing or drifted since signature"`)
  because `seat_emulator_sha256` is bound to the real file, and the corrected
  attempt exceeded the bound. `validate_claim` raises `E_FORGED_ROUTE` and
  `_authenticated_rejection` returns `None`, but that is unit-level only.

**Exact unresolved questions:** does a forged-route (routing field) verifier
claim at the real `run-case` CLI produce `E_FORGED_ROUTE`/owned recovery and
**never** `verified-rejection`, with intercepted external collaborators? Same
for a wrong-execution verifier claim (`E_STALE_TURN`/`E_CLAIM_MISMATCH`)? These
need a forged-claim seat fixture whose hash is either allowed by the signature
or injected below the gate (not a shared-wrapper edit).

## Carried evidence

- Prior independent rejection verification `candidate-review-rejection.md`
  (`c28bb9d5…`): FV-W/FV-WV accept-open 1+1, negatives (invented hash,
  completed mismatch, worker step, wrong execution, no-mismatch, forged route)
  return `None`, manifest bound, 38/38 gate in 841.88 s. Carried by pin; not
  re-run for the metadata-only change.
- Evidence bundle: `candidate-review-closeout-evidence/` (reproducers + logs).

## Effect

One bounded verdict: **INCOMPLETE** — metadata correction and the
QR-WV/expiry/outer-stop/replay/incarnation checks pass, but the wrong-execution
and forged-route negatives are not proven end-to-end. Returned to Tern; no
candidate edit, no live effect.
