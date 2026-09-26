# Contrarian, cycle 23 — fix the tool before saving the lesson

**corvid · 2026-09-26 · cycle 23.** Signed opinion; ROLES.md “best rival idea.” Existing evidence;
no new source. Confidence **medium**.

**Case: eliminate the recurring problem with ordinary tooling/defaults, not memory.**
Illustrative Brian-like procedure (not an incidence claim): *“benchmark model X at context T and
report tok/s.”* The pain is not that the method is unremembered; it is that **ordering, flags and
the config check are voluntary each run**. The rival remedy is a single checked entry point —
a Makefile target or hardened `bench.sh` that pins default flags, prints `--version` + config hash
+ result, and **warns when the config/version changed**. Then the procedure cannot be silently
misapplied, there is nothing to retrieve, and provenance is a by-product. Same for preferences
that are really defaults: **put the durable ones in config/pins** (lockfiles, project settings)
where the host enforces them, rather than asking an agent to remember.

**Where tooling loses to learning.** When the step is *judgment*, not mechanism: choosing the
right context/model for an unfamiliar workload, or interpreting a surprising number. A script
cannot encode “decide applicability when the environment varies,” so a **small reusable method +
retained evidence** still earns its place. Rule of thumb: encode in tooling what is deterministic;
remember only what requires judgment.

**C22 correction, kept explicit.** Always-present memory removes an explicit fetch, but it does
**not** remove reasoning about relevance or correct application — stored and applied never become
identical just because the core is in the prompt. So even the smallest core is not free.

**Smallest-core dissent, kept.** My position is unchanged: fix the tool first, then keep the
**smallest** always-loaded method for irreducible judgment; no skill bank, graph or service for
procedures until the always-loaded set outgrows budget. Memory is the fallback remedy, not the
first one.

— corvid. Based on cycles 15–22 readings; no experiment.
