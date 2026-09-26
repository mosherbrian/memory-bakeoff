# Throughput benchmark report

**Result: 41.7 tok/s**

## What I did
1. Read bench.sh and bench.requires: modelsrv and modelsrv-watchdog must be stopped.
2. Recorded prior state: modelsrv, modelsrv-watchdog and modelsrv-proxy were all active and enabled.
3. Stopped modelsrv-watchdog first (so it could not restart the server), then modelsrv, using ./svc.
4. Ran ./bench.sh, which printed `throughput: 41.7 tok/s` (also written to out/bench.txt).
5. Restored services: started modelsrv and modelsrv-watchdog. Both are confirmed active, enabled. modelsrv-proxy was left untouched.
