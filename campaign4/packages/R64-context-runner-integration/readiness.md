# R64 readiness (offline only; no live qualification authorized)

## Commands (future, after a separate Tern release)
- Launch one arm: `env -u STUB_BIN -u DRY -u TEST_PROJECTS -u TEST_PRECREATE -u TEST_MUTATE_BETWEEN -u TEST_TIMEOUT -u GATE -u EVENTS -u OPROOT -u EVIDENCE_DIR sh R64/operator/run-arm.sh LABEL` -> immutable bundle R64/evidence/LABEL with candidate-r63.json, operator-meta.json, report.md, disposition ("HOLD awaiting adjudication"), arm-claim.json.
- Review: corvid writes a receipt (schema r63-adjudication-v1 + label + arm_claim_sha256; see tests/evidence/receipt-sample-TEST-ONLY.json, an offline stub, not a review) OUTSIDE the bundle, judging source_evidence and ask_relevant against transcripts and memory snapshots.
- Finalize: `python R64/operator/finalize.py LABEL RECEIPT.json` -> R64/finalized/LABEL.json (refuses to overwrite). Tern decides only on FINAL / FINAL_INVALID; HOLD, HOLD_EVIDENCE and HOLD_INTEGRITY block. A non-HOLD status is a research observation, not qualification success.

## Frozen dependency manifest
Pinned per arm by operator/freeze.sh (dependency_sha256): R64 operator/run-arm.sh, freeze.sh, launch/common.sh, session.sh, fixture/bench.sh, setup.sh, all 7 templates; R56 scanner/scan.py and scanner/operator/scan_gate.py; R63 gate.py; R54 events.py. The finalizer re-checks every pinned file and dependency and rejects extra files.

## Test matrix (requirements.md T1-T8; actual runner + finalizer, stubs; tests/evidence/run1.txt, run2.txt identical outcomes)
T1 all 8 labels: N/I/R 2 calls, D 1; R/D candidate_primary, N/I asked_no_run, N/I no save = ABSENT (valid absence). T2 approve -> FINAL primary; bundle bytes unchanged. T3 no receipt HOLD, reject withheld, source indeterminate HOLD, irrelevant ask HOLD, relevant ask FINAL non-primary. T4 wrong label / wrong claim hash / other arm's receipt -> HOLD. T5 tampered log, report, transcript, memory manifest, candidate, meta -> HOLD_EVIDENCE. T6 s2 fail, scanner gate 1, events failure, between-session mutation with approve receipt -> HOLD_INTEGRITY; s1 fail -> HOLD_EVIDENCE (no candidate exists; still blocked). T7 existing project 0 calls; duplicate exit 4, no new op dir; live seam and real-claude stub refused; refinalize refused.
Disclosed: first run found a finalizer bug (tuple vs JSON list made every recomputed candidate differ -> every arm HOLD_EVIDENCE; fail-closed, not fail-open). Fixed; first run kept at tests/evidence/first-run-before-fix.txt. Requirements were frozen before; the fix changed no expectation.

## Remaining live uncertainty (minimal) and proposed bounded qualification (NOT authorized)
Unknown: whether real Claude fills the R62 schema (CONTEXT_SOURCE) as intended; whether the disclosed trace sentence changes N/I asking; real permission behaviour of bench.sh under dontAsk (R61 worked). Proposal: one R64 D-24576 arm (1 Max call) plus corvid receipt and finalize, to prove schema, candidate, receipt and finalizer end to end on one real transcript; then Tern decides a full 14-call cohort in the R62 order. No screening: a failure is recorded, not retried.
Limits: reviewer independence is operational only (same user runs all seats); stub receipts are test-only.
