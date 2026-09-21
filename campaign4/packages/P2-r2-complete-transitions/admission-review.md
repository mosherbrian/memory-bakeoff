# P2-r2-complete-transitions — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract reviewed:** `campaign4/packages/P2-r2-complete-transitions/package.md`,
  sha256 `3d25ab67376866ff09e97c22497cce751aca2060ac945c02b0497da264f14de1`,
  commit `557083bd34300ddb6c924eae43d78e15f24578d0` (working tree re-derived;
  byte-identical to the committed blob)
- **Dispatch record:** `admission-dispatch.md`,
  sha256 `90c8557e8fdc4cd9d6238c48b5b1bc9c025b9349fc4b3b2bbacf7d06bedd5be6`
- **Pass bound:** one 15-minute admission pass; absolute deadline
  2026-09-21T16:34:55+00:00

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract measures the
intended question, its inputs resolve, and its completion check demands the
deeper property the r1 disposition actually requires — not merely
"every state has some exit." Execution release to cairn is warranted under
the dispatch's conditional authorization. This is admission, not execution
verification and not acceptance.

## Why the question is the right one, and measurable

**Task.** Complete the transition specification so an implementation need not
invent exhaustion or blocked-verification behavior (package.md:11–23), and
decide whether the four P2 documents can be frozen for a later implementation
package. This is the correct successor task: r1's table satisfied
"every nonterminal has some exit" yet still could not be implemented without
invention, which is exactly why r1 was withheld.

**Decision informed.** Whether P2's specification documents can now be frozen
for a separately authorized implementation package (package.md:14–16). Named,
bounded, and answerable.

## The completion check targets the actual r1 gaps (verified against r1)

r1 was withheld for two concrete defects
(`P2-specify/acceptance-withheld.md:17–31`), independently confirmed against
the r1 table (`p2-attempt-history/v1/transitions.md` rows 7–16):

- **Gap 1 — no exhaustion route after a failed verification/acceptance.** Row 8
  permits CHECKING → REPAIR_ALLOWED "within budget"; row 9 lists impediments;
  row 14 exhausts **only from BLOCKED**. With the sole repair spent, an
  unsuccessful repair or a withheld acceptance had no explicit destination.
- **Gap 2 — a verification block cannot resume verification.** Row 9 enters
  BLOCKED from CHECKING, but row 11 returns only to REGISTERED or RUNNING, so
  resolving a missing artifact during verification would force a worker rerun.

The contract's completion check closes both, and more:

1. Package.md:50–52 requires an explicit owned, recorded terminal exhaustion
   path for a failed verification **or director acceptance** with no eligible
   allocation left, while keeping a valid negative finding as completion. This
   is the r1 event precisely (r1's post-repair verification PASSed; acceptance
   was withheld with the repair spent).
2. Package.md:53–57 requires BLOCKED to record originating phase, attempt
   identity and remaining allocation; a resolved verification block returns to
   CHECKING with no worker launch or new attempt; an expired verification may
   not silently receive a fresh deadline; other phase resumptions stay defined.
   This closes gap 2 without resetting budget or re-dispatching the worker.
3. Package.md:58–61 requires unambiguous destinations and precedence for
   deadline, invalid measurement, integrity mismatch, eligible repair and
   repair-exhaustion events, and preserves start-before-launch.
4. Package.md:62–67 requires concrete walks of the actual P2 exhaustion, a
   verification resuming within its original allocation, an expired
   verification, successful versus exhausted repair, plus the retained
   successful, valid-negative and amendment cases — with honest
   historical/simulated/projected labelling and a prohibition on invented
   transitions.
5. Package.md:68–70 preserves budget/history continuity, compactness, the
   shared-host trust limits, both decided ownership questions, and explicitly
   forbids rewriting r1's EXHAUSTED as SUPERSEDED or COMPLETE.

Each of the five is a checkable property of a resulting table; none requires
the reader to infer the intended question.

## Inputs resolve

- Commit `03b0ba2` resolves to `03b0ba2f7915e099ecefb219f2465ed7c80aa41c` and
  contains every listed r1 input: the four P2 outputs, `acceptance-withheld.md`,
  `verification.md` (the post-repair PASS), `repair-receipt.md`,
  `campaign4/p2-dispatch-20260921.md`, and `campaign4/p2-attempt-history/`.
- `campaign4/ACCEPTED-ARCHITECTURE.md` at `a4c143be…`, sha256
  `cf390ce0…` — verified present with that digest.
- `director-decisions.md` and P1 `acceptance.md` at `dd157642…` — both present
  in that commit, matching the "remain binding" claim.
- CHARTER carries the standing boundary instruction added at `557083bd`
  (Tern opens warranted successors herself), so the successor's authorization
  is grounded rather than inferred.
- Package.md:37–39 requires cairn to pin full commit and hash at registration
  and rejects a moving-HEAD input; the short `03b0ba2` is explicitly to be
  resolved to its full id at registration, which the commit-history check
  confirms is unambiguous.

## Roles, independence, allocation, permissions

- **Roles:** author/director Tern; reader/verifier corvid; worker kiln;
  controller/duty owner cairn (package.md:8–9, 105–111). Worker ≠ verifier;
  contract author ≠ validity reviewer; the reader did not materially repair
  this contract. Candidate disputes get one bounded disposition.
- **Allocation:** admission one 15-min pass plus one 10-min repair-confirmation;
  worker 30 min + one 15-min repair; verifier 20 min per pass including repair
  (package.md:76–91). Cumulative ceilings — 135 worker minutes and 100
  verifier minutes across r1+r2 — are arithmetically correct (r1 worker
  60+30 = 90, verifier 30+30 = 60; r2 worker 30+15 = 45, verifier 2×20 = 40)
  and preserve r1's spent repair rather than recycling it. Explicit new
  allocation, not an automatic retry.
- **Overdue/exhaustion:** cairn stops overdue work, records BLOCKED, wakes Tern;
  timeout does not auto-allocate a repair; after the allocated repair is spent,
  nothing further is automatic and Tern decides the terminal disposition
  (package.md:93–103). Consistent with the accepted architecture and the duty
  owner's existing authority.
- **Permissions:** read-only repository inputs and version/hash commands; the
  five named outputs only; cairn and corvid write only their registration,
  dispatch and review evidence here; r1 bytes preserved; no upgrade, migration,
  research execution, controller code or further package (package.md:105–111).
  Bounded and consistent with the charter.

## Non-blocking observations

- `campaign4/p2-dispatch-20260921.md` in the working tree carries one appended
  event after commit `03b0ba2`; the contract pins the commit's bytes, which is
  the correct immutable input, so no action is required.
- This admission does not certify the resulting table. Items 1–5 are execution
  verification, performed after the worker publishes, against the then-bound
  hashes. A PASS at that stage still requires Tern's explicit acceptance to
  freeze.

## Effect

Bound to contract bytes `3d25ab67376866ff09e97c22497cce751aca2060ac945c02b0497da264f14de1`
at commit `557083bd34300ddb6c924eae43d78e15f24578d0`. Cairn may release this
exact unchanged contract to kiln under the dispatch's conditional
authorization, after recording admission, input pins, and start/deadline, and
after confirming actual wake delivery. Changed bytes would require independent
confirmation before release.
