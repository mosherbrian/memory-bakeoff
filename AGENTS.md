# Codex instructions for this repository

Start with `STATUS_AND_FINDINGS.md`, then `CODEX_HANDOFF.md`.

## Non-negotiable evaluation rules

- Treat the evaluated system as the complete **engine + ingestion mode + models + runtime + harness + tools + environment**.
- The harness owns ground truth and grading. Never use model self-report as the score.
- Preserve the distinction between `baseline`, `controlled_core`, `raw_product`, and `product` results.
- Never silently replace an unavailable product dependency with a fake and publish the result as the product.
- Do not overwrite completed result directories or archived sidecar traces. Add new result directories.
- Record exact package/commit, embedding model, reranker, LLM/extractor, database/vector backend, thresholds, top-k/context budget, and host/runtime versions for every external result.
- Source provenance is a release gate. Returned evidence must map reliably to canonical benchmark record IDs before a score is considered publishable.
- Report memory lifecycle behavior separately from retrieval. In particular, false merge/supersession must not be rewarded as better retrieval.
- Always report exact returned context size and harmful/prohibited presence; do not rely on prohibited fraction alone.
- Before changing benchmark semantics, run the existing tests and inspect whether the proposed change invalidates prior result comparability.

## Current test gate

The handoff snapshot is expected to pass:

```bash
# Authoritative gate on any host. Must be fully green.
PYTHONPATH=src pytest -q tests/test_gen109_reader_interference.py \
  tests/test_gen110_reader_execution.py tests/test_gen111_reader_v2.py \
  tests/test_gen112_reader_v3.py tests/test_gen113_reader_v4.py \
  tests/test_gen115_adjudication.py tests/test_gen116_reader_v5.py
# 245 passed  (reader-interference lineage, 2026-09-06)

# Whole suite. Needs sklearn and pandas, which are NOT installed on every host.
PYTHONPATH=src pytest -q --continue-on-collection-errors
# 1082 passed, 18 failed, 6 skipped, 47 errors  (2026-09-06)
```

**The whole-suite figure is not green and has not been for some time.** The 18
failures and 47 collection errors trace to four causes, none of them in the
reader-interference line: missing result artifacts, the absent
`external/MemConflict` dataset, assertions pinning macOS paths, and missing
`sklearn`/`pandas`. Treat the lineage gate as the one that must pass; investigate
any *change* in the whole-suite numbers rather than the numbers themselves.

The "97 passed" figure that stood here until 2026-09-06 was a Gen28 snapshot. It
was reported stale by review three separate times before anyone fixed it.

## Preferred next work

1. Run Hindsight v0.9.2 faithfully on a normal networked host.
2. Run MemBukkit with intended pretrained encoder/reranker.
3. Run Mem0 with explicit real Qdrant/embedder/BM25 configuration.
4. Run agentmemory full service while preserving lifecycle metrics.
5. Run Claude-Mem's actual compression worker and compare default vs long-range retrieval.
6. Feed validated third-party retrieval into the existing deterministic reader evaluation.

See `CODEX_HANDOFF.md` for exact guidance and stop conditions.

## Existing findings to protect

- agentmemory controlled lifecycle: 418/450 stress distractors falsely superseded (92.9%).
- MemBukkit controlled bucket routing: same shared-LSA stress Hit/all-relevant as full dense scan while opening ~32.9% of the bank.
- Claude-Mem controlled semantic policy: implicit 90-day window reduces Hit@5 to 0.208; disabling the window restores the dense-LSA result.
- Habitus real runtime: stress Hit@5 0.792 with prohibited@5 0.025.
- Baseline real reader trace: BM25 12/14, TF-IDF 12/14 with one prohibited stale answer, dense LSA 14/14, hybrid RRF 14/14.

Do not reinterpret these as full product scores where the docs label them controlled arms.

