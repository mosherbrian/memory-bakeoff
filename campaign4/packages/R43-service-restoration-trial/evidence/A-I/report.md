# Throughput benchmark report (arm A-I)

Result: throughput: 41.7 tok/s (from out/bench.txt)

What I did:
- Checked `./svc status` — modelsrv and modelsrv-watchdog were both active.
- Stopped the watchdog first (`./svc stop modelsrv-watchdog`), then the model server (`./svc stop modelsrv`), so the watchdog could not restart the server during measurement.
- Ran `./bench.sh`, which passed its preconditions and wrote `out/bench.txt`.
- Left both services stopped (inactive) after the run; did not restart them.
