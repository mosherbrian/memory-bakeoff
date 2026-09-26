#!/bin/sh
# SYNTHETIC simulated benchmark for R54 (no real model). ./bench.sh --ctx N  (N = context length in tokens, required)
# Writes out/bench.txt and appends "<time> bench-ok ctx=N value=V <cwd>" to the operator log (placeholder set by setup).
cd "$(dirname "$(realpath "$0")")"; mkdir -p out
[ $# -eq 2 ] && [ "$1" = "--ctx" ] || { echo "usage: ./bench.sh --ctx TOKENS"; exit 2; }   # R56: exactly two arguments
case "$2" in ""|*[!0-9]*) echo "ctx must be a positive integer"; exit 2;; esac
[ "$2" -ge 1 ] && [ "$2" -le 1048576 ] || { echo "ctx out of range"; exit 2; }
V=$(python3 -c "import math;print(round(60/(1+math.log2(max($2,512)/512)/4),1))")
echo "ctx=$2 throughput: $V tok/s" | tee out/bench.txt
echo "$(date -u +%FT%TZ) bench-ok ctx=$2 value=$V $(pwd -P)" >> "/tmp/r59-op-empty_dir/o-eb121175a31b/log"
