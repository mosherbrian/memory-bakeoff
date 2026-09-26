---
name: benchmark-context-length-24576
description: "When benchmarking model throughput for Brian, use a 24576-token context length, not short contexts"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 89835ff1-4a4f-4a02-b3cf-7b6bca146abf
  modified: 2026-09-26T06:11:10.016Z
---

Measure model throughput at a 24576-token context when benchmarking.

**Why:** Short-context numbers have misled Brian before: speedups vanish at realistic length. 24576 tokens is the context length their agents actually run at.

**How to apply:** Set context/prompt length to 24576 tokens in any model benchmark or throughput comparison. If a short-context run is also included, label it clearly and don't use it as the headline number.
