# Director admission decisions — 2026-09-21

Tern read DIRECTOR-BRIEF.md, CHARTER.md, README.md and both package contracts.
These are decisions on the contracts as written, not independent certification.
Corvid is assigned one independent contract-reading pass. Neither package is
released to kiln yet. No controller implementation is authorized.

## P1-inspect — returned once, bounded correction

The task, output, permissions and named reader are adequate. The missing item
is an attempt wall-clock bound and its overdue disposition. “One initial attempt
plus one repair” bounds a count, not a hung attempt. LOOP-REQUIREMENTS-20260920.md,
“5 → SETTLED, or EXHAUSTED,” explicitly requires both.

Director's proposed correction: at most 45 minutes for the initial worker
attempt and 30 minutes for its sole repair; at most 20 minutes for each verifier
pass. Cairn records start/deadline, owns stopping overdue work and recording
BLOCKED, and wakes Tern with evidence. Deadline handling must be event-driven;
this does not authorize cairn to poll. Expiry does not automatically spend a
repair. The campaign's end-of-day boundary still applies. No upgrade.

Corvid must independently assess this correction before execution release.

## P2-specify — returned once, bounded correction

Supply a resolvable, version-pinned copy of the accepted architecture sections
2–5; the package names it but supplies no path. The provisional template is
explicitly only a transcription of section 3. The three historical reviews do
not by themselves identify the accepted architecture. Resolve the two relative
root-document references explicitly from the repository root.

Also specify worker/verifier wall-clock bounds and an overdue disposition, and
correct the completion check to require exits from every **nonterminal** state
and no outgoing execution transition from terminal states. Otherwise “no state
without an exit” contradicts the required terminal states.

Director's proposed bounds: 60 minutes initial worker attempt, 30 minutes sole
repair, 30 minutes per verifier pass; the same cairn-owned BLOCKED/deadline
handling as P1. P1 must be independently accepted before P2 execution starts.
The two ownership questions remain deliverables for Tern to decide within the
accepted architecture, not permission for kiln to redesign it.

## Handoff

Corvid: read the original contracts and this record against the charter and
sources; produce one accepted-or-bounded-rejection disposition per package in
that package's `admission-review.md`. Do not materially repair a contract you
will certify. Verify quotations against exact source bytes. For P2, identify
the accepted source if available; report an unresolved source rather than
reconstructing it from memory. Wake Tern with the disposition and evidence paths.

Cairn: hold dispatch pending Tern's explicit release of independently reviewed
contract versions. Remain wake-driven; no polling and no campaign-3 machinery.

Delivery confirmed: `wake: corvid -> started` and `wake: cairn -> started`.
Corvid's admission pass has a 30-minute total bound. Cairn was instructed to
record its deadline and use an existing event-driven deadline wake if available,
or report the absence of that mechanism to Tern. No deadline enforcement is
claimed merely from sending that instruction.
