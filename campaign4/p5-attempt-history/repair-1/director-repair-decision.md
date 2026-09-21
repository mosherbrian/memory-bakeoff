# P5 acceptance withheld; existing sole repair released

Tern, 2026-09-21. Initial 54 local tests pass; corvid PASS
33ae853dc14bcb47f4bed74b1992192627104edb6e03bc400c01452f6494ca75
is preserved with all initial files in campaign4/p5-attempt-history/initial/.
archive-manifest.json binds 25 files. director-probes.py and its initial JSON
record four concrete failures in three contract requirement families.

D1 — caller attribution is trusted. A raw ingress admit claim with actor
{seat:kiln, role:reader} is admitted and persisted. No independently supplied
trusted actor context exists. Requirement 1 explicitly forbids caller override
of actor attribution. Bind attribution at the trusted adapter boundary; caller
actor claims must not choose authority. This is not OS identity isolation or
protection from arbitrary trusted Python execution. Expose and document the
trusted context versus untrusted event, including record_terminal and atomic
subevents; test a forged director/reader claim through the supported ingress.

D2 — deadline authority is partial. publish_completion accepts and persists a
verifier deadline in 2099 without a grant. start_dispatch also accepts a pinned
CHECKING grant for RUNNING when phase_hint is absent. _deadline checks only
start and compares phase only if caller supplies a hint. Derive/check every
new execution or decision/handoff deadline against trusted phase/action grants
or authorized durations, including nested verify, handoff, atomic hold/decide
and terminal routes. Determine actual phase/action from authoritative state,
not optional caller hints. No permissive fallback allocation substitutes for
an explicit authorization. Do not reject legitimate distant pinned deadlines
as occurrence skew. Preserve start-before-dispatch and unchanged replay.

D3 — restart epoch is not unique. Closing and reopening with the same clock
values produces the same epoch (UTC plus truncated monotonic). Use a genuinely
new epoch for each ingress lifetime; never compare cross-process monotonic
values. Requirement 4 also requires ambiguous restart clock continuity to get
bounded owned reconciliation: document and test that path using persisted UTC
facts, including backward UTC at reopen, without silently extending deadlines.

These are existing contract requirements, not a new package or expanded grant.
Repair the three families coherently, with regressions for each public ingress
path rather than only the listed examples. Correct old tests that encoded
caller authority with explicit rationale; preserve their lifecycle assertions.
No live effects, original accepted packages unchanged. Preserve verification.md;
corvid writes verification-repair.md and independently mutates attribution,
phase/grant/deadline variants and restart clocks through reopened stores.

Cairn is authorized to dispatch the already allocated sole <=15m worker repair,
then <=20m independent post-repair pass. Generate trusted start and deadline
before wake; arm relative --on-active timer per CHARTER. Verify archive hashes
before dispatch. On absent completion wake reconcile session evidence and exact
output hashes before timeout disposition; no silent reset. Genuine expiry:
BLOCKED, stop overdue work, wake Tern. No second automatic repair. P5 historical
ceilings remain 55 worker/40 verifier minutes; initial attempt/pass spent,
remaining repair/pass allocated here, no new allowance. P5 remains nonterminal.
P6 live integration/retirement remains gated on acceptance; no script retires.
