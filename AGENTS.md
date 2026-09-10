# Codex instructions for this repository

**Reading order (reset, current):** `RESET_PLAN.md` (the governing reset
instruction) → `RESET_STATUS.md` (the one current status and decision page).
Everything below the non-negotiable rules is historical context from the
pre-reset generation loop; where the two differ, the reset documents win.

**The automated generation workflow is suspended** (2026-09-09,
`control-plane/PENDING.json` status `paused`). Do not deliver reset work
through consume-instruction, await-instruction, decide, doorbell, ring,
converge, after-converge, overnight or fallback-proposing scripts. The reset
uses direct, bounded handoffs described in RESET_PLAN.md.

## Current task (reset)

R1 (make the project legible, deliver the pilot recommendation) is on branch
`reset/practical-pi-20260907`. R2 — one bounded pilot over Brian's live
Pi/Pi-LCM setup, specified in RESET_STATUS.md — begins only after Brian's
explicit pilot-scope decision. The old "Preferred next work" list below is
superseded and retained as history.

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

## Test gate (reset policy — supersedes the per-generation mandate below)

For this reset, verification is scoped (RESET_PLAN.md §7):

- Documentation-only changes need direct source/diff checks, not suite runs.
- Run focused tests only where a changed document or field is actually
  consumed by code. Do not rerun the whole historical suite to edit a status
  page.
- For R2 code, run the focused tests covering the changed boundary plus one
  relevant regression path. A critical new check must reject one
  representative bad input through the real path it protects.
- Never disable installed hooks or use `--no-verify` to pass a gate.

The known-failure description below is reconciled with
`tests/KNOWN_FAILURES.json` (measured 2026-09-07, Gen125: 1557 passed, 26
failed, 3 skipped, 5 errors — 8 membukkit run-provenance, 16+5 absent
MemConflict dataset, 2 frozen-source drift after Gen123). Match failures by
test identity and cause; do not copy an old pass count as a current run.

## Historical test gate (pre-reset)

The handoff snapshot is expected to pass:

```bash
# Authoritative gate on any host. Must be fully green.
PYTHONPATH=src pytest -q tests/test_gen109_reader_interference.py \
  tests/test_gen110_reader_execution.py tests/test_gen111_reader_v2.py \
  tests/test_gen112_reader_v3.py tests/test_gen113_reader_v4.py \
  tests/test_gen115_adjudication.py tests/test_gen116_reader_v5.py
# 245 passed  (reader-interference lineage, 2026-09-06)

# Whole suite. Needs scikit-learn and pandas (declared in pyproject).
# `python -m pytest`, NOT bare `pytest`. Three tests import from `scripts.`, which
# resolves only when the working directory is on sys.path - which `-m` does and
# the bare entry point does not. Bare `pytest` gives 27 failed / 1472 passed, and
# an agent following this file verbatim would reasonably read those three as a
# new regression. Found by glm-5.3 at Gen120 round 5.
PYTHONPATH=src:vendor/membukkit/src python -m pytest -q --continue-on-collection-errors
# 1557 passed, 26 failed, 3 skipped, 5 errors  (2026-09-07, Gen125)
# Pinned by tests/test_preregistration_numbers_are_real.py against
# tests/KNOWN_FAILURES.json - this line cannot go stale silently again.
```

**The whole-suite figure is not green, and every remaining failure has a known
external cause.** As of 2026-09-06 they are exactly two clusters:

- **16 items** (`test_memconflict_gen36/37/38`): the pinned MemConflict dataset
  is absent. It is 182 MB of upstream data at `external/MemConflict/`, correctly
  not committed, and it must be fetched to run those tests.
- **8 items** (`test_membukkit_gen41_round1`): these assert on RUN PROVENANCE -
  `device_proof`, an empty `load_trace.downloads` - and need artifacts from real
  recorded runs. No path setting can satisfy them.

  `membukkit` itself is no longer missing. Gen120 put `vendor/membukkit/src` on
  the pytest path: that directory is the repo's OWN copy, pinned to commit
  `f28a2e58` with blob SHAs verified against upstream. That is configuration, not
  substitution. `pip install membukkit` would have been the substitution, pulling
  an unpinned build into a module whose entire job is raising `FallbackDetected`
  when something stands in for the intended artifact. Recovering those 14 tests
  cost nothing and changed no engine.

Nothing else fails. Treat the lineage gate as the one that must pass, and treat
any failure outside those two clusters as a real regression.

Earlier snapshots of this file were wrong in ways worth recording. "97 passed" was
a Gen28 figure that survived three review reports. A later note claimed the
failures traced to "missing result artifacts, macOS path assertions, and missing
sklearn/pandas": the artifacts turned out to be nine evidence directories that
existed only on one laptop and are now committed, and the macOS-path claim was an
artefact of grepping pytest OUTPUT rather than source — there is one such path in
the repo and it is an overridable default.

The "97 passed" figure that stood here until 2026-09-06 was a Gen28 snapshot. It
was reported stale by review three separate times before anyone fixed it.

## Preferred next work (SUPERSEDED 2026-09-09 — historical)

> Superseded by the reset: the current queue is in `RESET_STATUS.md`. This
> list is retained as history of where the pre-reset loop was pointed.

1. Run Hindsight v0.9.2 faithfully on a normal networked host.
2. Run MemBukkit with intended pretrained encoder/reranker.
3. Run Mem0 with explicit real Qdrant/embedder/BM25 configuration.
4. Run agentmemory full service while preserving lifecycle metrics.
5. Run Claude-Mem's actual compression worker and compare default vs long-range retrieval.
6. Feed validated third-party retrieval into the existing deterministic reader evaluation.

See `CODEX_HANDOFF.md` for exact guidance and stop conditions.

## Existing findings to protect

- agentmemory controlled lifecycle: 418/450 stress distractors falsely superseded (92.9%).
- MemBukkit controlled bucket routing: same shared-LSA stress Hit/all-relevant as full dense scan. The scan fraction for this configuration was never measured; the ~32.9% figure is RETRACTED (research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md).
- Claude-Mem controlled semantic policy: implicit 90-day window reduces Hit@5 to 0.208; disabling the window restores the dense-LSA result.
- Habitus real runtime: stress Hit@5 0.792 with prohibited@5 0.025.
- Baseline real reader trace: BM25 12/14, TF-IDF 12/14 with one prohibited stale answer, dense LSA 14/14, hybrid RRF 14/14.

Do not reinterpret these as full product scores where the docs label them controlled arms.

