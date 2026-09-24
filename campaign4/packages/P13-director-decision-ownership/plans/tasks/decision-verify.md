action: {QID}-v1
execution: ex-{QID}-v1
attempt: a1
step: verify-run
claim: {ARTIFACTS}/{QID}-v1.json
artifacts: {ARTIFACTS}
worker_claim: {ARTIFACTS}/{QID}-w1.json
check: recompute-sha256
package: {QID}
item: dv-{QID}
source time is recorded by the runtime, not by this task text
executable turn command (the seat runs exactly this):
decision-turn.sh --artifacts {ARTIFACTS} --claims {ARTIFACTS}/../claims --stream <bound-stream> --item dv-{QID} --action {QID}-v1 --execution ex-{QID}-v1 --package {QID} --step verify-run --outcome completed
