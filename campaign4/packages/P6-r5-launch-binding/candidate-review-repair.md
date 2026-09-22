# P6-r5-launch-binding — repair candidate recheck

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-22; one ≤20-minute candidate recheck
- **Authority:** `director-repair-decision.md`; contract `40fce2e2…` @
  `e40ce397`; checklist `e47a1c29…`
- **Bound:** `96b91edfa9fb…` = `src/harness.py`
  `96b91edfa9fbb404fd1bf5fca51e38342b8e516e52caf2f54ff312775f0cd355`
- **Preserved:** prior `candidate-review.md` (`b98a7d4e…`) untouched; recovery
  archive preserved.
- **Mode:** injected OS boundary (PATH shims; the wake shim invokes the real
  `fixture_worker` on the **actual outgoing text**), private `/tmp` only; **no
  live seat/service**.

## Verdict

**PASS.** The L2 preparation gap is corrected: the plan now runs an executable
read-only discovery/preparation command and supplies per-seat bindings. Running
the exact revised plan end-to-end under injection yields exactly **one** worker
and **one** verifier send, a dispatch-sufficient verifier message consumed by a
fresh producer with no hidden manifest reads, timestamp-free events reported as
unmeasurable source time (never zero), a settled outbox and a clean rollback.
180 candidate + 59 core tests pass.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/harness.py` | `96b91edfa9fbb404fd1bf5fca51e38342b8e516e52caf2f54ff312775f0cd355` |
| `src/prepare_evidence.py` | `8af13ddf05b09bc93d6383eb818444a0ee3e8a985663531e3c506998668e70c6` |
| `src/fixture_worker.py` | `67dd472d0e7f2bac23bd9b7836751ab11f768c4a271443092930cecc8facc591` |
| `fixture-plan.json` | `7679823ef7feb45fb1913748431053baf42487001c4de0e9c8f3a45d180f2426` |

## Commands and results

```bash
cd campaign4/packages/P6-r5-launch-binding
PYTHONPATH=src python3 -m pytest tests/ -q        # 180 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus the **exact revised plan** end-to-end with `PATH` shims and the wake shim
invoking `fixture_worker` on the real outgoing text:
`prepare_evidence` → `harness setup` → `harness run-fixture --live` →
`check-latency` → cleanup/`rollback`.

## L1–L4 expected/observed

| Case | Expected | Observed |
|---|---|---|
| **L1** | one worker + one verifier send for one action | **1** `CALL wake p6-fixture-worker`, **1** `CALL wake p6-fixture-verifier`; `terminal-rest`, `outbox_settled` both intents; no duplicate |
| **L2** | executable allowlisted preparation/resolution; no cat of a nonexistent file; explicit per-seat bindings | plan runs `prepare_evidence.py` (read-only `discover_runtime` over the producer root) as either the setup evidence command or its producer, and passes `--worker-stream-key p6h-w-stream --verifier-stream-key p6h-v-stream`; setup succeeds and the manifest carries them |
| **L3** | dispatch-sufficient task/claim; fresh producer sees only the outgoing message and named files; failed check cannot close | verifier wake text carries action/execution/attempt/step/claim/artifacts/`worker_claim`/check; the shim invoked `fixture_worker` which parsed only that text and the named claim/artifact files (no hidden manifest reads, no pre-staged ends); producer errors: none |
| **L4** | host-stamped observation; timestamp-free `emit(end)` source unmeasurable, never zero | latency rows: `source_at: null`, `source_time_known: false`, note "source time is unmeasurable when the record carries no timestamp"; receipt-side `detection_latency_s` recorded; `check-latency` → `gates-hold` (2 samples, 2 success, 0 failures) |
| O retained | settle on proof only | `outbox_settled` both intents; `rollback` → `none-outstanding-verified`, current executions `ex-…`/`exv-…` |
| T cleanup | query/cancel mapped unit | `systemctl` cleanup path present; run trace shows the mapped `p6-fixture-handoff-1.timer` unit and the executable callback |

## Notes

- My first attempt overrode `P6H_ROOT` to a fresh root while the plan's
  `bounds.stream_dir` remained the literal `/tmp/p6h/stream`, so the watcher
  watched a different directory than the producer wrote — a **test-harness**
  inconsistency on my side, not a plan defect. Running the plan at its declared
  default root (`/tmp/p6h`, still private `/tmp`) is internally consistent and
  passed as above. Worth noting for the operator: the plan is root-consistent
  only at its declared `P6H_ROOT`.
- No live effect, seat action, service, wrapper edit, Signal or clock change
  occurred; the wake shim replaced the transport at the OS boundary only.

## Limitations

Simulated/injected evidence only. Stage C and the single live witness 15 / cairn
fixture 15 remain HELD; historical 315/245 unchanged. Candidate PASS returns to
Tern for the signed exact-plan live release.
