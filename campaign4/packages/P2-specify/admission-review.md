# P2-specify — contract-reader admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract reviewed:** `packages/P2-specify/package.md`,
  sha256 `8206d5dd582cb9ae40502589dc07b5c7cff9fd96c8915202122cacf54b957e19`
- **Correction reviewed:** `campaign4/admission-20260921.md` lines 24–41,
  sha256 `f461552b1d43d2643a7665f5ae5f96f32915decdbc31fd32c4f7bda0eb55d6a0`
- **Sources checked:** accepted architecture (locator below),
  `CONTRACT-TEMPLATE.md`, `CHARTER.md`, `LOOP-REQUIREMENTS-20260920.md`,
  `DECISIONS-20260920.md`, the three historical reviews in `team/.director-*.md`.

## Disposition

**BOUNDED REJECTION.** The proposed direction is correct, but the contract is
not admissible as written. Three of the four items below are already named in
the director's correction; the first is the one only the reader could settle,
and it is not yet settled in a form the worker can use without reconstructing
the source. The reader is returning one bounded list of what is missing, not a
negotiation.

## What is missing — exactly

### 1. No resolvable, version-pinned source for the accepted architecture §2–5

package.md:21 names "Tern's architecture, sections 2–5, as the source" and
supplies no path. The reader located the accepted revision — it is not
invented:

- `/home/bmosher/.config/agent-deck/acp-history/51c152b6-1789855999.jsonl`
  (sha256 `281d50b6b604e2cf7ebc941892c069ac52c37027284b943ac49b5ba107431e74`,
  mtime 2026-09-20 23:03:42 -0700), JSONL line 234 (1-based), role `assistant`,
  timestamp `1789970622.2703586`, titled "Campaign 4: bounded research,
  predictable execution". Its §2 = "Assign roles and authority", §3 = "Use one
  compact work-package contract", §4 = "Execute a complete, bounded
  lifecycle", §5 = "Give each fact one authoritative home".

But this is a **session log outside the repository, not a version-controlled
artifact**. It cannot be a "resolvable, version-pinned copy" in the sense the
contract needs: a worker must freeze the specification, not a live transcript,
and must not be the one who decides which of two architecture drafts is
accepted. The package says "It is the specification; this package freezes it,
it does not redesign it" (package.md:21–23). That is only executable if the
specification is pinned by the author. Required: Tern commits a copy (or a
canonical extracted document) to the repository and cites
`path + sha256 + commit` in package.md Inputs. Until then the source is
**unresolved as a repository artifact**.

Confirming the draft/revision risk concretely: an earlier "§1–§8" draft exists
in the same session at JSONL line 230 and enumerates its own sections 1–8
beginning "Build a bounded work executor, not an autonomous research planner".
The three `team/.director-*.md` reviews do **not** identify which is accepted.
A reader that had not located line 234 could easily freeze the wrong document.
This is precisely why the path must be pinned rather than inferred.

### 2. The two relative root-document references resolve incorrectly

package.md:25–26 cite `../../LOOP-REQUIREMENTS-20260920.md` and
`../../team/.director-*.md`. Relative to the package directory
`campaign4/packages/P2-specify/`, `../../` resolves to `campaign4/`, so these
point at `campaign4/LOOP-REQUIREMENTS-20260920.md` and
`campaign4/team/.director-*.md` — neither exists. The intended repository-root
targets are `/home/bmosher/memory-bake-off/LOOP-REQUIREMENTS-20260920.md`
(present) and `/home/bmosher/memory-bake-off/team/.director-*.md` (present:
`.director-decisions-review.md`, `.director-index-review.md`,
`.director-loop-review.md`, `.director-loop-review-rev2.md`). Required: anchor
both to the repository root (three `../`, or root-absolute names).

### 3. The completion check contradicts the required terminal states

package.md:50 says corvid confirms "the transition table has no state without
an exit". The accepted architecture §4 defines seven nonterminal states plus
"**COMPLETE / EXHAUSTED / TERMINATED / SUPERSEDED** — Terminal for that
revision". A rule that every state must have an exit contradicts the required
terminal states. The director's correction is independently confirmed. Required
wording: exits are required from every **nonterminal** state, and terminal
states have **no outgoing execution transition** (SUPERSEDED is entered only by
the amendment path, §4, and is terminal for that revision).

### 4. No worker/verifier wall-clock bounds or overdue disposition

Same defect as P1: package.md:61–62 bounds a count ("One initial attempt plus
one repair") and no duration; the accepted architecture §4 requires "Each
execution and verification activity also has a deadline and resource limit",
and LOOP-REQUIREMENTS §5 boundary 1 requires a wall-clock limit plus a distinct
BLOCKED disposition with a named actor. Required: 60 min initial worker
attempt, 30 min sole repair, 30 min per verifier pass; the same cairn-owned
BLOCKED/deadline handling as P1, event-driven and not authorizing polling;
expiry does not spend a repair; the campaign end-of-day boundary still applies.

## Independent assessment of the proposed corrections

- **Deadline numbers (60/30/30).** Acceptable. They are judgment values with no
  contrary evidence; the reviewer checks that a bound exists and is paired with
  a named overdue disposition, not the arithmetic. Consistent with the accepted
  architecture §4 and with CHARTER.md:87–90 (cairn wake-driven, never polls).
  One clarification required: "per verifier pass" must cover any
  post-repair verification pass, not only the first.
- **"P1 must be independently accepted before P2 execution starts."**
  Consistent; P1 is accepted as corrected (see P1 disposition).
- **Ownership questions.** "The two ownership questions remain deliverables for
  Tern to decide within the accepted architecture, not permission for kiln to
  redesign it" — correct and consistent with architecture §6 ("The
  supervisor's own liveness and recovery ownership must be assigned") and §2.
  The reviewer notes the architecture names the duty owner as "proposed:
  overseer"; P2 must close that proposal, not restate it.
- **Compactness constraint.** package.md:61–62 ("If the contract cannot be kept
  compact, that is a finding") matches architecture §3's line "There is no
  bespoke schema or gate-authoring exercise for each package." Good.
- **CONTRACT-TEMPLATE is the right transcription.** It matches accepted §3, not
  the draft §3 (which was a 25-field data model). No issue.

## What is not in question

Task and decision are stated (package.md:9–16); outputs are named
(`contract.md`, `transitions.md`, `ownership.md`, `walkthrough.md`,
package.md:29–46); the work type (judgment) and named reader are present;
permitted reads/writes are bounded (package.md:64–67). The four work-type
extensions match accepted §3. The walkthrough's four cases match architecture
§7's "Walk successful, negative, blocked and amended examples".

## Quotations verified against source bytes

- "the transition table has no state without an exit" — package.md:50.
- "Terminal for that revision" — accepted architecture §4 (locator §1 above).
- "Each execution and verification activity also has a deadline and resource
  limit." — accepted architecture §4.
- "Bound the attempt, not only the count." — LOOP-REQUIREMENTS-20260920.md §5
  boundary 1.
- "There is no bespoke schema or gate-authoring exercise for each package." —
  accepted architecture §3.
- "Detection alone is not enforcement." — accepted architecture §6.
