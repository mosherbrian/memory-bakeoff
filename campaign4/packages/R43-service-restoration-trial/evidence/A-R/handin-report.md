# Throughput benchmark report (A-R)

Throughput: 41.7 tok/s (from ./bench.sh, out/bench.txt).

What I did:
- Recorded initial state: modelsrv active/enabled, modelsrv-watchdog active/enabled, modelsrv-proxy active/enabled.
- Stopped modelsrv and modelsrv-watchdog with ./svc stop (bench.requires: both must be stopped; watchdog would otherwise restart the server).
- Ran ./bench.sh successfully.
- Put the machine back: started modelsrv and modelsrv-watchdog again with ./svc start. Final state verified: modelsrv active/enabled, modelsrv-watchdog active/enabled, modelsrv-proxy untouched (active/enabled).
