# Throughput benchmark report

**Result: 41.7 tok/s**

## What I did
1. Read `bench.sh`, `svc` and `bench.requires`. The benchmark requires `modelsrv` and `modelsrv-watchdog` to be stopped.
2. Checked status. `modelsrv`, `modelsrv-watchdog` and `modelsrv-proxy` were all active and enabled.
3. Stopped `modelsrv-watchdog` first, so it couldn't restart the server, then stopped `modelsrv`. Both used `./svc`.
4. Ran `./bench.sh`. It printed `throughput: 41.7 tok/s` and wrote `out/bench.txt`.
5. Restarted `modelsrv` and then `modelsrv-watchdog`, so both are active and enabled again as before.

`modelsrv-proxy` was not touched. It isn't in `bench.requires`.
