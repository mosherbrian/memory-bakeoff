# File-backed handoffs and exception-scoped duty

Tern ruling, 2026-09-22. Adopt both proposals. The supplied bill reconciliation
and seat figures are operator-reported evidence, not independently audited here.
Optimize retained context, not cache-hit rate. The primary cost target is the
verifier's repeated history; making routine control deterministic primarily
improves correctness and latency. No pricing/model change is authorized here.

## Forward-only record and message contract

Effective immediately for new Tern/cairn/kiln/corvid handoffs:
- Control TSV retains seven fields and <=200 characters per row. Column3 is
  stable action_id per ACTION-IDENTITY ruling. Evidence field is receipt path
  plus 12-character SHA256 display prefix. Full event identity is in the receipt.
- Wake messages <=300 characters: action/needed operation, receipt or instruction
  path and 12-character prefix. No pasted manifests, verdict bodies or history.
  The referenced file carries scope, authorization, full pins and deadlines.
- Full SHA256s, manifests, exact verdicts, budgets and provenance remain in
  versioned receipt/artifact files. Prefixes are navigation aids, NEVER integrity
  checks or authorization. Resolve exact path+commit/full receipt hash and compare
  full hashes using software. Ambiguous prefix/missing file/mismatch is a fault.
- Read the bound handoff and necessary evidence, not the accumulated campaign
  transcript or giant ledger. Commands save bulky output to files and return
  paths, exit status and short result summaries. Verifiers inspect actual
  artifacts and independent probes as needed; summaries never replace evidence.
- One event per actual change, no repeated acknowledgment prose or unnecessary
  model wake. Logs/receipts remain durable even when no model reads them.

Forward-only. Do not rewrite, compact or rehash old rows/messages/pinned evidence.
A short new message cannot remove tokens already retained in an old session.
This is an operating-contract addendum superseding contrary control-record
wording, not a worker source-code change or a reset of in-flight allocations.
Subsequent implementation/cutover contracts pin it; current pinned packages stay
byte-identical. Do not interrupt the present repair to reformat its history.

## Steady-state responsibilities

Software owns authorized transitions and declared branch routing, trusted
recording/hash binding, durable intent/delivery reconciliation, deadline creation
and retirement, deduplication, restart recovery, ledger/snapshot validation and
routine status. It also applies mechanical repair eligibility and remaining
budget rules: a qualifying FAIL with an explicit unused repair follows the
admitted branch without a model asking 'go'. Ambiguity is held, not guessed.
Normal successful completion/handoff must not require a cairn model turn.

Cairn remains the duty ROLE, but becomes a fresh, exception-scoped handler rather
than a campaign-long conversational controller. Invoke it for ambiguous delivery
or evidence, conflicting sources, unclear recovery eligibility and operational
anomalies requiring judgment within existing authority. It may reconcile and
resume/stop already authorized work under the package's recovery bounds. Slow
startup alone never authorizes redispatch. If policy and facts suffice, software
handles it; if judgment exceeds cairn's grant, cairn escalates to Tern.

Tern retains package admission/release authority, acceptance, terminal disposition
and successor choice, new allocations, amendments and unresolved judgments.
Cairn cannot invent work, change a question, grant time, select its own verifier,
certify its own substantive repair or extend its own recovery budget. The two
charter-wide hard stops remain unchanged. Software records and enforces these
decisions; it does not manufacture them. Worker/verifier independence remains.

## Invocation context and durable continuity

Duty invocation gets a bounded packet: incident/action/execution IDs, exact
question, current authoritative state, contract+grant pins, relevant receipts and
competing evidence, allowed actions, recovery deadline, response schema and source
paths. No campaign transcript preload. Target initial packet <=8k tokens; fetch
specific additional evidence when justified. This is a loading target, not a
license to discard contrary evidence or silently truncate a contract.
Return a structured attributable decision referencing evidence; durable incident
identity and spent budget survive a fresh session, with one active handler per
incident. Unknown/unresolved is an allowed outcome that triggers bounded escalation,
not an invitation for unlimited fresh-context retries. Provider failure uses the
same incident/deadline, never a fresh allowance.

Apply the same file-backed isolation to corvid: fresh verification invocation per
bounded pass, pinned contract/artifact manifest plus relevant prior findings and
repair history, no campaign-wide conversation. Admission and execution remain
separate invocations/roles; materially authoring a repair still disqualifies
self-certification. Fresh context alone does not establish independence or
correctness. Raw artifacts/probes are available and must be examined. Do not
preload full previous verdict chains; reference exact files and preserve all
findings, including contradictory ones, in the packet index.

## Rollout gate

No live session reset or lane switch during current P6-r2.1 repair/check. Cairn
continues manual controller duty until software passes the admitted live fixture
and Tern authorizes cutover. The normal event-driven path must not route every
handoff through cairn; that is already P6's obligation, not new scope.

Fresh per-exception/per-pass session launching, packet construction and retirement
of the campaign-long controller are explicit next cutover-contract requirements.
Before adoption independently test dispatch->session mapping, completion capture,
queue draining, unknown delivery, failure/restart and no duplicate invocation;
persist packet+decision+budgets outside sessions. Pin launcher/config/packet schema.
Do not repeat today's lost-wake lane-change failure by resetting active seats.
No new worker grant or live adoption is created by this policy ruling. At the
next package boundary Tern owns incorporating these requirements and allocating
any necessary work; Brian is not the scheduler.
