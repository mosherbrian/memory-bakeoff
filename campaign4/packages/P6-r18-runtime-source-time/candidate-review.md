# P6-r18-runtime-source-time — candidate review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-review-1` (existing ≤40 m grant)
- **Brief:** `dispatch-receipt.json` (`P6r18-candidate-1`, contract
  `8e981e9e…`, admission `6f461611…`); parent R16 `c8e99cf` / manifest
  `3862a0a2`, R17 evidence `d0769c2e`.
- **Claim:** `completion-claims/ex-p6r18-candidate-1.json`.
- **Evidence:** `/tmp/p6r18-review-gate.log`. No source edit, no live effect.

## Verdict

**FAIL (bounded) — manifest binding defect.** The source-time implementation is
correct and the full composed gate is green (90/90), retained 83+59 green, core
byte-identical, and the shipped hook works through a real subprocess. But the
delivered `candidate/manifest.json` is materially inaccurate: **79 of 162 entries
point into a stale duplicate tree `candidate/candidate/…`** (R16/R14 bytes),
alongside the correct outer entries. The contract requires accurate acyclic
manifests; this must be corrected before acceptance. (The source-time work itself
is otherwise sound and is retained as bounded evidence.)

## Manifest defect (blocker)

- `candidate/manifest.json`: 162 entries → **79 under `candidate/candidate/`**,
  83 outer; 0 hash drift (the nested files exist and match), so the drift check
  alone does not catch it.
- The nested tree is a stale pre-change copy: `candidate/candidate/src/
  case_entry.py = 1adf3ed2` (R16) vs the real `candidate/src/case_entry.py =
  a07f82e4`; `…/r3harness/harness.py = 50f15cdf` (R14) vs the real `d44e6103`.
  It also carries `__pycache__`.
- So the manifest binds both the actual candidate and a stale R16/R14 duplicate;
  paths/prefixes are not the reviewed bytes for half the entries. This violates
  "accurate acyclic manifests/descriptors … no stale provenance" and the
  "unchanged-core comparison" intent.
- **Smallest correction:** remove the `candidate/candidate/` duplicate tree and
  re-emit `manifest.json` (and `composition-manifest.json`) mechanically with
  only the actual `candidate/...` paths, acyclic, no self-hash.

## Source-time implementation (sound; retained)

- `runtime/interface.md`: v1 same-record versioned fields, one append; consumer
  `source_mode` (`runtime` | `sidecar` legacy); failure semantics truthful
  (unavailable/missing → INCOMPLETE, telemetry never kills work; end ≠ work
  success).
- `runtime/srcemit.py`: `source_fields(session,item,now)` with nonempty
  session/item validation, host-UTC stamp, `src_uncertainty_s:1`, clock state
  `ok`/`discontinuous`/`test`, `src_status`; `emit_end` single write+fsync and
  `SourceWriteError` after stderr. Independent subprocess probe
  (`ACP_SOURCE_TEST_NOW` injected) emitted exactly one matching versioned end
  record (rc0).
- `runtime/acp-worker` (local copy): confined diff — `_runtime_source_fields`
  delegate + `emit("end")` merges the receipt into the same record; helper
  failure → stderr + explicit `unavailable` receipt; append failure now reported
  on stderr (previously silent). Shared `~/.config/agent-deck` untouched.
- Consumer (`case_entry.py`/`harness.py`): `source_mode: runtime` parses the
  receipt from the observed end, persists to kv, joins each action's receipt to
  its own detection via R16 item→action binding; `src_status`/`src_clock` gating
  and session/item/execution binding; sidecar mode preserved. Core
  `driver/ingress/store/lifecycle/validator/turn_handoff` and `host_adapter`
  byte-identical to R16.

## Gates

- `PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider`
  → **90 passed in 666.61 s** (rc0), no skips/removals.
- Retained `p5r2` → **83 passed**; `p3r3` → **59 passed**.
- Claimed negatives/replays and unshared mutation are in `test_r18_source_time.py`
  (I did not individually re-run each within the bound; the composed gate covers
  them, and my subprocess hook probe is independent).

## Bounded / limits

R17 diagnostic replay and R15 remain non-live; quiet-rest configurable-window
correction still owed; candidate PASS never certifies live timing/runtime
adoption. No code/evidence edit, no live effect.

## Effect

One bounded verdict: **FAIL (bounded)** — source-time fix and gates are good, but
the stale `candidate/candidate/` duplicate baked into 79 manifest entries must be
removed and the manifests re-emitted before acceptance. Returned to Tern.
