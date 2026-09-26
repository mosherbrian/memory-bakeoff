---
name: benchmark-context-length-12288
description: "When benchmarking models for Brian, measure throughput at a 12288-token context, not short context"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 65b2f94d-321e-466d-a64e-3bff4ba40be1
  modified: 2026-09-26T03:57:33.360Z
---

When benchmarking models, measure throughput at a 12288-token context.

**Why:** Short-context numbers have misled Brian before: speedups vanish at realistic length. 12288 tokens is the context length their agents actually run at.

**How to apply:** Set the benchmark prompt/context to 12288 tokens by default for any model throughput comparison. If also reporting short-context numbers, label them clearly as secondary.
