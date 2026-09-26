---
name: benchmark-context-length
description: "When benchmarking models, measure throughput at 12288-token context (the length Brian's agents run at)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 507b400a-fed5-4627-a28f-8c9e75e6be14
  modified: 2026-09-26T06:25:16.706Z
---

When benchmarking models, measure throughput at a 12288-token context.

**Why:** Short-context numbers have misled Brian before: speedups vanish at realistic length. 12288 tokens is the context length their agents actually run at.

**How to apply:** Set the benchmark prompt/context to 12288 tokens by default for any model throughput comparison. Short-context runs can be added as extras, but don't report them as the headline number.
