# Contrarian, cycle 30 — append both, let the executive read, defer the merge

**corvid · 2026-09-26 · cycle 30.** Signed opinion; ROLES.md “best rival idea.” Existing evidence;
no new sweep. Confidence **medium**.

**Strongest practical alternative to explicit conflict/lifecycle machinery.** When two hosts report
incompatible lessons, keep **both source episodes verbatim, append-only** (git already preserves
both byte-wise), tag each with **source host + environment identity + timestamp**, and let the
**executive read both at use**. Do not auto-merge.

**First, distinguish the two cases — they need different responses.**
- *Different environment/scope*: not a contradiction. Same procedure valid under different configs;
  record applicability conditions and keep **both as conditional guidance**.
- *Real contradiction at the same scope*: incompatible claims about the same conditions. Here the
  executive compares each report’s environment facts and outcome — an **artifact check**, not a
  semantic merge — and, if still unresolved, defers to **Brian or the artifact**.

**Why read-both is cheaper than machinery first.** A conflict/lifecycle layer needs provenance,
scope and authority metadata to be meaningful (c28); without them it merely **hides** the
disagreement. ReMe/Hindsight offer consolidation, but their dedup/threshold mechanics can fold
distinct beliefs, and byte-level git merges carry no semantics. For a few small episodes, an
executive reading both is cheaper and lossless.

**Authority stays separate from confidence.** Two agents disagreeing is *evidence*; neither
confidence score adjudicates. Only Brian’s direction or an artifact settles authority. The
executive reports the conflict; it does not crown the louder claim.

**Recommendation.** Append-both with source/env/scope tags; executive reads and resolves; escalate
same-scope contradictions to Brian. **Reversal:** if unresolved contradictions are frequent enough
that per-use reading is costly, or hosts must act autonomously without an executive, a lifecycle/
merge mechanism earns its cost.

— corvid. No experiment.
