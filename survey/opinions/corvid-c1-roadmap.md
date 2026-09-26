# Contrarian addendum — the five-layer hypothesis and the Pi pilot

**corvid (Contrarian), 2026-09-26.** Signed opinion, not an audit. Confidence = transfer
to Brian’s decisions. Quote ROLES.md: *“argue the strongest case AGAINST the current
position memo, and for the best rival idea.”*

**Strongest case against:** the five-layer roadmap is a **decomposition of
responsibilities, not an architecture**, and the Gen45 pilot is being read backwards.
Arm B lost 7/12 to 12/12 — but per the pilot’s own mechanism section, the state layer was
*model-volunteered* (6 accepted patches, **0 transitions across 12 runs**) and retrieval
was absent, so layers 1–3 were never in the comparison. What lost was “two interaction
units + hand-maintained state + three ignored tools.” The pilot **does not falsify the
composite**; it falsifies a bounded hand-maintained window. The keeper is H1/H2: bounding
per-request context did **not** bound total work (T3: 337 requests, 591 tool calls, 3
timeouts, 1.1 MB/request vs arm A’s 209× growth and 12/12). **High confidence** the pilot
is not evidence for or against the five layers; **medium** that it is evidence against
model-maintained state and against treating “bounded context” as the win.

**Best rival idea — the two-layer baseline.** Arm A *is* the rival: verbatim transcript
replay + Pi’s own surface, no state projection, no WM synthesis, one implicit composer. It
won 12/12. The strongest rival to five layers is **lossless history + retrieval-on-demand**,
with **harness-written state only if a measured failure demands it**. Every added layer is
a new failure surface (state drift, patch churn, composer duplication) purchased before a
demonstrated benefit. An integrated long-context product may satisfy the same
responsibilities with two moving parts. **Medium confidence.**

**Where I think Tern is wrong:** the revised claim that “responsibilities hold while product
choices remain open” is half right. The *responsibilities* are real measurement properties
and the seven failure classes are sound. But the reconciliation slides from responsibilities
to **five separable services**, and that slide is untested — Gen45 is the only composition
evidence and it ran a mutant. Product choice and architecture shape are **coupled**: a
single integrated product that keeps an append-only log plus good retrieval would satisfy
the responsibilities *without* an explicit state-projection or WM layer, i.e. it falsifies
the layered hypothesis structurally, not merely by substitution. So product choices are not
independent of the layer question. **Medium confidence.**

**What the negative pilot does and does not change (scope preserved):** 4 invented tasks, 3
stochastic samples each, one local 35B at temp 0.6, no seed, one host; *not* a coding
benchmark, *not* a full five-layer test, Pi compaction never fired. It changes: how we read
composed-context wins, and how much we trust model-written state. It does not change: the
case for durable history or retrieval.

**Evidence that would settle it:** re-run the paired-live harness with (a) harness-written
state, not volunteered; (b) tasks long enough to trigger compaction; (c) a **two-layer
rival** (verbatim replay + on-demand retrieval) as its own arm beside the full composite
and the Phase-G ablations. If two layers match or beat five on verifier pass and cumulative
work, the five-layer hypothesis is displaced. That single arm is cheaper than the matrix.
