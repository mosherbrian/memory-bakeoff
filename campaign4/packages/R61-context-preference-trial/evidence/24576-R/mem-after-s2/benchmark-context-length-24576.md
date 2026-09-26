---
name: benchmark-context-length-24576
description: "When benchmarking model throughput for Brian, use a 24576-token context, not short context"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6c900677-6ca3-49ce-bf66-aa1e48c5b4af
  modified: 2026-09-26T04:09:18.409Z
---

Measure model throughput at a 24576-token context when benchmarking models.

**Why:** Short-context numbers have misled Brian before: speedups vanish at realistic length. 24576 tokens is the context length their agents actually run at.

**How to apply:** Set the benchmark prompt/context to 24576 tokens by default, and report that length alongside any throughput numbers. Only add short-context runs if asked, and label them clearly.
