# Habitus provenance re-run — recorded method, recorded class defect

**Author:** Corvid (`worker-glm-dsh3`), R&D pulse 2026-09-12
**Cost:** $0, local, in-process, deterministic; no LLM, no network, no model
weights. **New result dirs** (nothing overwritten):

- `results/habitus_provenance_probe_20260912_core/`
- `results/habitus_provenance_probe_20260912_stress/`

**Plain English (for Brian):** the old Habitus run predates the provenance
schema, so we could only *infer* whether its evidence used native record IDs.
I re-ran the same provider with the current runner. It reproduces the old
numbers exactly and now **records** the answer: 100% native IDs. The same fresh
run also records the class-label defect — it labels the run `raw_product` when
it should be `controlled_core` — turning that from an argument into a receipt.

## Commands

```bash
cd implementer/repo-glm-dsh3
PYTHONPATH=src python3 -m memory_bakeoff.cli run --providers habitus \
  --mode raw --distractors 0   --out results/habitus_provenance_probe_20260912_core
PYTHONPATH=src python3 -m memory_bakeoff.cli run --providers habitus \
  --mode raw --distractors 450 --out results/habitus_provenance_probe_20260912_stress
```

## Result 1 — the frozen numbers reproduce

| Run | Hit@5 | MRR | All-relevant@5 | Prohibited@5 | Matches frozen |
|---|---|---|---|---|---|
| core | 0.875 | 0.785 | 0.750 | 0.097 | `results/habitus_core` exactly |
| stress | 0.792 | 0.701 | 0.667 | 0.025 | `results/habitus_stress` Hit@5/MRR/prohibited exactly |

## Result 2 — the method is now recorded, not inferred (closes survey gap 5)

The new `run.json` carries the fields the frozen one lacked:

```json
"experiment_class": "raw_product",
"publishability": {"status": "publishable", "publishable": true, "reasons": []},
"provenance": {"status": "verified", "publishable": true,
               "methods": {"native": 76},
               "reason": "all returned evidence used native IDs or exact canonical markers"}
```

- core: **76 native** resolutions; stress: **130 native**.
- Those counts are exactly the frozen runs' `retrieved_ids` counts (76 and
  130), which is corroboration that the frozen runs used the same native path
  (the artifact-level census showed 100% canonical IDs).
- Combined with the vendored code persisting `record.record_id` and the earlier
  synthetic probe, the method half of survey gap (5) is now **recorded native**
  for Habitus. No `fuzzy_subtext`/`unmapped` appears, so the headline rows are
  not exploratory-only on provenance grounds.

## Result 3 — the class-label defect now has a run-level receipt

The fresh run's own `experiment_class` is **`raw_product`**, but the evaluated
configuration is a **`controlled_core`**: the vendored run uses the upstream
`DeterministicHashEmbedder`, whose docstring
(`vendor/habitus/src/habitus_ai/embeddings.py:37-44`) calls it an offline
test/demo stand-in. The written evidence pages (`RESULTS.md:80`,
`ROUND1_FINAL_READOUT.md:14`) already say `controlled_core`; this run shows the
adapter's declared class disagreeing with them. Fix (owner = implementer/build):
explicit `raw_experiment_class = "controlled_core"` and
`product_experiment_class = "controlled_core"`, plus `product_ingest=False`.

## Method and limits

- In-process, deterministic, `$0`; the "dense" lane is still the offline hash
  stand-in, so this is a `controlled_core` result regardless of the label the
  adapter prints.
- New directories only; the frozen `results/habitus_core|stress` are untouched.
- This reproduces the *provider path and scores*, not the frozen run's original
  process; it is a same-configuration re-derivation, not a replay.

— **Corvid** (`worker-glm-dsh3`). The old run could not say how it resolved
IDs; the new one does, and it also names the label bug.
