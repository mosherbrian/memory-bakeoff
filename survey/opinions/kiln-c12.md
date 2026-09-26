# kiln (Practitioner) — c12: the smallest arrangement, and what would change it

**kiln · 2026-09-26 · ~400w · advice, nothing deployed by me. Sources: cycles 1–11 (all prior kiln pieces), roadmap inputs, BRIAN-PRINCIPLES. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack".**

## The arrangement (four lanes, one repo)

One versioned canonical markdown repo holding scoped preferences (sourced, dated) and textual skills distilled from runs that passed their outcome check. Views, never copies: Claude Code via `@imports` and path-scoped rules; Pi via agent-dir checkout with pi-lcm as on-demand FTS recall (compaction role untouched); local agents via operator-inserted slices. Skills frozen after recording — edits only on steered-wrong failure (the /verify pattern); manual `/name` invocation for side effects; `/doctor`-style trim passes on the always-loaded tier; auto-memory left on as capture net with unreviewed entries untrusted. Single-writer rule: corrections land in canonical first, flow outward.

## Who does what, per host

| | capture | update | delivery | correction |
|---|---|---|---|---|
| Claude Code | auto-memory + hand edits | commit to repo / `/memory` audit | always-loaded tiers + on-demand skills | prune contradictions; validity lines on reversals |
| Pi | operator writes (nothing auto-extracts observed) | same canonical commit | agent-dir files; pi-lcm tool recall | single-writer rule against view drift |
| Local | operator inserts slice | canonical commit | prompt context | re-slice; usage glance as retire signal |

Maintenance totals: one edit location, three mechanical view paths, failure-driven skill edits, periodic trim — no curator, no service, no dashboard. Precedence discipline borrowed from StateMem's wrapper rules: later supersedes earlier, rules outrank instances, recompute derived, retire only on explicit supersession or expiry.

## The symptom that would change my vote

One concrete trigger, not a feeling: **the same corrected preference has to be re-applied by hand on two hosts within one week, or a stale preference causes a real wrong action that a validity line would not have prevented.** That symptom means hand-carried views have failed, and it names the buyer: shared cross-host delivery with invalidation semantics (Zep's graph or MemOS's local plugin — both watch-listed, lifecycle-gated, never benchmark-admitted). Until that symptom appears, a service relocates the work (servers, pins, dashboards, extraction bills) without removing any failure Brian is currently paying for. Unknown integration, honestly marked: Pi's exact load order, local-harness variance, trigger reliability of auto-invoked skills.

**Medium confidence** in the arrangement (assembled from primary docs throughout); **high** that the trigger symptom is the right tripwire — it converts "someday a service" into an observable.
