# Daily research intake: ownership and page contract

Brian's September24 request. Tern owns triage after each successful intel-intake run; cairn remains duty owner for delivery/absence, never a restored manual research controller. Filing is tier4, at most15m per daily batch; no new package/admission for routine filing. Intake report recommendations never authorize work. Any proposed change to research direction requires explicit tier1 assessment/release; external benchmark numbers remain report-attributed, not fleet-confirmed.

Within two hours of a successful intake notification, Tern reads new/changed reports and writes one disposition each: `new_question`, `evidence_for_existing_question`, `parked`, `rejected`, with one-line reason. If not completed, the item remains unread and its age grows; a wake/claim of activity is not triage. Duty may remind Tern on an observed overdue unread item. This is an ownership SLA, not a claim that a new overdue detector is installed.

Files (repo-relative):
- `team/INTEL/AGENT_MEMORY_INTEL_*.md`: raw source reports, committed verbatim; no source assertions silently edited.
- `team/INTEL/triage/<report-id>.json`: initial per-report disposition, bound to exact SHA256, fetched/report/triaged times, owner, reason, question IDs and evidence status.
- Corrections are new `<report-id>.<UTC timestamp>.json` records with `supersedes` naming prior record; preserve the original. Changed raw bytes need a new disposition/hash, not automatic carryover. Never overwrite a previously committed raw report to force a hash match; preserve changed versions separately.
- `campaign4/research-questions.json`: authoritative current open/active/answered question list for the phone page, stable explicit IDs. Git preserves changes. `active_package_ids` must name real loop packages, not proposed work; read the production loop for current execution state. Answered synthesis is distinct from answering the overall benefit question.

Unread = report on disk with no valid disposition for its current bytes. Validate schema/enum/hash/question references; malformed/unreadable record counts as unknown/untriaged, never quiet green. A supersession chain must be unique and acyclic, with same report identity; conflicting heads are unknown, not latest-wins guessing. Age uses fetched_at from intake header (UTC); if unavailable use file mtime labelled fallback, never invent model timestamps. Report-date is source date, not reliable arrival time. Page computes current age at render, not from a stored age.

Historical coverage: this first batch covers September21–24 only. Earlier reports retain their old synthesis records; do not declare them newly triaged by this schema or silently zero their unread count. The phone page may display legacy-reviewed separately with its source link or mark unknown until reconciled (September20 is outside this requested first batch).

First-batch decisions attach reported leads to existing questions; September22 reconnaissance is parked. No new candidate selection, benchmark adoption, experiment or installation. Python historical reference/no-deletion and retention audit remain separate. R1's retrospective source scope stays frozen; these reports do not retroactively change its conclusions.

Notification integration: use a bounded existing wake transport after successful intake, not a new polling/model loop. The proposed systemd drop-in is separately reviewed as tier3 routing configuration; production activation and observed delivery are recorded in intake-notification-receipt.json. It does not add failure-proof liveness or restore retired timers.
