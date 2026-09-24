# P13-receipt-plan-1: cause of "held-awaiting-receipt" (proven from raw records)

Source: the retained private DB of the closure-2 run, /tmp/p13repoff-HZeg2h/root/p13doff1.db (read-only),
and its streams dir. Product code: internal/host/adapter.go settleOne/executionProven, internal/loop/loop.go:688-700.

1. The transport receipt is VALID. driver_kv msg:msg-D-off1-w1-1 =
   {"action": "D-off1-w1", "execution": "ex-D-off1-w1", "kind": "dispatch", "rc": 0,
    "receipt": "wake: p6-fixture-w-id -> started", "seat": "p6-fixture-w-id", "state": "sent"}
   route:D-off1-w1 = p6-fixture-w-id; exec-current:D-off1-w1 = ex-D-off1-w1. So state, action, execution
   and seat all match. The receipt guard is NOT the problem and is not changed.
2. The missing proof is the TURN: there is NO turn-seen:* key in driver_kv. executionProven requires one.
3. Why: the loop maps a stream "end" to a package by stream_key = the stream FILE NAME, and it looks the key
   up among the ACTIVE SEAT SESSION IDS (loop.go:695 active[key]). The harness wrote the turn ends to
   streams/W1.jsonl and streams/V1.jsonl, but the routed session ids are p6-fixture-w-id / p6-fixture-v-id.
   So the ends were read and matched no active seat. (Control: the accepted repair-1 witness used session
   ids W1/V1 and wrote W1.jsonl/V1.jsonl; there it worked.)
4. Also: an item id is compared with the step time when it carries a time (itemTime); the witness used
   "i<epoch-ms>". The harness now uses the same form.

Fix (test double only): the harness writes each turn end to streams/<routed session id>.jsonl with an
"i<epoch-ms>" item. No product or adapter change.
