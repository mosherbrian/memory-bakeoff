# P6-r11 — completion-1 independent causal verification

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-verify-1` (existing unspent corvid ≤30 m grant), frozen at
  `05eba448bcec710c143fa707f328d9a5fd169d25`
- **Artifacts under review:** `candidate/` (entry
  `candidate/src/case_entry.py` sha256 `2504e07e38de…`), `completion-claims/
  ex-p6r11-completion-1.json` (INCOMPLETE preserved), `concrete-cases.md`
  (`db840dd7…`). No candidate byte, receipt or manifest edited by this review.
- **Evidence bundle:** `candidate-review-completion-1-evidence/` (reproducer,
  candidate-pointed test, raw claims, latency, deliveries, verifier stream).

## Verdict

**FAIL (bounded).** The candidate's change is confined to `case_entry.py`
(`harness.py` `d7b4e517…` and `host_adapter.py` `231f45f0…` unchanged), and the
QR-W continuation is a genuine scoped improvement. But **failed-verification is
not completed**: tracing the reattach shows a **genuine verifier rejection**
(verifier dispatched, produced an end, and wrote an honest `outcome:"failed"`
claim with `hash mismatch: out.bin`) that the harness misclassifies as
`owned-recovery E_ARTIFACT_MISMATCH`; the authorized `case_entry.py`-only scope
cannot repair it. The manifest self-hash defect and missing new-pass assertions
stand, and the full retained+new gate is UNRUN, so no PASS is possible.

## Reproducer (frozen candidate, injected only)

```
# candidate-pointed copy of the pinned cases (plan stays the immutable r9 plan)
cp concrete-cases/test_r11_failed_quiet.py /tmp/p6r11-cand-repro/test_cand.py
sed -i 's#P6-r9-observer-lifetime"#P6-r11-case-observer-continuation/candidate"#' ...
python3 /tmp/p6r11-cand-repro/repro.py     # FV-W then QR-W, prints rc/stdout/receipt
```

Exact copies: `candidate-review-completion-1-evidence/{repro.py,
candidate-pointed-test.py,cand-repro.log}`.

Actual results on frozen bytes:

- **QR-W candidate:** rc0, `timecheck accept`, `sends {worker:1,verifier:1}`,
  `committed_actions [p6c-h5v,p6c-h5w]`, `outcome.worker.decision terminal-rest`
  — scoped improvement confirmed on injected path.
- **FV-W candidate:** rc3
  `{"error":"E_CASE_FAIL","detail":"failed-verification reattach did not commit
  under valid grant: {'decision':'owned-recovery','reason':'E_ARTIFACT_MISMATCH',
  'escalation':'escalated-owned', 'worker':{'decision':'transition-committed',
  ... next p6c-h3v ...}}"}`.

## Causal trace (actions / executions / ledger / tamper / claims)

Run dir `/tmp/p6r11-case-tc8x0jvx`; executions `ex-61c76706a734` (worker),
`exv-61c76706a734` (verifier).

1. Worker dispatched `18:05:24Z`; claim `ex-61c76706a734.json` = `outcome
   completed`, `out.bin` sha256 `46409ea69826a6733ced5dd67fc0a9080601cbaaacd7a02192732356d25c0c88`.
2. `handoff-done:p6c-h3w:ex-61c76706a734` present → worker handoff committed.
3. `corrupt-after-worker` then overwrote the artifact **after** the commit:
   on disk now `9809428be764eec8582fc8be345d5dbdf89ece29f1c536bd6567691d3970300e`
   (`tampered-by-fixture-control`). Ordering is therefore **correct**
   (post-commit, before verifier recompute) — the completion claim's
   "tamper-before-recompute ordering unresolved" is **not** the defect.
4. Verifier dispatched `18:05:42Z` (`msg:msg-p6c-h3v-2` sent), produced stream
   end `i14269c7795f4`, and wrote `exv-61c76706a734.json`:
   `outcome:"failed"`, `check:"recompute-sha256"`,
   `check_detail:"hash mismatch: out.bin"`, referencing the **pre-tamper**
   `46409ea6…`.
5. **Which actor's hashes:** the verifier's own claim artifacts. The verifier
   recomputed the on-disk (tampered) bytes against the referenced pre-tamper
   hash. This is a genuine verifier rejection — not the worker re-validating
   after its own commit (the worker validation completed at step 2, before the
   tamper, with matching hashes).
6. **Exact source of `E_ARTIFACT_MISMATCH`:** `r3harness/turn_handoff.py`
   `recompute_artifacts` (`:196-218`) raises it because claim-declared
   `46409ea6…` ≠ disk `9809428b…`. In `run_handoff`, the
   `try: validate_claim; recompute_artifacts` block (`:272-283`) runs **before**
   the `outcome in ("failed","cancelled")` branch (`:289-290`); the raised code
   is not in `(E_FORGED_ROUTE,E_CLAIM_MISMATCH)`, so it routes to
   `_recover(..., "E_ARTIFACT_MISMATCH")` (`:284-286`) → `owned-recovery` +
   escalation. `run_fixture` returns that as the verifier result
   (`harness.py:781-806`); the candidate branch requires
   `transition-committed|terminal-rest` and raises `E_CASE_FAIL`.

## Repair location and smallest correction (not implemented)

- **Requires another module** — `r3harness/turn_handoff.py` (frozen, outside the
  authorized `case_entry.py`-only scope). It **cannot** be fixed in
  `case_entry.py` alone without either blessing the `E_ARTIFACT_MISMATCH`
  literal (explicitly forbidden) or re-implementing verification in the
  entrypoint.
- **Minimal specific change:** in `run_handoff`, for
  `contract_step == "verify-run"`, treat a claim whose `outcome` is a
  non-completion (`failed`) with a genuine artifact mismatch as a **bounded
  verified rejection** that leaves the action open (a distinct rejection
  decision consumed by `timecheck` as `accept-open`), instead of
  recompute→`E_ARTIFACT_MISMATCH`→`_recover`. The simplest form is to evaluate
  the verified `outcome` before invoking `recompute_artifacts` for verify-run,
  while still recomputing the artifact (independently checkable in the receipt)
  to prove the corruption. No change to `case_entry.py`'s COMPLETE-forbid is
  needed, but the branch's success condition must accept the rejection decision
  rather than only commit/rest.

## Manifest self-hash

- 32 entries; **31 correct, 1 offending**. Offending path
  `candidate/composition-manifest.json` declares
  `161afac5e212dbc99c77454f4d3cf6fd5ef1768e1c131663e60e7a26c7e78cca` (the old
  r9 manifest) while its actual sha256 is
  `742eeb792e3412…`. All other paths are candidate-bound
  (`candidate/src/...`, `candidate/tests/...`, `candidate/candidate-plan.md`,
  `candidate/changes.md`) with correct hashes; `changed` correctly lists
  `candidate/src/case_entry.py`. The self-entry is circular by construction —
  the fix is to exclude the manifest from its own list or bind it externally,
  never to hash the manifest inside itself. Rejected manifest left unchanged.

## Missing executable new-pass assertions

`candidate/tests/test_fault_ordering.py`, `test_case_execution.py`,
`test_observer_lifetime.py` are byte-identical to the r9 copies (no new
assertions). There is **no executable new-pass test** for FV accept-open or QR
continuation; `concrete-cases.md`'s cases assert the baseline **old-fails**
outcome and must not be represented as new-pass tests. `candidate/candidate-plan.md`
is prose only; `candidate/stagec-plan.json` is absent. The completion claim's
FV/QR results are ad-hoc runs, not a retained executable acceptance.

## Scoped positives / limits

- QR-W repaired on injected path (above); FV-W is not.
- QR-WV, FV-WV, both expiry controls, and the retained 34-test gate are
  **UNRUN** and are not promoted by this review.
- No live effect, no retry-until-green, no candidate/receipt/manifest edit
  occurred in this verification.

## Effect

One bounded verdict: **FAIL** — candidate-source change is real and scoped
(QR-W improved; harness frozen), but failed-verification is blocked by a
harness-level misclassification (`run_handoff` recompute-before-outcome) that
the authorized module set cannot repair, plus a manifest self-hash defect and
absent executable new-pass assertions; full gate unrun. Returned to Tern for the
warranted amendment/allocation.
