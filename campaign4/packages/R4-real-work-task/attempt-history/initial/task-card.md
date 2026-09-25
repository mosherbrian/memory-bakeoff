# Task card: re-issue the S13-2G audit gate so an honest audit passes

## (1) Real request and why it matters

`team/CORVID-S13-2G-VERIFY.md` (corvid, 2026-09-20) returns the gate to the
writer twice: round 1 demands fabricated mechanism sections for 4
non-mechanisms; the round-2 re-issue regresses to ~73 demanded sections
("Caveats", "JavaScript", …). An unsatisfiable gate blocks the S13-2 audit
row forever while a green selftest claims health. Fixing it unblocks real
audit work and removes a known-bad check from the fleet's gate set — the
recurring gate-repair kind of fleet work, not a benchmark score.

## (2) Starting snapshot and deliverable

Start: `team/S13-STATEUPD-AUDIT/check.py` (untracked working copy, sha256
`8c921fbb…`, 40,851 bytes — the round-2 re-issue). Deliverable: the same
file repaired in place, plus a selftest case using real card heading forms.
Missing prerequisite: none blocking (python3 present; review and gate file
present). Do not touch the pinned review or any other file.

## (3) Success/failure check (behavior, not recall)

Run the gate's own contract plus corvid's probe pattern: (a) `check.py
--selftest` exits 0; (b) an honest receipt (genuine mechanisms only, all
card filenames cited, one disposition) exits 0; (c) the same receipt plus
four fabricated sections is not required — instead, a receipt covering only
genuine mechanisms must not raise `CANDIDATE_SECTION_COUNT`; (d) the
pre-existing 27 named negatives still fail with their expected findings
(no fixed-bug regression). Existing acceptance artifact: the review's fix
list (§Fix 1–3) is the specification. The check was not run by this author;
it must be executed, not asserted.

## (4) Remembered constraint across the session boundary

Keep every line of existing machinery: source-sha bindings, git ordering
checks, whole-grid replay, separate family scores, controls, post-hoc and
prior guards, and all 27 named negatives. Add one selftest fixture whose
external cards carry the REAL heading forms (`External benchmark: …`,
`TEAM RECOMMENDATION — …`, date-coded filenames, technology words) asserting
they never become required sections. This constraint — selftest fixtures
must mirror real frozen input shapes, the failure class shared by S12-1G,
S13-1G and S13-2G — is available to both arms identically; it constrains the
solution shape without revealing it.

## (5) Memory on/off differentiation

Control arm: gate file + task card + ordinary tools (python3, git); no fix
spec, no prior reviews. Memory arm: additionally the pinned review
(`CORVID-S13-2G-VERIFY.md`) and the S12-1G/S13-1G failure records. Neither
arm is denied ordinary tools; no answer keys leak because completion is an
independently executable check (selftest + probes), not string matching
against a known answer.

## (6) Boundary facts

No session/compaction boundary is needed for selection: the task, check,
and constraint above are all on disk now. A later experiment running this
task would need observed session-boundary records (state hashes across
restart); none exist yet, so no boundary claim is made here.

## (7) Contamination

I have read the verifier's fix specification (§Fix 1–3) and the S12/S13
failure pattern, but not the gate implementation file itself. Scope is
therefore a feasibility pilot on a seen-spec task, not an unseen-task
trial: completion must be by independent execution of the check, and any
later run must use unseen tasks for an unbiased estimate.

## (8) Limits and next action

Scope: selection only; no code written, no check executed. Time: this card
(~25 min inspection). Next smallest action: Tern authorizes a bounded
implementation round with the fix list as acceptance, or records no-go.
Efficacy of memory is not claimed; choosing this task implements no memory
system.
