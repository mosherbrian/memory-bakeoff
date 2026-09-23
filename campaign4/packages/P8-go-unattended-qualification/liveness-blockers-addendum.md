# P8 liveness blockers — corroboration and classification
Tern, 2026-09-23T06:04:49.503857+00:00. Source remains
agent-loop71318c4e7a0ed142acd61d4553f31e5bad0fb474. No code change or allocation.

Claude independently inspected and reported two gaps already covered by P8's
terminal NOT READY decision. Director inspection of internal/loop/liveness.go
and the oneshot unit confirms the paths; Claude's report is not a new live test.

1. Damaged or unreadable <db>.liveness.json causes loadState/Check to return before
assessment. CLI exits1 and sends nothing; the failed oneshot has no OnFailure
notification. This is a missed-fault/ownership blocker, not a satisfactory
fail-closed liveness outcome. Corvid's narrow observation that malformed state
returns nonzero is true; it does not prove owned escalation. The terminal report
already cautions against that inference. Classify this explicitly NOT READY.
2. A future heartbeat (including host clock rollback after a real write) has
negative age and is treated as fresh, suppressing detection until clock catches
up. Explicit NOT READY, consistent with Corvid's reproduced false REST.
3. Process-incarnation binding remains separately unresolved. That a replacement
normally overwrites the record on its first pass does not establish safety before
that pass completes. Recent evidence from the previous process cannot certify the
current one. Do not remove this existing blocker based on the normal path.

Ordinary past heartbeat older than100s is detected; no claim that every stale
record is missed. Fix line count does not supply qualification evidence or renew
P8's spent single repair. No further P8 repair, new candidate pin, or P8-r2 is
released. Main and installed binary remain unchanged. Any later explicit safety
allocation must reproduce these failures and requalify the affected checker and
live behavior. If damaged state is quarantined in such future work, preserve the
original bytes/evidence and incident continuity; do not silently reset ownership.

P9 carries these blockers in its supervised-preview docs/status qualification
limits under its existing known-limits obligation. This addendum adds evidence
and classification, not control-code scope. P8 terminal/source hashes and P9's
pinned inputs are preserved; no in-place rewrite of historical verdicts. P9 may
not hide these repairs in packaging. No adoption or script retirement.
