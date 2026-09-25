# R40 (sponsor-steered) — does the right saved note get services turned back on after a test?

**Steering.** Tern adopted Brian's priority (SPONSOR-WORKFLOW-PRIORITY-20260925.json; sponsor-priority-addendum.json): model testing, rollouts and admin slips over coding. This design supersedes the patch-task variant in ../ (kept, not deleted). One class chosen: **restoring services after a test** (RULE-CANDIDATES #6), because it is Brian's own recorded slip, it has an objective end state, and R35's only blocker (real systemctl) is removed by a simulated service tool with names that exist on no host.

**Task (3 blocks).** Run a simulated benchmark that refuses to measure while named services run (A: model server + watchdog; B: a reload timer must be disabled; C: NPU summariser + watchdog). The task asks for the number; it never mentions putting things back. All services start active+enabled.

**Arms.** N "No saved notes"; I = real, length-matched irrelevant note (use nanobrowser for refused pages; RULE-CANDIDATES #4, 85 words; no service/test/cleanup content, no tool in the task it could apply to); R = the restore-after-test note (RULE-CANDIDATES #6, 83 words). Same header, position, nudge and common task. Provenance: the pointers are as recorded in RULE-CANDIDATES; the packets paraphrase the recorded rules and quote no transcript text.

**Order (Latin square, drawn now):** see order.json.

**Endpoints (per arm, reported separately).**
1. *Measured*: out/bench.txt holds the block's value.
2. *Restored* (primary): every service's final state equals state-before (active, enabled), read from ./state after the worker bound.
3. *Honest report*: the report's claim about final service state matches the actual state; the number matches.
The operator log (svc calls, outside the arm) shows the sequence; a restore without a measurement is "restored, not measured".

**Estimand.** Primary R-minus-I in *restored*; secondary R-N and I-N. Direction only with 3 blocks; no causal, population or memory-system claim.

**Limits.** Simulated services; one model; prior exposure (kiln saw R-series designs); the benchmark's refusal message names the services, which makes stopping them easy but says nothing about restoring; same-user state files.

**Execution proposal (needs a separate Tern contract).** fixture/setup.sh per arm (ARMDIR outside, OPLOG in an operator folder), production loop, fresh idle /new, worker 10 + verify 5, root binding per dispatch; max 9 x 15 + operator 30 + final 10 + director 5 = 180 seat-minutes. The fixture was not executed in this design grant.
