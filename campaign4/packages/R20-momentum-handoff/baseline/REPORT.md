# R20 baseline: momentum measures, 2026-09-24T19:00Z to 2026-09-25T19:00Z

Produced by baseline/measure.py (read-only). Raw numbers: baseline/out/metrics.json. Sensitivity run: baseline/out-sens (R1 to R3 bound to stream A). Evidence extracts: events-window.json and escalations-window.json in each out dir (question/type/seat/time only; no message bodies). The SQLite snapshot was taken through the backup API and then deleted, because driver_kv can hold acknowledgement capabilities.

## Coverage and limits (read first)
- Loop events exist only for loop packages. The first event in the window is 01:17:36Z, so the first 378 minutes have no loop records. REST rows and the registry history still cover that time.
- Many packages today ran OUTSIDE the loop: Claude-authored releases R5, R9-execution-2, R10 to R13, R16, R17 and R19-prepare, plus R20 itself. Their time counts as "executing" only where a REST row covered it. So stall minutes are an UPPER bound on idle time, not a measurement of it.
- R1 to R3 carry no question_id record. The main run leaves them unbound; the sensitivity run binds them to stream A.
- Streams: A was active the whole window (legacy top question until the registry at 15:42:11Z). B was active from 16:28:53Z (151 min).
- The R18 rule did not exist before 18:38Z. "Stall under R18" asks what the new check would have called a stall, not what anyone was told.

## (a) Stall minutes (active time with no executing bound loop package and no valid rest)
| Stream | Rule | Active | Executing (loop) | Stall | Stall after first loop event |
|---|---|---|---|---|---|
| A | R11 rest rules (as live then) | 1440 | 85 (116 sens.) | 583 (553) | 206 (175) |
| A | R18 rule (<=2h, structured next step) | 1440 | 85 (116) | 1349 (1319) | 972 (941) |
| B | R11 | 151 | 4 | 4 | 4 |
| B | R18 | 151 | 4 | 128 | 128 |
The largest stream-A gap under the live rules is 19:00Z to 04:20Z, broken only by R1 to R3. That is the idle evening Brian flagged at 04:18Z ("the fleet is stopped"); R4 started at 04:20Z.

## (b) Dropped handoffs
22 loop packages started in the window. 2 were dropped (R19-PY2-C and R19-PY2-T: timed out, no claim), which is 0.9 per 10 packages. Phase sensitivity: R19-LB1-C, the third drop from the same defect, started at 19:02Z, just after the window. All three wrote an answer and then did not hand it in (delivery failure, caused by the preparation defect), not an inference stall.

## (c) Terminal decision to next dispatch, same stream
14 intervals in the main run (19 in the sensitivity run). Most are 0 to 2 min: Tern opens the successor in the same step. The long ones: R8 to R14 623.5 min (mostly out-of-loop work: R9 execution, R10 to R13, and the permission-blocked night), R14 to R18 107.4 min, R3 to R4 138.6 min (sensitivity run; the idle evening), R4-repair to R6 22 min. R15 (stream B) is right-censored: no later B dispatch in the window.

## (d) Stall escalations reaching Claude or Brian
71 escalation-ledger rows (tern 63, agent-loop 6, fleet 2). None has kind research-gap, so the checker raised no stall incident. The rows are director notices to Claude, not stall alarms; channel delivery is not recorded (the ledger is the durable record). Brian: 2 ticket files (T-103 and T-104, fleet-spend-stop budget notices, not stalls). Excluded as test pages: the two synthetic Signal pages at about 15:52Z from the old poller test harness.

## (e) Stamp honesty
Not applicable before activation. The only structured commitments are the R18 rest receipts appended at 18:38:49Z (both due at 18:46Z). They are outside the pre-stamp design and are not counted as a baseline.
