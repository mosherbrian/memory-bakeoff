# P2-specify — independent verification

- **Verifier:** corvid (named reader; did not author these outputs)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Pass:** 30-minute independent pass (deadline 2026-09-21T15:42:43Z)

## Artifacts verified

| Artifact | sha256 (recomputed on disk) |
|---|---|
| `packages/P2-specify/contract.md` | `fd573ad3d068f90afb3182fc145736c828eb34dde0798a5ebc1970076d13845e` |
| `packages/P2-specify/transitions.md` | `77b795749631b65d7b1907bb25c65c8f03dd5faad0d43c6a355ed65f93b40252` |
| `packages/P2-specify/ownership.md` | `c8126700897cfcb78cb25c7e481c5ecb32518858a5540e2d804874fdf84e4150` |
| `packages/P2-specify/walkthrough.md` | `8cee592012f562a2607942bd52f42744833fd06850cbf87ca09fe71870be2d07` |

All four hashes match the values supplied at dispatch (recomputed, not trusted).

## Verification inputs

- Contract: `packages/P2-specify/package.md`,
  sha256 `30f98fd59e9d4026edfff4a01f81ad1e56c7414d6effb90a51faf32933fed9ec`
  (recomputed; matches).
- Director decisions: `packages/P2-specify/director-decisions.md`,
  sha256 `75540744f853ebd5e0f02cdc100ad79716d8aefc352c5aef1f82f014b8cd654e`
  (recomputed; matches).
- Accepted P1 input: `packages/P1-inspect/capability-map.md`,
  sha256 `b7279897618c41339e4eca3b6744527b991c7c38d712b62bb5eeb8b1c111eea9`
  (recomputed; matches), plus P1 `acceptance.md` (`b402a771…`) for the
  shared-host limitations director-decisions requires.
- Pinned source: `campaign4/ACCEPTED-ARCHITECTURE.md` (§2–§5).
- Authoritative execution record: `campaign4/p2-dispatch-20260921.md`.

## Verdict

**FAIL** — one bounded, correctable defect. Every completion-check condition is
met and the specification substance is sound; the failure is a single factual
value in `walkthrough.md` that contradicts the authoritative dispatch record.
The defect is in scope because `director-decisions.md` requires the walkthrough
to preserve P1's and P2's **actual admission and execution history**, and the
frozen output would otherwise carry a wrong execution bound.

## The defect (bounded)

`walkthrough.md:60` states P2's execution bound as:

> this specification is at RUNNING (start 15:08:16Z, **deadline 16:09:31Z**)

The authoritative dispatch record contradicts this. `p2-dispatch-20260921.md`
records that the original `OnActiveSec=1h` timer scheduled 16:09:31Z — "75
seconds beyond the allocation" — was **replaced**:

> Replaced with `campaign4-p2-initial-deadline.timer`, absolute
> **2026-09-21T16:08:16Z** … Start and budget unchanged.

The governing initial deadline is therefore **16:08:16Z** (start 15:08:16Z +
60m, per the dispatch header). `walkthrough.md:60` cites the superseded timer
value, 16:09:31Z. This is the corrected-deadline error the dispatch record
explicitly warns about ("deadlines must be computed from the recorded start,
not timer creation time"). The same file's P1 example is internally consistent
(start 14:51Z, deadline 15:36:10Z, both `= start + 45m`), so the P2 value is an
isolated error.

**Required correction:** replace `16:09:31Z` at `walkthrough.md:60` with
`16:08:16Z` (or cite `p2-dispatch-20260921.md`), preserving all other bytes and
the ACTUAL/SIMULATED/PROJECTED labelling. This is a one-value repair; the
repair budget (1 × 30 min) applies, with a 30-minute post-repair verification.

## Completion check — all four conditions CONFIRMED

1. **Every nonterminal state has an exit.** DRAFT → rows 1–2; ADMITTED → 3;
   REGISTERED → 4; RUNNING → 5–6; CHECKING → 7–9; REPAIR_ALLOWED → 10;
   BLOCKED → 11–14. All nonterminal states have at least one exit
   (`transitions.md:10–27`).
2. **Terminal states have no outgoing execution transition.** Row 16 marks
   `COMPLETE / EXHAUSTED / TERMINATED / SUPERSEDED` terminal with destination
   "None"; the amendment path (row 15) originates from a live revision, not a
   terminal. Confirmed.
3. **The amendment path exists and does not reset budgets.** Row 15 routes
   old revision → SUPERSEDED, new revision → DRAFT, "budget continues under
   stable `question_id`", with the note "Resumption never resets"
   (`transitions.md:26,34–35`). Confirmed.
4. **Every role's "may not" is stated.** `ownership.md:10–18`, column "May
   not", for Director, Contract reader, Worker, Independent verifier, Duty
   owner/overseer, Controller, Sponsor. Confirmed.
5. **The walkthrough reaches a terminal state for all four examples without a
   step not in the table.** Examples 1–3 terminate in COMPLETE/negative/
   EXHAUSTED using only rows [1],[3],[4],[5],[7],[6],[9],[11],[14]; example 4's
   amended branch reaches terminal (old revision → SUPERSEDED) with P2's
   terminal step explicitly labelled PROJECTED, which `director-decisions.md`
   (46–56) expressly permits. Confirmed. The deadline defect does not add a
   step to the table; it misstates a value inside a projected step.

## Director decisions — incorporated

- **Overseer recovery budget:** one ≤15-min recovery + one ≤15-min repair of
  that recovery, corvid ≤10-min verification passes when relied-on artifacts
  change; ceilings not grants; first-expiring limit governs; failed recovery
  stays BLOCKED → Tern; no ladder; cairn cannot certify its own repairs
  (`contract.md:35–56`, `transitions.md:56–63`, `ownership.md:20–29`). Matches
  `director-decisions.md:7–24`.
- **Supervisor liveness:** Tern owns supervisor liveness and the host-side
  silence backstop; cairn owns per-attempt one-shot deadlines and
  reconciliation; cairn wake-driven, never polls; `campaign4-watch` is an
  interim backstop distinct from specified enforcement; failure coverage for
  lost timers, host restart, stale activity, failed wake delivery; reconcile
  before dispatch (`transitions.md:41–67`, `ownership.md:12,16,27–29`). Matches
  `director-decisions.md:26–44`.
- **Codex exhaustion:** stops the director role, waits for Brian, no substitute
  model; Tern's unresolved decision uses the pause path rather than an
  automatic retry (`transitions.md:64–67`, `ownership.md:12`). Matches
  `director-decisions.md:40–44`.
- **Shared-host identity limitations:** `contract.md:52–56` states the
  controller reads configured session metadata, not cryptographic proof of
  authorship/execution; worker hashes, identity-file paths and pane collection
  do not prevent another same-filesystem process from supplying those bytes;
  cross-boundary claims are payload, never attribution. This matches P1
  `acceptance.md:29–36` and `capability-map.md` §5. Confirmed.
- **P1 baseline interpretation:** `contract.md:6–7` fixes installed v1.16.4 and
  P1 v1 accepted; `contract.md:60–61` withholds upgrade/migration authority;
  experiment registration, attempt binding and the `question_id` budget rule
  follow the settled `LOOP-REQUIREMENTS-20260920.md`, not a redesign.

## Fidelity to the accepted architecture (no redesign)

- `contract.md` freezes §3 (six fields, four work-type extensions, admission as
  accepted-or-one-bounded-rejection) and stays compact at 64 lines.
- `transitions.md` freezes §4 (all states, exits, destinations, amendments,
  workflow-vs-outcome separation).
- `ownership.md` freezes §2 (role table, independence rules, closed ownership
  questions) and CHARTER's seats/lanes.
No state, role or rule was added, removed or reinterpreted against the pinned
source beyond the decisions `director-decisions.md` authorizes.

## Other checks

- `walkthrough.md` uses P1 and P2 themselves as examples, consistent with
  package.md:56 and director-decisions.md:52.
- P1 example figures cross-check against `p1-dispatch-20260921.md`
  (contract `04afe817…` at `33d9a25a`, output `b7279897…`, verdict
  `98201be9…`, start 14:51Z / deadline 15:36:10Z, PASS within bound).
- No controller code, upgrade, migration or subsequent-package claim appears in
  any of the four outputs.

## Re-verification after repair

A post-repair pass will recompute all four hashes and re-check `walkthrough.md`
line 60 against `p2-dispatch-20260921.md`; the other three artifacts are
confirmed and should be unchanged.
