# MemBukkit intended models on the frozen Round1 raw-product ruler

**Evidence class:** existing `raw_product`, configuration-scoped to *MemBukkit intended models*.
This is a within-product model-weight ablation on a frozen ruler, not a new lane. It does not
replace the Gen8 documented-fallback row, which stands unchanged, and it says nothing about
MemBukkit's quality on any other benchmark.

Gen40 proved the intended MemseekAI pair loads and runs. Gen41 asks the only question that
proof unlocked: on the same corpus, scorer, provider, ingest surface, retrieval configuration
and device policy, what do the intended weights do that the documented fallback pair did not?

## What was held fixed

MemBukkit source `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` — the Gen7/Gen8/Gen40 pin, unchanged. Ingest through
upstream `MemorySystem.ingest_facts`, one benchmark record per atomic fact, no distiller and no
LLM. Retrieval exactly as the committed provider freezes it: `union_lanes=("atomic",)`,
`bucket_mode=topic`, `num_buckets=24`,
`scan_budget=0.3`, `select="hybrid"`,
`rerank_cap=50`, `top_k=10`,
`k_rrf=60`, `lexical_lane=False`, in-memory backend, Round1 scorer
consuming the top 5. Asserted at the start of every scored run, not assumed.

## Device, which had to be closed first

`research/MEMBUKKIT_FALLBACK_GEN8.md` records that Gen8 ran on CPU, and Gen40 measured that the
historical encoder wrapper never passes `ModelConfig.device` to `SentenceTransformer`, so the
bi-encoder auto-selects an accelerator while the reranker honours the request. Left alone that
would have made device a second variable inside a model-weight ablation, so Gen41 set out to
force both models onto CPU.

The replication control says that plan was built on a wrong premise. Under a forced CPU the
stress condition does **not** reproduce Gen8: MRR 0.5535 to 0.5431, and 9 of 26 queries come back
reordered. Under the product's own device selection it reproduces Gen8's committed metrics
exactly, in both conditions. Gen8's models therefore ran on the accelerator, whatever its
document says. The claim was never checked at the time because nothing depended on it until now.

Device therefore cannot be both "equal to Gen8" and "CPU". Rather than pick one and lose the
other, Gen41 runs **both policies**, each internally matched across the two model
configurations, and declares that tolerance before reading any intended-model result:

- `product_default` — the product selects the device, which is what Gen8 did. Proven devices:
  bi-encoder ['mps:0'], reranker
  ['mps:0'].
- `cpu` — a harness-owned shim supplies a device at the model constructor boundary where the
  caller supplied none. Proven devices: bi-encoder ['cpu'], reranker
  ['cpu'].

The shim touches no weight, tokenizer, pooling, precision or retrieval parameter, and the device
is read off each constructed model rather than trusted, on all twenty-four scored runs. Because
each policy is internally matched, each is a valid model-weight ablation on its own; the pair
also shows whether the answer survives the device choice.

## Model pins

| configuration | role | repository | revision | files loaded | mismatched files |
| --- | --- | --- | --- | --- | --- |
| fallback_control | encoder | `sentence-transformers/all-mpnet-base-v2` | `e8c3b32edf54` | 11 | 0 |
| fallback_control | reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | `233902d25c44` | 6 | 0 |
| intended | encoder | `MemseekAI/membukkit-biencoder-v1` | `50ab0a1fefa4` | 12 | 0 |
| intended | reranker | `MemseekAI/membukkit-reranker-v2` | `0b46ab535caa` | 7 | 0 |

Only loader files are downloaded for the fallback pair; the ONNX, OpenVINO and duplicate `.bin`
exports in those revisions are never touched, so reconciliation is scoped to the downloaded
manifest and says so. One provenance detail worth recording: the fallback reranker id named in
the pinned MemBukkit source, `cross-encoder/ms-marco-MiniLM-L-6-v2`, now redirects — Hugging Face
renamed the repository to `ms-marco-MiniLM-L6-v2`. The revision is unchanged, and the pinned
revision resolves under the new name.

## Replication gate — run before the intended models saw the ruler

| condition | policy | metric differences vs Gen8 | queries with different returns | repeat returns identical | provenance clean |
| --- | --- | --- | --- | --- | --- |
| core | product_default | 0 | 0 | True | True |
| core | cpu | 0 | 0 | True | True |
| stress | product_default | 0 | 2 | True | True |
| stress | cpu | 1 | 9 | True | True |

The gate passes on a declared tolerance, not on silence: the product-default control must
reproduce Gen8 exactly — which is what proves harness, corpus, scorer, ingest and retrieval
equivalence — and the CPU control's deviation must be confined to what the device change itself
moves. The CPU deviation is published above as its own quantity rather than absorbed into a pass.

Committed Gen8 anchor: core Hit@5 1.0000, MRR 0.5854;
stress Hit@5 0.8750, MRR 0.5535.

## Result

| device policy | condition | metric | fallback control | intended | delta |
| --- | --- | --- | --- | --- | --- |
| product_default | core | hit@5 | 1.0000 | 1.0000 | 0 |
| product_default | core | mrr | 0.5854 | 0.6417 | +0.0563 |
| product_default | core | all_relevant@5 | 1.0000 | 0.9583 | -0.0417 |
| product_default | core | prohibited@5 | 0.1250 | 0.1083 | -0.0167 |
| product_default | core | useful_before_harmful | 0.6875 | 0.6875 | 0 |
| product_default | core | mean_context_chars | 378.0385 | 404.3846 | +26.3462 |
| product_default | stress | hit@5 | 0.8750 | 0.9167 | +0.0417 |
| product_default | stress | mrr | 0.5535 | 0.4486 | -0.1049 |
| product_default | stress | all_relevant@5 | 0.7500 | 0.8333 | +0.0833 |
| product_default | stress | prohibited@5 | 0.0667 | 0.0583 | -0.0083 |
| product_default | stress | useful_before_harmful | 0.6923 | 0.7143 | +0.0220 |
| product_default | stress | mean_context_chars | 500.8846 | 510.4231 | +9.5385 |
| cpu | core | hit@5 | 1.0000 | 1.0000 | 0 |
| cpu | core | mrr | 0.5854 | 0.6417 | +0.0563 |
| cpu | core | all_relevant@5 | 1.0000 | 0.9583 | -0.0417 |
| cpu | core | prohibited@5 | 0.1250 | 0.1083 | -0.0167 |
| cpu | core | useful_before_harmful | 0.6875 | 0.6875 | 0 |
| cpu | core | mean_context_chars | 378.0385 | 404.3846 | +26.3462 |
| cpu | stress | hit@5 | 0.8750 | 0.9167 | +0.0417 |
| cpu | stress | mrr | 0.5431 | 0.4556 | -0.0875 |
| cpu | stress | all_relevant@5 | 0.7500 | 0.8333 | +0.0833 |
| cpu | stress | prohibited@5 | 0.0667 | 0.0583 | -0.0083 |
| cpu | stress | useful_before_harmful | 0.6923 | 0.7143 | +0.0220 |
| cpu | stress | mean_context_chars | 500.8846 | 510.3846 | +9.5000 |

Retrieval latency, operations only, mean ms per query:

| device policy | condition | fallback control | intended |
| --- | --- | --- | --- |
| product_default | core | 72.4 | 65.7 |
| product_default | stress | 256.8 | 256.7 |
| cpu | core | 68.1 | 72.0 |
| cpu | stress | 333.6 | 334.8 |

## Stability

| device policy | condition | control returns identical across repeats | intended returns identical across repeats | queries where the two configurations differ |
| --- | --- | --- | --- | --- |
| product_default | core | True | True | 22 |
| product_default | stress | True | True | 26 |
| cpu | core | True | True | 22 |
| cpu | stress | True | True | 26 |

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

Contract `src/memory_bakeoff/membukkit_gen41.py`, sha256 `2a9829e58e944f7d525f0ef212b0db8e9cc6e9874f12b75f3f5f3044ac5625d5`.
Artifacts: `results/membukkit_gen41_manifest/` (pins, replication gate with its declared
tolerance, comparison), `results/membukkit_intended_gen41_{policy}_{core,stress}-r{1,2,3}`
and `results/membukkit_gen41_replication_control_{policy}_{core,stress}-r{1,2,3}` for both
device policies.
