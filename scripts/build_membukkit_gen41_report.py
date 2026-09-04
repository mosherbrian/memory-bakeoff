#!/usr/bin/env python
"""Build the Gen41 research report from the committed Round1 leaves."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen41 import (  # noqa: E402
    CONFIGURATIONS,
    EXPECTED_RETRIEVAL,
    ROUND1_CONDITIONS,
    contract_sha256,
    gen8_reference,
    membukkit_pin,
)

MANIFEST = ROOT / "results" / "membukkit_gen41_manifest"
METRICS = ("hit@5", "mrr", "all_relevant@5", "prohibited@5", "useful_before_harmful",
           "mean_context_chars")


def fmt(v) -> str:
    return f"{v:.4f}" if isinstance(v, float) else str(v)


def signed(v: float) -> str:
    return f"{v:+.4f}" if v else "0"


def main() -> int:
    cmp_ = json.loads((MANIFEST / "comparison.json").read_text())
    gate = json.loads((MANIFEST / "replication_gate.json").read_text())
    pins = json.loads((MANIFEST / "pins.json").read_text())

    POLICIES = ("product_default", "cpu")

    def control_json(policy: str, condition: str = "core"):
        return json.loads(
            (
                ROOT / "results"
                / f"membukkit_gen41_replication_control_{policy}_{condition}-r1"
                / "gen41_control.json"
            ).read_text()
        )

    devices = {
        policy: {p["kind"]: p["devices"] for p in control_json(policy)["device_proof"]}
        for policy in POLICIES
    }

    lines = []
    for policy in POLICIES:
        for condition in ("core", "stress"):
            b = cmp_["conditions"][policy][condition]
            for key in METRICS:
                lines.append(
                    f"| {policy} | {condition} | {key} | {fmt(b['fallback_control'][key])} | "
                    f"{fmt(b['intended'][key])} | {signed(b['delta_intended_minus_fallback'][key])} |"
                )
    table = "\n".join(lines)

    gate_rows = "\n".join(
        f"| {c} | {policy} | {len(g[policy]['metric_differences_vs_gen8'])} | "
        f"{len(g[policy]['queries_with_different_retrieved_ids'])} | "
        f"{g[policy]['repeats_retrieved_ids_identical']} | {g[policy]['provenance_clean']} |"
        for c, g in gate["conditions"].items()
        for policy in POLICIES
    )

    pin_rows = "\n".join(
        f"| {cfg} | {role} | `{spec['repo']}` | `{spec['revision'][:12]}` | "
        f"{pins[cfg][role]['n_files_local']} | {len(pins[cfg][role]['reconciliation']['mismatched'])} |"
        for cfg, roles in CONFIGURATIONS.items()
        for role, spec in roles.items()
    )

    stability = "\n".join(
        f"| {policy} | {c} | {b['control_repeats_ids_identical']} | "
        f"{b['intended_repeats_ids_identical']} | "
        f"{len(b['queries_with_different_retrieved_ids'])} |"
        for policy in POLICIES
        for c, b in cmp_["conditions"][policy].items()
    )

    lat = "\n".join(
        f"| {policy} | {c} | {b['latency_ms']['fallback_control'][0]:.1f} | "
        f"{b['latency_ms']['intended'][0]:.1f} |"
        for policy in POLICIES
        for c, b in cmp_["conditions"][policy].items()
    )

    cpu_stress = gate["conditions"]["stress"]["cpu"]
    cpu_drift = cpu_stress["metric_differences_vs_gen8"]
    drift_text = (
        ", ".join(
            f"{k.upper()} {v['gen8']:.4f} to {v['gen41']:.4f}" for k, v in sorted(cpu_drift.items())
        )
        or "none"
    )

    anchor = {c: gen8_reference(ROOT, c)[0] for c in ROUND1_CONDITIONS}

    doc = f"""# MemBukkit intended models on the frozen Round1 raw-product ruler

**Evidence class:** existing `raw_product`, configuration-scoped to *MemBukkit intended models*.
This is a within-product model-weight ablation on a frozen ruler, not a new lane. It does not
replace the Gen8 documented-fallback row, which stands unchanged, and it says nothing about
MemBukkit's quality on any other benchmark.

Gen40 proved the intended MemseekAI pair loads and runs. Gen41 asks the only question that
proof unlocked: on the same corpus, scorer, provider, ingest surface, retrieval configuration
and device policy, what do the intended weights do that the documented fallback pair did not?

## What was held fixed

MemBukkit source `{membukkit_pin()}` — the Gen7/Gen8/Gen40 pin, unchanged. Ingest through
upstream `MemorySystem.ingest_facts`, one benchmark record per atomic fact, no distiller and no
LLM. Retrieval exactly as the committed provider freezes it: `union_lanes=("atomic",)`,
`bucket_mode=topic`, `num_buckets={EXPECTED_RETRIEVAL['num_buckets']}`,
`scan_budget={EXPECTED_RETRIEVAL['scan_budget']}`, `select="{EXPECTED_RETRIEVAL['select']}"`,
`rerank_cap={EXPECTED_RETRIEVAL['rerank_cap']}`, `top_k={EXPECTED_RETRIEVAL['top_k']}`,
`k_rrf={EXPECTED_RETRIEVAL['k_rrf']}`, `lexical_lane=False`, in-memory backend, Round1 scorer
consuming the top 5. Asserted at the start of every scored run, not assumed.

## Device, which had to be closed first

`research/MEMBUKKIT_FALLBACK_GEN8.md` records that Gen8 ran on CPU, and Gen40 measured that the
historical encoder wrapper never passes `ModelConfig.device` to `SentenceTransformer`, so the
bi-encoder auto-selects an accelerator while the reranker honours the request. Left alone that
would have made device a second variable inside a model-weight ablation, so Gen41 set out to
force both models onto CPU.

The replication control says that plan was built on a wrong premise. Under a forced CPU the
stress condition does **not** reproduce Gen8: {drift_text}, and 9 of 26 queries come back
reordered. Under the product's own device selection it reproduces Gen8's committed metrics
exactly, in both conditions. Gen8's models therefore ran on the accelerator, whatever its
document says. The claim was never checked at the time because nothing depended on it until now.

Device therefore cannot be both "equal to Gen8" and "CPU". Rather than pick one and lose the
other, Gen41 runs **both policies**, each internally matched across the two model
configurations, and declares that tolerance before reading any intended-model result:

- `product_default` — the product selects the device, which is what Gen8 did. Proven devices:
  bi-encoder {devices['product_default'].get('biencoder')}, reranker
  {devices['product_default'].get('reranker')}.
- `cpu` — a harness-owned shim supplies a device at the model constructor boundary where the
  caller supplied none. Proven devices: bi-encoder {devices['cpu'].get('biencoder')}, reranker
  {devices['cpu'].get('reranker')}.

The shim touches no weight, tokenizer, pooling, precision or retrieval parameter, and the device
is read off each constructed model rather than trusted, on all twenty-four scored runs. Because
each policy is internally matched, each is a valid model-weight ablation on its own; the pair
also shows whether the answer survives the device choice.

## Model pins

| configuration | role | repository | revision | files loaded | mismatched files |
| --- | --- | --- | --- | --- | --- |
{pin_rows}

Only loader files are downloaded for the fallback pair; the ONNX, OpenVINO and duplicate `.bin`
exports in those revisions are never touched, so reconciliation is scoped to the downloaded
manifest and says so. One provenance detail worth recording: the fallback reranker id named in
the pinned MemBukkit source, `cross-encoder/ms-marco-MiniLM-L-6-v2`, now redirects — Hugging Face
renamed the repository to `ms-marco-MiniLM-L6-v2`. The revision is unchanged, and the pinned
revision resolves under the new name.

## Replication gate — run before the intended models saw the ruler

| condition | policy | metric differences vs Gen8 | queries with different returns | repeat returns identical | provenance clean |
| --- | --- | --- | --- | --- | --- |
{gate_rows}

The gate passes on a declared tolerance, not on silence: the product-default control must
reproduce Gen8 exactly — which is what proves harness, corpus, scorer, ingest and retrieval
equivalence — and the CPU control's deviation must be confined to what the device change itself
moves. The CPU deviation is published above as its own quantity rather than absorbed into a pass.

Committed Gen8 anchor: core Hit@5 {fmt(anchor['core']['hit@5'])}, MRR {fmt(anchor['core']['mrr'])};
stress Hit@5 {fmt(anchor['stress']['hit@5'])}, MRR {fmt(anchor['stress']['mrr'])}.

## Result

| device policy | condition | metric | fallback control | intended | delta |
| --- | --- | --- | --- | --- | --- |
{table}

Retrieval latency, operations only, mean ms per query:

| device policy | condition | fallback control | intended |
| --- | --- | --- | --- |
{lat}

## Stability

| device policy | condition | control returns identical across repeats | intended returns identical across repeats | queries where the two configurations differ |
| --- | --- | --- | --- | --- |
{stability}

## What the numbers say

Read across the two policies first: every delta agrees in sign and, apart from MRR, in value to
four decimal places. The answer does not depend on the device choice.

The intended models **find more and rank worse**. Under stress they raise Hit@5 from 0.8750 to
0.9167 and All-relevant@5 from 0.7500 to 0.8333, lower Prohibited@5, and lift
useful-before-harmful — but MRR falls by about 0.09 to 0.10. Under core they raise MRR from
0.5854 to 0.6417 while dropping All-relevant@5 from 1.0000 to 0.9583, the only metric where the
fallback pair was already at ceiling.

The retrieval change underneath those modest numbers is not modest: the two configurations return
a different top-5 on 22 of 26 core queries and on all 26 stress queries. A reader who saw only
the aggregate would conclude the swap barely mattered. It changes almost every answer.

Nothing here says the intended pair is better or worse. It says the fine-tuned pair surfaces the
relevant record more often in the harder condition and places it lower in the list when it does,
under this frozen ruler, at these settings, on this corpus of 26 queries — a corpus far too small
for those differences to be more than descriptive.

## Reading rules for this row

Every returned item mapped through native `source_ref` to a benchmark record; no fuzzy or
text-derived recovery. No LLM, no reader and no external API took part, and outbound network was
blocked at the socket layer inside every scored run. No benchmark gold or scorer-only field
reaches indexed text, a model query or product metadata. The local Metal accelerator is used in
the `product_default` policy — that is what Gen8 did and what reproducing it requires — and is
not used at all in the `cpu` policy; no inference server or remote accelerator is involved in
either.

Because source, ingest surface, retrieval configuration, device, scorer and corpus are all held
fixed and proven, the differences above are caused by the model configuration under this frozen
setup. That statement does not extend to MemBukkit's product quality in general, to its LLM
distiller path, or to any other benchmark.

Contract `src/memory_bakeoff/membukkit_gen41.py`, sha256 `{contract_sha256()}`.
Artifacts: `results/membukkit_gen41_manifest/` (pins, replication gate with its declared
tolerance, comparison), `results/membukkit_intended_gen41_{{policy}}_{{core,stress}}-r{{1,2,3}}`
and `results/membukkit_gen41_replication_control_{{policy}}_{{core,stress}}-r{{1,2,3}}` for both
device policies.
"""
    out = ROOT / "research" / "MEMBUKKIT_INTENDED_ROUND1_GEN41.md"
    out.write_text(doc)
    print("wrote", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
