# P6-r17 — live failed-verification review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r17-live-review-failed-1` (allocated ≤15 m)
- **Evidence:** `live-failed-1/` (streams, faults, claims, latency, DB,
  deliveries, cleanup archive), `failed-result-reconciliation.md`,
  `live-failed-1-release.json`, `admission-review.md`.
- **Scope:** read-only trace of the `E_NO_ONSET` cause; no code/evidence edit, no
  retry, no synthesized onset.

## Disposition (one)

**INCOMPLETE (bounded).** The live run again produced a **genuine authenticated
verifier rejection** (real post-commit tamper, verifier `failed` claim on a bytes
mismatch, `verified-rejection`, 1+1 sends, **never COMPLETE**), but the causal
gate aborted `E_NO_ONSET` because the **producer onset sidecars are absent**:
`onset_dir` is empty, so no item can be resolved. This is **missing
instrumentation / producer noncompliance**, not a new identity-join defect and
not missing end records. Preserve rejection and missing source together.

## `E_NO_ONSET` root cause (traced)

- `run.out`: `E_NO_ONSET "no bound source item for required action
  p6r17-f1-failed-verification-w; INCOMPLETE"`.
- **Ends are present:** worker stream ends `{"t":"end","item":"i1790129700495"}`;
  verifier stream ends `{"t":"end","item":"i1790129733549"}`.
- **Onset sidecars are absent:** `failed-verification/onsets/` is empty, and no
  `*onset*` files exist anywhere under the live root or `/tmp/p6r17-live-failed-1`.
- `_resolve_item` resolves an item only from `stream_end_items ∩ onset_sidecars`;
  with an empty onset dir the intersection is empty → `E_NO_ITEM` (caught) →
  `items[sid]=None` → `_resolve_causal_items` maps nothing → required worker
  source missing → `E_NO_ONSET`. Receipt `worker_item`/`verifier_item` are
  therefore `null`; latency rows carry `onset_at: null`, `onset_known: false`.
- So the answer to the missing-vs-join question: **sidecars absent (empty dir)** —
  not malformed, not wrong item, not wrong path, not present-but-unjoined, and
  not a filename/identity-join regression.

## Task-instruction comparison (R15 vs R17)

The dispatched worker/verifier task texts are **identical** between R15 and R17
and contain **no instruction to write an onset recorder/sidecar** or its
schema/path (`onset_dir` appears only in the harness manifest, not in the
dispatched text). R15's seats nevertheless produced sidecars
(`i42e65da2879b.json`, `id492c9c28b64.json`, provenance `fixture-producer-seat`);
R17's real seats produced `end` records but **no sidecars**. Instrumentation was
therefore assumed/inferred in R15 and is now missing — an undocumented producer
requirement plus live-seat noncompliance. No timestamp was invented from detector
time; the real worker/verifier runtimes (33 s/34 s) and item↔detection mapping
are otherwise intact in the streams.

## Genuine rejection / no-COMPLETE (confirmed)

- `faults/failed-verification.applied.json`: `corrupt-after-worker`, `induced`,
  applied post-commit (expected `c16a40a4…` → observed `9809428b…`; disk
  `out.bin` = `9809428b…`).
- Claims: worker `ex-75ca81d45b77` `completed`; verifier `exv-75ca81d45b77`
  `outcome:failed`, `check:recompute-sha256`, `hash mismatch: out.bin`.
- Receipt: `outcome.decision = verified-rejection`, `expected/observed` present,
  `sends {worker:1, verifier:1}`, `committed_actions` both, `gate PASS`,
  `simulated:false`, `induced:true`; **no COMPLETE / terminal-rest**. Latency has
  worker `transition-committed` (02:15:33) and verifier `verified-rejection`
  (02:16:07) but no accepted `timecheck`.

## Cleanup / runtime

- Both r17f1 IDs are **ABSENT** from the live registry; exact-ID cleanup archive
  (`cleanup-archive/launcher-records.json`) holds exactly the two prepared IDs.
- Residual: the owned case timer `p6r17-f1-failed-verification.timer` was still
  armed at review, and the safety
  `campaign4-p6r17-failed1-cleanup.timer` remains armed (~29 m). Confirm the case
  timer retires and the safety cleanup completes.
- Quiet-rest remains **BLOCKED/UNEXECUTED** per `admission-split-decision.md`;
  not inferred from this failed case.

## Bounded result / limits

- One live witness of authenticated rejection + applied tamper + no COMPLETE, not
  a live PASS. Missing producer onset instrumentation bounds it to INCOMPLETE.
- No code/source/evidence change, no retry, no manufactured onset. R9 positive
  remains historical; no four-case/adoption/retirement claim.

## Effect

One disposition: **INCOMPLETE (bounded)** — genuine rejection preserved, timing
unaccepted because producer onset sidecars are absent (undocumented requirement /
seat noncompliance), not an identity-join defect. Returned to Tern for terminal/
successor decision (bounded instrumentation or contract correction); quiet case
stays blocked.
