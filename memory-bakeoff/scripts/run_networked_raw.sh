#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-results/networked-raw}"
mkdir -p "$(dirname "$OUT")"
memory-bakeoff probe | tee "${OUT}.probe.json"
memory-bakeoff run \
  --providers bm25,dense_lsa,hybrid_rrf,mem0,agentmemory,membukkit,habitus,claude_mem,hindsight \
  --mode raw --top-k 5 --out "$OUT"
