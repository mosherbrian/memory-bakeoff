#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-results/product}"
mkdir -p "$(dirname "$OUT")"
memory-bakeoff probe | tee "${OUT}.probe.json"
memory-bakeoff run \
  --providers bm25,dense_lsa,hybrid_rrf,mem0,agentmemory,membukkit,habitus,claude_mem,hindsight \
  --mode product --top-k 5 --out "$OUT"
