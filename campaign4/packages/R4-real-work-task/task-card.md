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

## (4) Remembered constraint, identical for both arms

Both arms receive the IDENTICAL task card, including the full fix
specification (§Fix 1–3 requirements) and normal repository access (python3,
git, the gate file, prior reviews). A repair task is defined by its
acceptance criteria; withholding them from control would make control do a
different task, so the criteria cannot be the memory treatment. Both arms
see the historical constraint — keep all existing machinery; selftest
fixtures must mirror real frozen input shapes — at task start, as part of
the identical instructions. No arm gets it earlier or later; timing is equal
by construction, recorded in the run log.

## (5) What memory-only persistence/retrieval differs

The sole systematic difference is runtime persistence across the task's own
sessions: the memory arm retains and can retrieve its own prior-session
materials (its earlier attempts, notes, failure records from THIS task);
the control arm starts each session without them. Same task, same spec,
same tools, same model. Plainly stated limit: the executable check cannot
distinguish "derived independently" from "recalled the specification" — a
passing check does not prove independent derivation, and solution leakage
through the shared specification is not prevented by any check here. The
contrast measures only whether own-prior-session retrieval changes the
completion outcome, not the purity of derivation.

## (6) Boundary facts: observable end/start to collect later

No boundary is claimed yet; the following end/start observables are
specified now for later collection: end = the file/byte inventory (with
sha256) the seat wrote in session N (attempts, notes, failure records);
start = session N+1's logged reads of those files (or their absence for
control). Continuity holds iff the start-session inventory matches the
end-session inventory for the memory arm and is empty for control. If either
record is missing, the boundary was not observed for that pair. Compaction
remains unobserved and excluded.

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
