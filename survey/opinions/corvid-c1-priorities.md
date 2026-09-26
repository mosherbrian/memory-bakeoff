# Contrarian priorities — procedures, compact

**corvid, 2026-09-26.** Signed opinion; confidence = transfer to Brian. ROLES.md: strongest
case against the memo.

**Rival (medium confidence):** retrieval from **raw episodes + executive reasoning** beats an
explicit skill/runbook library as the *default* for avoiding procedural re-learning. A runbook
freezes a past success into a present instruction: it silently carries the artifact state of
when it was written, so configuration_collapse and stale_persistence become advisory prose a
careless agent follows anyway. Episode retrieval keeps the trace and lets the executive decide
*applicability* — which is exactly Brian’s split: history reconstructs, artifacts establish
truth, executive reasoning decides meaning. Runbooks win only where a procedure is **stable,
verified, high-frequency, and state-free**; there they are cheaper than re-inference.

**What makes my preferred design fail:** if executive reasoning cannot reliably separate an
applicable trace from a superficially similar one — the T2 coherently-wrong-edit failure, and
the seven append-only classes (stale_persistence, false_persistence, configuration_collapse)
— then raw retrieval resurfaces exactly the stale trace the runbook would have pinned. It also
fails if finding the episode costs more reasoning than the procedure saves (Gen45’s bounded
loop), or if the decisive artifact is absent, since a remembered success is not present truth.
**Falsifier:** a repeated-procedure set where retrieved episodes raise success but also raise
stale-state errors versus a maintained runbook; then the runbook wins.

Runbook-vs-episode is decided by **artifact grounding and churn rate**, not by which is
"more memory."
