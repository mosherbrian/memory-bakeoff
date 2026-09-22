# P6-r11 — routing negatives verification (wrong-execution + forged-route CLI)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-routing-negatives-1`, start `19:27Z`, deadline `19:47Z`
- **Release:** `routing-negatives-release.md` @ `7dffaac`; candidate immutable at
  `e0847de`.
- **Candidate hashes before/after:** `case_entry.py` `2326e6b89740…`,
  `turn_handoff.py` `2b6aa7efe8af…`, `harness.py` `d7b4e517…`,
  `composition-manifest.json` `44d119fb…` (unchanged by this review).
- **Scope:** private forged-claim producer fixture only; no candidate edit, no
  signature/identity relaxation, no live effect.

## Verdict

**INCOMPLETE (bounded).** Both malformed verifier claims genuinely reached
production claim ingestion, and neither became `verified-rejection` /
`COMPLETE` / `terminal-rest`: the worker handoff was preserved, there was no
duplicate dispatch, and no forged evidence was accepted. **But** the surfaced
CLI outcome is `E_NO_LATENCY` for both, not the expected authority/routing
failure or bounded owned recovery — the harness's routing error is swallowed and
masked by the entrypoint. The security property holds; the required *shown
failure mode* is not met.

## Fixture and method

- Real bound worker: the **original** `candidate/src/seat_emulator.py` (its hash
  remains signature-bound and unchanged); only the verifier process is a private
  external producer fixture (`candidate-review-routing-negatives-evidence/
  forged_seat.py`) that, after the genuine worker handoff, publishes one
  malformed verifier claim and one end record before the runtime end is
  consumed. Signature still binds the real seat hash; no signed tool was edited.
- Injected only; no production sockets/timers/services.

## Results

| case | forged claim | reaches ingestion | `verified-rejection`? | terminal/COMPLETE? | surfaced rc/outcome |
|---|---|---|---|---|---|
| forged-route | `route:"attacker"` added | yes (consumed) | **no** (no `verified-rejection:*` key) | **no** | rc3 `E_NO_LATENCY "candidate latency rows missing"` |
| wrong-execution | `execution:"exv-WRONGEXECUTION"` | yes (consumed) | **no** | **no** | rc3 `E_NO_LATENCY "candidate latency rows missing"` |

Both runs: `handoff-done:p6c-h3w:<ex>` present (legitimate worker handoff
preserved), `msg-counter = 2` (exactly one worker + one verifier dispatch, no
duplicate), forged verifier claim on disk verbatim, no `verified-rejection:` key,
no `latency.jsonl` written.

## Bounded defect (masked authority failure)

`run_handoff` raises the authority/routing error (`E_FORGED_ROUTE` for the
`route` field; `E_CLAIM_MISMATCH`/`E_STALE_TURN` for the wrong execution) as an
`OwnedFault` before any rejection can persist — consistent with "never trust a
forged claim". However the harness process returns rc3 with an error decision
that the `failed-verification` branch in `case_entry.py` does not surface; the
branch then falls through to the timing gate, which raises `E_NO_LATENCY`
because no latency rows were written. So at the production `run-case` boundary
the negative presents as a missing-evidence fault, not as the routing rejection.
This is a reporting/handling gap in the entrypoint's error propagation for
malformed-claim cases, not acceptance of forged evidence and not a
`verified-rejection`.

## Exact unresolved question

Does the entrypoint propagate a harness authority/routing error decision
(rc3 error dict) instead of continuing to the timing gate, so the CLI shows
`E_FORGED_ROUTE` / `E_CLAIM_MISMATCH` (or an explicit bounded owned recovery)
for a malformed verifier claim? Reproducer and logs:
`candidate-review-routing-negatives-evidence/` (`forged_seat.py`,
`run_neg.py`, `forge-route.log`, `forge-wrongexec.log`).

## Preserved

- Checks 1–3 and wrong-incarnation PASS from `candidate-review-closeout.md`
  (`687a811f…`) stand; legitimate rejection behavior unchanged (no verified
  rejection was produced or suppressed for valid claims).
- No candidate/source write; hashes before == after.

## Effect

One bounded verdict: **INCOMPLETE** — forged claims are correctly refused
ingestion as rejections and never accepted, but the expected routing failure is
masked as `E_NO_LATENCY` at the CLI boundary. Returned to Tern; no automatic
repair or repeat grant.
