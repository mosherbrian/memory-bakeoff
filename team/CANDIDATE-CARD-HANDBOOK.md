# Candidate card — HANDBOOK.md (long-context agentic instruction following)

**Author:** muse-drafter (proposal-drafter seat), watchlist delta #2 follow-up (Sprint-2 goal 5)
**Date:** 2026-09-15 · **Cost:** $0 (abstract/body web reads only)
**Status:** **candidate discovery only — no score import.** Best candidate of
`SPARK-WATCHLIST-DELTA-2-20260915.md` (the only both-lane reuse-green entry).
Owner unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *HANDBOOK.md: A Benchmark for Long-Context Agentic Instruction Following* |
| Authors | Liudas Panavas, Sebastian Minus, Bradley Monton, Derek Ray, Suhaas Garre, Sushant Mehta, Edwin Chen (Surge AI) |
| ID / date | [arXiv:2607.25398](https://arxiv.org/abs/2607.25398) v1 2026-07-28, **v3 2026-08-03**, cs.AI/cs.CL; **COLM 2026 WAB** |
| Paper license | **CC BY 4.0** |
| Artifact | tasks + environments + evaluation harness at `github.com/surge-ai/handbook` — **Apache-2.0**, 54★, actively pushed |
| Numbers | vendor-reported only: strict-grading best model **36.2%**, most frontier **<25%** — **NOT verified, do not cite** |

## What it is

65 agentic tasks, each in a self-contained company environment (file workspace +
mock email/chat/calendar/issue-tracking/commerce over **MCP**), governed by an
expert-written SOP of **20–124 pages**. Five domains, 10 fictional companies;
every task mutates one of 10 base handbooks so **no two tasks share policies**
(memorization resistance). Grading is **fully deterministic**: 824 programmatic
criteria that check **both that required actions occurred and that prohibited
actions did not**.

Documented failure patterns (vendor): a plausible but **unauthorized
in-environment request overrides the standing policy**; an agent **performs a
required check then acts against its result**; **rule details are lost over long
horizons**; and agents **report compliance they did not achieve**.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **good (design)** | standing policy vs in-environment request — a precedence conflict, measured |
| **stale-instruction / premise awareness** | **good** | "required check performed then ignored"; "details lost over horizon" |
| **G3 invocation** | partial | standing policy constrains each action; no proactive deadline |
| **G4 material outcome** | partial | task completion under policy, not coding time/errors |
| **reporting discipline** | **good** | required **and** prohibited criteria — mirrors our harmful/prohibited-presence rule |
| G2 supersession / G5 continuity | weak | no old→new retirement, not longitudinal work |

## What it offers us

- **A deterministic required+prohibited rubric** at step granularity — the same
  reporting shape we enforce, applied to policy-following.
- **Two named failure classes** we can adapt directly to our stale-path probe
  design: *authorized-vs-unauthorized precedence* and *check-performed-then-
  ignored* (a premise-awareness analogue).
- **MCP-based environments** with released harness — reusable as a *design*
  reference for our own environments, and Apache-2.0.

## What it cannot ground

Memory retrieval, supersession, or coding outcomes. It is instruction-following
in mock business workflows; its numbers are vendor and stay uncited. It is
**not** a memory benchmark.

## Next step (bounded)

1. Body pass: extract the rubric/prohibited-criterion schema and the MCP
   environment shape — check whether the "required check then ignored" class maps
   onto our premise-awareness / stale-path probes (design, not a run).
2. If it transfers, add the two failure classes to the stale-path probe design;
   otherwise record as a **policy-following design reference**.

## Verification status

Existence, title, authors, ID/date, venue, paper license, and the **Apache-2.0**
harness repo confirmed. Numbers are **unverified vendor claims**. No score
import. Second seat **done**: `CORVID-HANDBOOK-PINCHECK.md` (clean pass, pin +
abstract + artifact independently confirmed).

## Seat pre-review (primary spot-check, 2026-09-15)

Independent abs-page + API read of the card's load-bearing claims:

- **"65 agentic tasks"** ✓, **"824 [criteria] in total"** ✓, **"20–124 pages"**
  SOPs ✓, **"strongest evaluated model passes 36.2%"** under strict all-criteria
  grading ✓, **COLM** venue ✓ (abstract).
- **Harness `surge-ai/handbook` license = Apache-2.0** ✓ (GitHub API `spdx_id`).

All checked claims agree; **not** a substitute for Alice's second seat, and the
vendor rates remain uncited.

— **muse-drafter** (Spark). Candidate discovery, $0; no score import.
