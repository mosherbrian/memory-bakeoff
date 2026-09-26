# Throughput benchmark report (C-R)

Result: 55.9 tok/s (from out/bench.txt: "throughput: 55.9 tok/s").

What I did (all in /tmp/campaign4-r43/arms/C-R, using ./svc only):
- Checked initial state: npu-summariser active/enabled, modelsrv-watchdog active/enabled, modelsrv (model-server) active/enabled.
- Stopped npu-summariser and modelsrv-watchdog for the measurement (left modelsrv running; no disables needed — bench only requires stopped).
- Ran ./bench.sh; it succeeded and wrote out/bench.txt.
- Restored the box: started and re-enabled npu-summariser and modelsrv-watchdog. Verified final status: both active/enabled, modelsrv untouched (active/enabled).
