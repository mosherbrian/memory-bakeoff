# Throughput benchmark report (arm A-N)

Result: **41.7 tok/s** (from `out/bench.txt`: "throughput: 41.7 tok/s").

What I did:
1. Checked status: `modelsrv` and `modelsrv-watchdog` were both active.
2. Stopped the watchdog first (`./svc stop modelsrv-watchdog`), then the server (`./svc stop modelsrv`), so the watchdog could not restart the server during measurement.
3. Ran `./bench.sh`, which succeeded and wrote `out/bench.txt`.
4. Left `modelsrv-proxy` untouched (not listed in `bench.requires`).
