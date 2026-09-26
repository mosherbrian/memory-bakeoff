---
name: bench-prefs
description: how Brian wants model throughput benchmarks run
metadata:
  type: feedback
---

Measure model throughput at a 12288-token context, not at short context. Short-context speedups have misled Brian before; 12288 is the length his agents actually run at.
