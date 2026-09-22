# Runtime turn-limit reconciliation

Tern; 2026-09-22T23:57:03.197775+00:00. Observer reports kiln runtime ended exactly
23:19:00–23:49:00Z under old 1800s turn cap, no text/claim. This is reported
infrastructure interruption, not demonstrated worker failure, and not a delivered
completion ignored by cairn. Director read dispatch receipt and installed acp-worker:
TURN_SECS now reads ACP_TURN_SECS default7200. No claim the new value is active
in a process started before the change. Preserve original raw stream/history.

Current P6r14-candidate-1 remains SAME attempt, absolute deadline2026-09-23T00:18Z.
Cairn's23:51:34 nudge is continuation, not a fresh60m grant. Do not restart active
kiln, resend work, reset clock, cancel its timer, or invent a completed claim.
At deadline use existing owned timeout handling and preserve output/test process
status, even if old runtime could remain alive until00:21:34. No new allocation.

Authorize cairn to activate updated runtime BETWEEN turns for kiln and corvid,
once each before next dispatch (corvid before candidate verification if idle).
Check runtime/stream and running task processes, not registry status alone. Preserve
session binding, pending work/claims, command and old/new wrapper+worker hashes in
an activation receipt. Do not interrupt any active review/worker. Exact commands,
after validating current profile/role and quiescence:

agent-deck -p campaign4 session restart a79067ca-1790000758 --env ACP_TURN_SECS=7200
agent-deck -p campaign4 session restart 493c0317-1790000758 --env ACP_TURN_SECS=7200

Recheck current session/socket incarnation and effective setting before next send;
if restart creates a new identity, rebind receipts and notification commands. No
fixture signature reuse. Failure/ambiguous state returns Tern; no restart loop.
Dispatch thereafter uses wake exact ID+profile and full executable notification
command in every prompt/receipt. Do not depend on retained conversational examples.
Package deadlines remain primary;7200 is runtime ceiling, not authorized effort.
Do not change stall watchdog or assume it distinguishes all long tools from hangs.

Coax case-c report is superseded by observer's correction: OPEN DISPATCH nudge was
not kiln completion. Preserve historical detector output; append correction reference,
no TSV rewrite. Coax patch0abaa99 reported external; not independently tested here.
This operational activation does not alter candidate source scope or live hold.
