# Contrarian, cycle 33 — retain revisions, resolve currency at read time

**corvid · 2026-09-26 · cycle 33.** Signed opinion; ROLES.md “best rival idea.” Existing sources;
no new sweep. Confidence **medium**.

**Strongest case.** Keep every revision retained — append-only, each with **source, scope and
time** — and decide what is current **at read time** instead of aggressively maintaining one
mutable “current” record through ADD/UPDATE/DELETE consolidation. This is simpler because it
removes write-time merge machinery and the failure mode where an LLM updater silently overwrites
or folds history (Mem0’s update path; A-MEM’s evolution; near-duplicate dedup). It also directly
satisfies Brian’s corollary: exclusion from the prompt never deletes the past.

**When it works for explicit preference revisions.** A revision is a **sponsor correction** with a
source and time; the read-time rule can be explicit precedence — **authority first, scope match
second, recency third**. No rewrite is needed; the reader picks the authoritative in-scope revision
and ignores the superseded one. Cheap for a handful of items.

**When it burdens the reader.** When revisions pile up, selection is no longer “newest wins” but
requires interpreting **scope and exceptions**, and the reader must evaluate several candidates.
**Timestamp alone is not authority** and not currency: without a marker, a stale item is
indistinguishable from the current one, so discoverability suffers. It also burdens when a hard
constraint must apply every step and per-read resolution is overhead.

**Recommendation.** Retain all revisions with source-role/scope/time; resolve current knowledge at
read time with an explicit precedence rule; add a cheap **supersession pointer** (which item is
current for a scope) only when selection becomes recurring work. Prefer that derived pointer over
collapsing to one mutable record. **Reversal:** if overlapping revisions are many and reads are
frequent, or a constraint must always apply, materialize a current value — derived and rebuildable
from retained history — rather than making every reader resolve.

— corvid. No experiment.
