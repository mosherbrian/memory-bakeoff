# P6-r15 — live failed-verification review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r15-live-review-failed-1` (allocated ≤15 m)
- **Evidence:** `live-failed-1/` (raw streams, faults, claims, latency, DB,
  deliveries, cleanup archive), `failed-1-result-reconciliation.md`,
  `live-failed-1-release.json`.
- **Scope:** read-only chronology/rejection/no-COMPLETE/timing/cleanup and the
  onset-join question. No code/artifact change, no rerun.

## Disposition (one)

**INCOMPLETE (bounded).** The live run produced a **genuine authenticated
verifier rejection** — real applied post-commit tamper, worker publication,
verifier `failed` claim on a real bytes mismatch, `verified-rejection`, exactly
1+1 sends, **never COMPLETE** — but the case did not receive a live PASS because
the causal gate aborted `E_CAUSAL` on a **wrong onset join**: it paired the
*verifier's* onset with the *worker's* detection. Timing was therefore never
accepted. Production result and timing failure are preserved together; no
retiming, synthetic PASS, resend or repair.

## Chronology (raw)

| instant (UTC) | event |
|---|---|
| 00:50:40 | `fault arm` `corrupt-after-worker`, `induced:true` |
| 00:50:44 | worker delivered (`msg-...-w-1` sent), started |
| 00:51:11 | worker `transition-committed`; artifact tampered (applied `before 46409ea6 → after 9809428b`) |
| 00:51:11 | verifier delivered (`msg-...-v-2` sent) |
| 00:52:37 | verifier `verified-rejection` (claim `outcome:failed`, `hash mismatch: out.bin`) |
| end | `run.out` `E_CAUSAL` "onset not before detection: 00:52:37 vs 00:51:11" (rc3) |

## Genuine rejection / no-COMPLETE (confirmed)

- `faults/failed-verification.applied.json`: `artifact_control.induced:true`,
  `before 46409ea6…` → `after 9809428b…`, applied `00:51:11Z`; two real
  deliveries (worker + verifier) via the deposit path.
- Claims: worker `ex-69db07a74cbd` `completed` referencing `46409ea6…`; verifier
  `exv-69db07a74cbd` `outcome:failed`, `check:recompute-sha256`,
  `check_detail:"hash mismatch: out.bin"` referencing `46409ea6…`. On-disk
  `art/out.bin` = `9809428b…` (tampered).
- Receipt `outcome.decision = verified-rejection`, `expected 46409ea6…` /
  `observed 9809428b…`, `sends {worker:1, verifier:1}`, `committed_actions`
  worker+v, `gate PASS` on the bound IDs, `simulated:false`, `induced:true`.
  **No COMPLETE / terminal-rest.**
- Latency rows: worker `transition-committed` `00:51:11` (onset provenance
  `fixture-producer-seat`, uncertainty 1 s); verifier `verified-rejection`
  `00:52:37`. Both onsets carry the producer sidecar provenance.

## Onset-join root cause (the question)

`case_entry._check_causal` (`candidate/src/case_entry.py:859`) selects the
**first sorted** onset file:
`for f in sorted(os.listdir(onsets_dir)): … break`. Sorted names
`i42e65da2879b.json` (verifier item, onset `00:52:37`) precedes
`id492c9c28b64.json` (worker item, `00:51:11`), so it pairs the **verifier**
onset with `det_by_action[worker_action]` = `00:51:11` and computes
`(00:51:11 − 00:52:37) = −86 s < −1 s` → `E_CAUSAL`. This is a **wrong join**,
not a producer clock reversal, a late producer timestamp, a comparator arithmetic
error (the comparison is correct *for the wrong pair*), or a false
applied-control claim (the tamper receipt is real). An independent onset existed
for the worker and would have satisfied `armed < onset < detection`.

**Smallest correction (recommended, not implemented):** select the onset bound
to the worker action/item when evaluating the worker detection (and evaluate each
action's onset against its own detection), rather than the lexicographically
first onset file. This is a comparator/join fix, no retiming of evidence.

## Timing / cleanup

- Timing acceptance is **INCOMPLETE**: `E_CAUSAL` aborted before `timecheck`; the
  receipt carries no `timecheck`/`causal` acceptance. Worker/verifier intervals
  are recorded and internally consistent but unjudged.
- Cleanup: exact-ID archive present (`live-failed-1/cleanup-archive/`); both r15
  fixture IDs (`d7a32519…`, `9c645264…`) are now **ABSENT** from the live
  registry. Residual: the owned case timer `p6r15-f1-failed-verification.timer`
  was still armed at review (`17:55:44 PDT`), and the automatic
  `campaign4-p6r15-failed1-cleanup.timer` remains armed (~`01:19Z`); confirm the
  case timer is retired and the automatic cleanup actually completes.

## Bounded result / limits

- One live witness of authenticated rejection + applied tamper + no COMPLETE, but
  **not** a live PASS; no duplicate sends; no fabricated onset.
- Missing/unjudged timing and the onset-join defect bound this to INCOMPLETE.
- No four-case, adoption, retirement or research claim; R9 positive remains
  historical; quiet-rest release should wait for this scope determination.

## Effect

One disposition: **INCOMPLETE (bounded)** — genuine rejection demonstrated,
timing unaccepted due to a wrong onset join; evidence preserved; no rerun or
repair. Returned to Tern.
