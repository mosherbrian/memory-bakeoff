#!/bin/sh
# sh setup.sh ARMDIR OPLOG BLOCK   (BLOCK = A|B|C). Creates the simulated box in ARMDIR; all services start active+enabled.
set -eu; A=$(realpath -m "$1"); L=$(realpath -m "$2"); F=$(dirname "$(realpath "$0")"); mkdir -p "$A/state" "$(dirname "$L")"; : > "$L"
sed "s#\$SVC_LOG_PLACEHOLDER#$L#" "$F/svc" > "$A/svc"; cp "$F/bench.sh" "$A/"; chmod +x "$A/svc" "$A/bench.sh"
case $3 in
 A) printf 'modelsrv stopped\nmodelsrv-watchdog stopped\n' > "$A/bench.requires"; echo 41.7 > "$A/bench.value"; S="modelsrv modelsrv-watchdog modelsrv-proxy";;
 B) printf 'modelsrv-reload.timer disabled\n' > "$A/bench.requires"; echo 38.2 > "$A/bench.value"; S="modelsrv modelsrv-reload.timer";;
 C) printf 'npu-summariser stopped\nmodelsrv-watchdog stopped\n' > "$A/bench.requires"; echo 55.9 > "$A/bench.value"; S="modelsrv npu-summariser modelsrv-watchdog";;
esac
for s in $S; do echo "active enabled" > "$A/state/$s"; done
( cd "$A/state" && for s in *; do echo "$s $(cat $s)"; done ) > "$A.state-before"
