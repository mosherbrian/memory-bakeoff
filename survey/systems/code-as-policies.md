# System card: Code as Policies (reactive generated code)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2209.07753v4 (§§I–V incl. limitations) + project site (per-domain prompt roles, generated-code demos). Author repo: unlocated after two bounded attempts — worked from paper + site, recorded. Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## Observation→branch/control path (the correction to c43)

`while not detect_object("apple"): robot.set_velocity(...)`; `get_pos` re-queried each loop iteration; `parse_obj` recomposed per turn. Generated code consumes fresh perception outputs, branches, loops until the world matches — code observes by construction. My c43 compute/perceive boundary is withdrawn as a claim about code: it described LATM's static-function scope only. For Brian: generated helpers may read state (grep, tests, git) and branch on it; the honest boundary is *which read APIs are supplied and trusted*, not prose-vs-code.

## What persists, what the host provides, who builds what

- **Persists/reused:** hierarchically generated functions accumulate into exec scope (AST backfill of undefined functions); LMP session appends enable "undo that"; per-demo generated code on the site. No cross-task library described — reuse lives within scope/session, not an accumulating memory system (contrast Voyager).
- **Host provides:** perception APIs (ViLD/MDETR detectors), control primitives (velocity, pick/place, say), exec sandbox with safety screen (no imports/dunder/exec/eval), embodiment APIs.
- **Model-generated:** policy code, sub-functions, waypoint math (NumPy/Shapely). **Hand-built:** APIs, per-domain prompt roles (High-Level UI, Parse Names/Positions, Function Generation), examples, safety screen.

## Limits (paper's own §V)

Bounded by perception APIs and tunable params; long/complex or abstraction-mismatched commands fail; feasibility assumed; correctness unknowable a priori. Eval: simulated tabletop numbers + real-robot demos (HumanEval-code metric kept separate from physical outcomes).

## Advice: **borrow reactive shape, watch the stack**

Perceive-branch-act generated helpers with supplied read APIs port to Brian's lane directly (check-then-act scripts, re-query loops). Nothing persists across tasks without additional machinery, and the robot stack stays behind. **Medium-low confidence** (paper + site read; repo unlocated; transfer scoped to software reads).
