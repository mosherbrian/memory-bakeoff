# Contrarian, cycle 4 methods — MemGPT’s captured history, and what it still cannot decide

**corvid · 2026-09-26 · cycle 4 methods.** Signed opinion; primary source read: MemGPT v2
§§2.1–2.4 (arXiv:2310.08560v2). My c4 opinion is preserved; this is a correction, not a rewrite.

**Change of mind — L1 is stronger than I said.** §2.2: the queue manager “writes both the
incoming message and the generated LLM output to recall storage (the MemGPT message database)…
evicted messages … are stored **indefinitely in recall storage** and readable via MemGPT function
calls.” So capture is not “only what the agent chose to write” — every incoming/output message
is persisted, and eviction removes it from the prompt, not from storage. That satisfies Brian’s
corollary at the message level. My c4 table row “L1 not covered” was wrong; L1 is **partially
covered** (message log, not full event/branch/tool provenance). `[read]`

**Does integrated capture + agent paging make lifecycle projection optional?** No — and the
paper shows why the *mechanism* is not absent, just unauditable. MemGPT’s update behavior is
two-part: **append** (recall) plus **self-directed rewrite of working context**, a fixed-size
read/write text block the model edits by function call, explicitly intended to hold “key facts,
**preferences**, and other important information.” So I will not count the absent bitemporal
schema as absence of update behavior: **update exists**. What is missing is everything that makes
an update *decidable*:
- no valid/event time, supersession, or scope — “current” ≈ whatever the model last wrote;
- preferences are prose with no source/authority marker, so an old preference recalled from
  storage is indistinguishable from the current one except by the agent’s own reading;
- retrieval **re-inserts** old messages into context, so the stale item is not merely retained,
  it is re-activated — risk of resurrecting a superseded preference;
- edits are self-directed, so if the model doesn’t rewrite working context, stale truth
  persists (our Gen45: 6 patches, 0 transitions — tools largely unused).
So L2 is the one layer that cannot be made optional *for Brian*, because his two costs
(procedure reuse, preference correction) are exactly current-vs-obsolete decisions.

**What evidence would distinguish it.** Not a recall task. Needed:
1. **Preference reversal probe.** A preference stated in session 1 and revised in session N;
   history keeps both. Measure whether the agent applies the *current, scoped* preference and
   cites the correction — not the older message it can still retrieve. MemGPT’s DMR/opener tests
   recall consistency and engagement; §§3.1 has **no supersession case**, so this is untested.
2. **Changed-environment procedure probe.** A repeated task whose prerequisite changed; measure
   stale-procedure adoption vs re-check. MemGPT has no procedure library — reuse is episode
   retrieval, so it would test whether pagination + agent judgment catch the change.

**Adjacent primary-source question worth reading.** Does any integrated/self-editing memory
expose **provenance or versioning on the self-edited context block** (e.g. MemGPT/Letta memory
blocks with edit history), so that a preference reversal is auditable and the current value is
distinguishable from the recalled old one *without* relying on the agent’s reading? Read the
current Letta memory-block/archival semantics against this paper’s recall-vs-working-context
split.

— corvid. `[read]` MemGPT v2 §§2.1–2.4 fetched 2026-09-26; no reproduction, no experiment.
