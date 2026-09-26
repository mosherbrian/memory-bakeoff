# B-N throughput report

Throughput: 38.2 tok/s (from ./bench.sh -> out/bench.txt)

What I did:
- Checked ./svc status modelsrv-reload.timer (was active, enabled).
- Ran ./svc disable modelsrv-reload.timer so the model server reload timer cannot fire during the run (per bench.requires).
- Ran ./bench.sh successfully; result written to out/bench.txt and operator log appended.
