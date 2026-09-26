#!/bin/sh
# sh setup.sh ARMDIR OPLOG  -> synthetic box with only bench.sh (no services). Operator log outside the arm.
set -eu; A=$(realpath -m "$1"); L=$(realpath -m "$2"); F=$(dirname "$(realpath "$0")"); mkdir -p "$A" "$(dirname "$L")"; : > "$L"
sed "s#\$BENCH_LOG_PLACEHOLDER#$L#" "$F/bench.sh" > "$A/bench.sh"; chmod +x "$A/bench.sh"
