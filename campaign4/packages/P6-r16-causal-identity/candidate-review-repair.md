# P6-r16-causal-identity — repair-1 verification (D1/D2 + bound manifests + full gate)

- **Reviewer:** corvid-dsh
- **Action:** `P6r16-repairverify-1` (existing ≤30 m grant)
- **Brief:** `repair-1-receipt.json` / `repair-allocation-1.md`; base `64850c0`;
  prior bounded PASS `bb28e63f…` preserved, not promoted.
- **Final bytes:** `case_entry.py 1adf3ed271af…` (was `b14de4c46d03…`),
  outer manifest `3862a0a2…`, composition `6034fc3b…`, descriptor `a7afd10f…`.
- **Evidence:** `/tmp/p6r16-repair-gate.log` + `/tmp/r16-d1.py`. No source edit.

## Verdict

**PASS (bounded).** D1 is fixed and independently reproduced (old accepts a
missing-item sidecar by filename default; new rejects missing/null/empty/wrong
and still passes a genuine explicit item). D2 shows the upstream authority checks
already dominate on the fresh path (adversarial pre-planted item + plausible
sidecar → `E_UNDELIVERED`, behaviour unchanged). Full composed gate 78/78 and
retained 83+59 are green on the final modules; manifests/descriptor are accurate.
Cleared for Tern acceptance.

## D1 — explicit onset item (independently verified)

`case_entry._read_onset` now requires `rec["item"]` to be a nonempty string
**equal** to the requested bound item; missing/null/empty/wrong return `None`
(fail closed), no filename default. Independent probe against the pinned base
`64850c0` vs the repaired candidate:

| sidecar | OLD `_read_onset` | NEW |
|---|---|---|
| `item` absent | **accepted** (defaulted to filename) | rejected |
| wrong / empty / null `item` | rejected | rejected |
| genuine explicit matching item | accepted | accepted |

No R15 sidecar rewritten; genuine explicit items still pass; original
uncertainty/causal limits and metadata bindings preserved. `E_NO_ONSET` remains
the owned error for a missing bound source.

## D2 — fresh-path authority (proof reviewed; behaviour unchanged)

Trace confirms upstream checks dominate before the causal helper:
`turn_handoff.run_handoff` (`E_UNBOUND_TURN`/`E_STALE_TURN` on
action/execution/step + current execution), `validate_claim`/
`recompute_artifacts` (`E_FORGED_ROUTE`/`E_CLAIM_MISMATCH`) and
`case_entry` `E_UNDELIVERED` (pre-planted ends lack a delivery record). The
exact-CLI adversarial test `test_D2_adversarial_plant_with_plausible_sidecar_
rejected_cli` passes (planted item + plausible explicit-item sidecar, text held
→ `E_UNDELIVERED`); empty `carried` on fresh paths is normal and not required
nonempty. No caller-supplied mapping or stream membership is treated as
authority; no new schema/authority infrastructure added. Reported as
**proof-obligation satisfied, not a live defect**.

## Bound bytes / surface

- Only production change: `case_entry.py 1adf3ed2…`; `driver/ingress/store/
  lifecycle/validator/turn_handoff/harness/host_adapter` are **byte-identical**
  to R14. Manifests composition 74 / outer 78 — 0 drift, **no self-reference**;
  `R3_REVISION.json` 0 copy-hash drift.

## Gates (actual final modules)

- `PYTHONPATH=candidate/src pytest candidate/tests -q -p no:cacheprovider`
  → **78 passed in 666.17 s** (rc0), no skips/removals (76 prior + 2 D-checks).
- Retained `p5r2` → **83 passed**; `p3r3` → **59 passed**.
- D1/D2 targeted tests → 2 passed.

## Preserved / limits

Original wrong-pair fix, authenticated rejection, no-COMPLETE, no-duplicate
sends, T1–T4 and R13 safeguards retained; R15 diagnostic replay remains
**non-live** with no retroactive PASS; live held. Late-recorded completion proof
and queued/ambiguous controls unresolved; finding5 NOT REPRODUCED.

## Effect

One bounded verdict: **PASS (bounded)** — D1 explicit-item rejection and D2
upstream-authority proof verified, full composed 78/78 plus retained 83+59 green,
descriptors/manifests accurate. Returned to Tern for acceptance and a fresh live
witness under separate exact releases.
