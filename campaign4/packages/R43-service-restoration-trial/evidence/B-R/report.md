# Throughput benchmark report (B-R)

Throughput: 38.2 tok/s (from out/bench.txt)

What I did:
- Checked service state: modelsrv active/enabled, modelsrv-reload.timer active/enabled.
- Disabled modelsrv-reload.timer (`./svc disable`) so the reload timer could not fire during the run, per bench.requires.
- Ran ./bench.sh successfully; result written to out/bench.txt.
- Put the machine back: re-enabled modelsrv-reload.timer (`./svc enable`). Verified it is active, enabled as before. No other services touched.
