action: {QID}-w1
execution: ex-{QID}-w1
attempt: a1
step: worker-run
claim: {ARTIFACTS}/{QID}-w1.json
artifacts: {ARTIFACTS}
artifact: out.bin
pinned_input: p13-fixture-decision
package: P13FIX
item: dw-{QID}
source time is recorded by the runtime, not by this task text
executable turn command (the seat runs exactly this):
decision-turn.sh --artifacts {ARTIFACTS} --claims {ARTIFACTS}/../claims --stream <bound-stream> --item dw-{QID} --action {QID}-w1 --execution ex-{QID}-w1 --step worker-run --outcome completed
