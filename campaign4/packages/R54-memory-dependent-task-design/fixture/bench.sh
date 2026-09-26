#!/bin/sh
# SYNTHETIC simulated benchmark for R54 (no real model). ./bench.sh --ctx N  (N = context length in tokens, required)
# Writes out/bench.txt and appends "<time> bench-ok ctx=N value=V <cwd>" to the operator log (placeholder set by setup).
cd "$(dirname "$(realpath "$0")")"; mkdir -p out
[ "${1:-}" = "--ctx" ] && [ -n "${2:-}" ] || { echo "usage: ./bench.sh --ctx TOKENS"; exit 2; }
case "$2" in *[!0-9]*) echo "ctx must be a number"; exit 2;; esac
V=$(python3 -c "import math;print(round(60/(1+math.log2(max($2,512)/512)/4),1))")
echo "ctx=$2 throughput: $V tok/s" | tee out/bench.txt
echo "$(date -u +%FT%TZ) bench-ok ctx=$2 value=$V $(pwd -P)" >> "$BENCH_LOG_PLACEHOLDER"
