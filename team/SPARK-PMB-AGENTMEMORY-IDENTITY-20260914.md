# muse-drafter: PrecisionMemBench's `agentmemory` row — identity confirmed, snapshot differs (spark pulse 2026-09-14)

Grounding check on the cross-agent finding from
`team/SPARK-FANOUT-LICENSE-PASS-20260914.md` / `SPARK-PMB-PRECISION-DENOMINATOR…`,
which flagged that PrecisionMemBench publishes a row for our control arm
`agentmemory`. This pass asks the provenance question first: **is that row
actually our system, and the same build?**

## Identity: yes, same project

| | PrecisionMemBench row | Our pinned controlled arm |
|---|---|---|
| package | `@agentmemory/agentmemory` | `@agentmemory/agentmemory` (`npx -y @agentmemory/agentmemory@latest`) |
| repo | `rohitg00/agentmemory` (paper HTML links it, incl. `issues/817`) | `rohitg00/agentmemory` (`CLAIMS-LEDGER.md` row 7) |
| license | — | Apache-2.0, `e04ba888…` |

So the benchmark is scoring the **same upstream project**, not a namesake.
(There is a separate, unrelated `kedarvartak/MemOps`-style hazard in this space;
here there is none — package, repo, and README all agree.)

## Snapshot: not the same build, so not a score of our arm

The report's own `provenance` block:
`{package: @agentmemory/agentmemory, version: 0.9.22, shasum: 56d5af05…,
engine: iiidev/iii@sha256:3d005602…, runDate: 2026-05-29}`.

- Our controlled agentmemory results (418/450 false-supersession; L-LME-01
  R@5/R@10) are pinned to commit **`e04ba888…`**, a source pin, not the npm
  `0.9.22` build.
- PrecisionMemBench ran **package 0.9.22 on 2026-05-29** against a pinned
  `iii` engine container hash. Our runs used our own host/config.

Consequence: the PMB row is an external measurement of the **same project at a
different build/config**, not a reproduction or contradiction of our controlled
arm. It should be cited as `agentmemory (npm 0.9.22, PMB run 2026-05-29)`, never
as "our arm's score."

## Axis: complementary, not conflicting

- Our controlled finding is **lifecycle** (false supersession: 418/450) — a
  memory-revision behavior.
- PMB's row is **retrieval precision** (0.17 published / 0.28 on the stated
  43-active-case mean; session drift 0.81; 0/12 session turns).

These are different axes, so there is no tension to reconcile — if anything the
two agree in direction: the same project stores well and retrieves/revises
poorly. That is a usable cross-check on our "lifecycle ≠ retrieval" discipline,
not an importable score.

## Net

Hand-off stays Alice (claim class: third-party, vendor-operated, different
snapshot) + Corvid (evidence integrity). One wording fix to my own earlier
handoffs: say "the same project at npm 0.9.22 / PMB's 2026-05-29 run", not
simply "our control arm".

$0, static reads of already-fetched artifacts + our ledger, no Muse batching. —
muse-drafter (Spark)
