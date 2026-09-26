# Decision evidence — three findings that actually discriminate, and three that only look strong

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 31.**
Existing primary readings only; no new paper. Question: which findings genuinely discriminate
the practical arrangements (native files vs automated memory service vs trained/skill route)
for Brian's two pains — and which strong-looking numbers do not. C30 corrections carried:
matched-policy comparison only (Table 3's aggressive surfaces all sit at 97.5%; the 64.9%
conservative row is a different operating point — my cross-policy "preservation loses accuracy"
framing is retracted); a supplied deterministic schema is a design input, not automatically a
ground-truth oracle; simulated 100% post-verification says nothing about verifier internals; a
semantic handle needs interpretation, enforcement and time/scope design, not just a record
shape; no universal "Brian adjudicates" rule.

## Three findings that discriminate

1. **Frozen-executor bank transfer (SkillForge; my c22 `[note]`) — discriminates *stored
   procedures* from *training*.** Unchanged model, bank varied: +6.5/+4.7 (ALFWorld/AppWorld).
   Supports: a plain file store of curated procedures captures most of the claimed benefit
   without any training route. Transfer limit: small envs; second-hand numbers. **Confidence:
   medium.**
2. **Artifact-with-check beats lesson-prose (DC v2, c20 `[read]`; ReMe failure gate, c24
   `[read]`).** DC: stored discovered solver 10→99 on recurring families, and *truncated
   rewrites* rot the prose layer; ReMe: single-failure lessons harmful, reflection written only
   when the retry succeeds. Supports: capture the ran-and-worked artifact **with the check that
   marked it worked**; gate failure-lessons on a successful retry. Transfer limit: label-blind
   curation; green-but-wrong code; needs an observable check. **Confidence: high.**
3. **Floor-before-threshold + evaluator reversal (Xiong c27 `[read]`; ReMe c26 `[read]`).**
   Counter-based pruning tracks quality only with a decent evaluator — explicit reversal when
   the evaluator is weak; the α-floor is the only stated protection for rarely-used records.
   Supports: count uses; never prune below the floor; name the checker per record. Transfer
   limit: rare records unanalyzed anywhere; Brian's rare-use incidence unquantified.
   **Confidence: medium-high.**

## Three strong-looking results that do NOT discriminate

- **SkillRL +15.3** — every arm RL-trained; separates nothing for a lane that cannot train
  (c15 gap). **HippoRAG 2 "continual"** — revision never tested (c17). **INMS sharing gains** —
  no private-pool control; shows filtered retrieval, not sharing-vs-handoff (c29).

## Recommendation (opinionated)

**Native files with three conventions, no service:** (1) capture artifacts-with-checks on
*observed* recurrence; (2) usage-floor counts before any pruning, checker named per record;
(3) record-first with an explicit in-band decline and escalation to raw history — keeping a
reactive correction channel, since confidence-silencing (PAHF, c14) is the one measured failure
of ask-only designs. The discriminating evidence points at record shape and cheap counts, not
architecture; the missing perfect controls narrow tuning, not the choice.

— cairn. All cited findings from own reads c15/c17/c20/c22/c24/c26/c27/c29/c14.