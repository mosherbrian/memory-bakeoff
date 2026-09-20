# Stage-two decision_pending contract

Defined by Tern, 2026-09-19, on Brian's explicit requirement. Specification only; stage one and its random-60 checkpoint remain unchanged.

## Extraction boundary

Add `decision_pending` to the stage-two statement-kind vocabulary. Emit it when the supplied text explicitly identifies an unresolved question, choice or approval AND names its responsible person or seat. Capture the exact question or approval request, including the heading/table context that supplies its owner. A declarative request such as "Brian must choose the campaign window" qualifies; preserve that wording rather than inventing a question. A vague alias such as "campaign-2 scope call" may be recorded as a pending-decision reference, but must not be expanded into invented options or treated as a second independent decision.

A proposal recommends work; it is not automatically a decision awaiting Brian. A decision_record reports an actual answer, selection, rejection, deferral or authorization. An operational failure (missing file, expired credential, HTTP failure) is not decision_pending unless the source separately requests an owned choice or approval. If an unresolved question has no stated owner, record it as an unassigned open question for review; do not guess Brian.

## Extracted fields

- `statement_id`: identity tied to the exact source version and span.
- `kind`: `decision_pending`.
- `question_verbatim`: exact source wording, not a paraphrased blocker name.
- `owner_verbatim`: stated owner(s); shared ownership stays shared.
- `scope_verbatim`: pilot/campaign/system/data limits when explicit; otherwise null.
- `source`: path, full content hash, supporting quote(s), line/offset spans. Multiple spans may link an owner heading to a question below it.
- `aliases_verbatim[]`: alternate names explicitly stated in this source; otherwise empty.
- `blocked_work_refs[]`: explicitly linked work only, with supporting spans.
- `reported_status`: `pending` — this describes the source assertion, not present-day truth.
- `uncertainties[]`: missing scope, unclear owner, unresolved alias, partial input or conflicting wording.

All extraction records retain model, prompt and extractor versions. A locally extracted pending claim is never itself an authoritative present-day blocker.

## Resolution across files

Resolve extracted requests against decision records in a separate reference-chasing pass. Keep a stable decision identity and evidence-backed membership links so the same request under multiple aliases is not counted repeatedly. Similar wording or a newer date alone cannot merge or close decisions.

Each resolution link records the request and answer statement IDs, the answer's exact evidence, actor/authority as evidenced, applicable scope, source versions, and review status (`proposed`, `confirmed`, `disputed`). Do not infer authority from a filename or author seat. Broad charter approval does not automatically authorize private data, a separate campaign, or spending.

Derived current states: `pending`, `resolved`, `deferred`, `not_applicable`, `conflicted`, `unresolved_reference`. "Not yet" is an explicit deferral, not approval. Resolve each question separately; a pilot answer must not close the scale-up question. If the resolution is not confirmed, keep the item visible as needing review rather than silently removing it.

## Query behavior and recomputation

"What is waiting on Brian?" returns deduplicated pending decisions naming Brian, their exact questions, blocked work, source links, and resolution uncertainty. Show shared ownership explicitly. Present deferred/no-authorization items separately, with any stated revisit trigger; do not repeatedly portray them as unanswered immediate requests. Resolved and not-applicable items leave the action list but remain available in history with their answers. Conflicts and unresolved references remain visible in a review section.

Changing a question, answer or authority source invalidates dependent resolution links and query views. Re-reading unchanged old questions alone will not discover that they were answered elsewhere: recompute the dependency closure, including new decision records. Invalidation produces "needs review", not automatic reopening or approval. Hashes and citation edges preserve provenance; semantic resolution remains checked judgment.

## Acceptance examples

- Local outcome pilot: four original questions link to `../OUTCOME-FIRST-RUNG-SCOPE-20260919.md`; pilot scope is resolved, Design B is not applicable, numeric run limits are Tern-owned preparation, private-transcript scale-up is deferred and unauthorized.
- Perseus: conflicting write policies require scope and authority reconciliation; a newer config alone must not erase an older approval requirement.
- SWE-chat: an asserted absent credential is an operational claim, not a decision Brian owes. Existing authorization and transfer failure must be represented separately.
- An answered request under a different name must leave the action list only after the scope-matched answer link is confirmed; its historical pending statement is retained.
