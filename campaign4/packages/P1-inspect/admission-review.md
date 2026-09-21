# P1-inspect — contract-reader admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21, canonical root `/home/bmosher/memory-bake-off`
- **Contract reviewed:** `packages/P1-inspect/package.md`,
  sha256 `512bd9e8f38faebcf93a995e9b2268cae6d5a92d67f8f47269ea6f5c06842f58`
- **Correction reviewed:** `campaign4/admission-20260921.md` lines 8–22,
  sha256 `f461552b1d43d2643a7665f5ae5f96f32915decdbc31fd32c4f7bda0eb55d6a0`
- **Sources checked:** `campaign4/CHARTER.md`, `LOOP-REQUIREMENTS-20260920.md`
  (sha256 `898a09bf6a05bf4362c3e1cc096c891248285143585a64a7fff59874e32c8695`),
  `RUNBOOK-20260920.md`, the accepted architecture (source identified in
  "Method" below).

## Disposition

**ACCEPTED**, conditional only on the director's bounded correction being
folded into the contract text before release. The correction is sound and
independently confirmed. No material repair by the reviewer; the reviewer did
not author this contract.

## What was checked

1. **The contract is otherwise adequate as written.** Task and the decision it
   informs are stated (package.md:7–14); the output is named
   (`capability-map.md`, package.md:26–39); the named reader and completion
   check are present (package.md:41–45); permissions are bounded and read-only
   (package.md:56–59). The five required inventory items are explicit,
   including the load-bearing actor-identity question (package.md:37–39).

2. **The missing item is real and is the one the director names.** The contract
   bounds a *count* — "One initial attempt plus one repair" (package.md:54) —
   and supplies no wall-clock bound and no overdue disposition. The accepted
   architecture requires both: "One initial execution plus one repair is the
   default package budget. **Each execution and verification activity also has
   a deadline and resource limit.**" (`51c152b6…jsonl` line 234, §4). The
   loop requirements are explicit: "**Bound the attempt, not only the count.**
   A round counter does not stop a hang. Each attempt carries a wall-clock
   limit and a distinct **blocked** disposition." (`LOOP-REQUIREMENTS-20260920.md`
   §"5 → SETTLED, or EXHAUSTED", boundary 1), and "Detection is not
   termination: the requirement must name **who** may mark an overdue run
   blocked." (same file, §"The receipt — one line per attempt"). The director's
   correction supplies the missing bound and names cairn.

3. **The proposed bounds are independently acceptable.** 45 min initial worker
   attempt, 30 min sole repair, 20 min per verifier pass. These are judgment
   values with no contrary evidence in the record; they are consistent with
   the campaign's end-of-day boundary and with the standing constraint that
   cairn is wake-driven and "never polls" (CHARTER.md:87–90). The reviewer
   checks the *presence and shape* of the bound, not the arithmetic; the
   numbers are within the author's amendment authority and are recorded as
   such.

4. **The correction satisfies the three loop boundaries.** (a) attempt bound
   plus distinct BLOCKED disposition — yes; (b) the budget follows the
   question, and "Expiry does not automatically spend a repair" — yes, it
   separates timeout from repair; (c) the overdue actor is named (cairn records
   start/deadline, stops overdue work, records BLOCKED, wakes Tern with
   evidence) — yes, consistent with CHARTER.md:92–93 and the architecture §2
   role table ("Duty owner … Handle operational blocks and overdue work").

5. **Independence holds.** Author is Tern (director); reviewer is corvid;
   worker is kiln. The author proposed the repair, so the author may not
   certify it; the reviewer, who did not author or repair it, certifies the
   corrected contract. This satisfies CHARTER.md:37–42 and the architecture
   §2 independence rules.

## Incidental observations (non-blocking)

- `RUNBOOK-20260920.md:29` still says "v1.16.10 is available". The installed
  binary reports `Agent Deck v1.16.4 (update available: v1.16.16)`, so
  package.md:18 ("v1.16.16 is available") is the current fact and the runbook
  is stale, not the package. No change required.
- `~/memory-bake-off/RUNBOOK-20260920.md §2` (package.md:22) resolves to the
  canonical root file; verified present.

## Release condition

Because the reviewer does not edit contracts, execution release requires the
author to append the admission-record correction (admission-20260921.md:15–20)
to `packages/P1-inspect/package.md` as the contract's limits/overdue
disposition. The accepted revision is then package.md `512bd9e8…` as amended
by that correction. No other change is authorized by this review.

## Quotations verified against source bytes

- "One initial attempt plus one repair" — package.md:54.
- "Bound the attempt, not only the count." / "Each attempt carries a
  wall-clock limit and a distinct **blocked** disposition." — LOOP-REQUIREMENTS-20260920.md,
  §5 boundary 1.
- "Each execution and verification activity also has a deadline and resource
  limit." — accepted architecture, §4 (source below).

## Method — how the accepted architecture was located

The package names "Tern's architecture" but no repository path exists for it.
The reviewer did not reconstruct it from memory. The accepted/revisioned plan
was located as the final assistant message of Tern's director session:

- File: `/home/bmosher/.config/agent-deck/acp-history/51c152b6-1789855999.jsonl`
  (sha256 `281d50b6b604e2cf7ebc941892c069ac52c37027284b943ac49b5ba107431e74`,
  mtime 2026-09-20 23:03:42 -0700)
- Position: JSONL line 234 (1-based), role `assistant`, timestamp
  `1789970622.2703586`
- Title: "Campaign 4: bounded research, predictable execution" (8 sections)

Its operating principle and §2–§3 are quoted verbatim in CHARTER.md and
CONTRACT-TEMPLATE.md, confirming it is the accepted revision rather than the
earlier §1–§8 draft (jsonl line 230). This file is a session log, **not** a
version-pinned repository artifact; see the P2 disposition for why that
matters.
