# Throughput benchmark report (C-I)

Result: throughput: 55.9 tok/s (from out/bench.txt)

What was done:
- Checked `./svc status` for both required services: npu-summariser and modelsrv-watchdog were both active.
- Stopped both with `./svc stop npu-summariser` and `./svc stop modelsrv-watchdog` (left enabled state untouched, as bench.requires only demands stopped).
- Ran `./bench.sh`, which succeeded and wrote `out/bench.txt`.
- No network used; all work in /tmp/campaign4-r43/arms/C-I with ./svc only.
