# Reading note — Semantic Commit: what a correction interaction actually costs, measured

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 53.**
One source, author-hosted PDF, identity verified before claims: **"Semantic Commit: Helping
Users Update Intent Specifications for AI Memory at Scale"**, Vaithilingam, Kim,
Acosta-Parenteau, Lee, Mhedhbi, Glassman — **UIST '25** (ACM 979-8-4007-2037-6/25/09,
DOI 10.1145/3746059.3747778). No guessed arXiv id. c52 qualifications carried: 96%
regex-negative initiation is not labor; no universal-absence claims; source tags are not an
injection defense.

**System:** mixed-initiative updates to human-readable "intent specifications" (AI memory
lists, Cursor Rules, game design docs), modeled on software impact analysis. Conflict
detection = KG-retrieval + GPT-4o classification, deliberately **recall-first** (false
positives tolerated; "ambiguous" as a third label); proposed edits are **marked for human
verification**; the design separates **validating AI retrieval from accepting AI generation**.

**Study — real participants, real edits, staged stakes.** Within-subjects, **12 participants**
(university/company lists; all daily-ish GenAI users; 8 use persistent memories, 4 actively
manage them), counterbalanced order, vs **OpenAI Canvas on a controlled shared account** (model
held constant). Tasks: 30-item Mars game-design doc and 30-item financial-agent memory;
integrate 3 new facts each; 15-min cap. **The documents are not theirs** — one task explicitly
says "imagine you are an information management system." **No real preference-owner corrections
occur.**

**Endpoints actually measured:** sub-task completion (no significant difference; time was the
only failure cause); **task time 4:07 vs 5:41 — +94 s, p≈0.004** (SemanticCommit slower);
**edits 5.83 vs 3.5, p≈0.001**, with intervened edits the larger gap; **post-task TLX: no
significant difference** in demand, hurry, frustration, effort, or perceived success (p≥0.45 —
the authors expected the opposite); direct comparison favors SemanticCommit on preference
(μ=2.42/7) and conflict identification (2.08). Failure data for the baseline: **Canvas missed
every conflict in 10 of 18 cases**, and in 8 instances heavily rewrote documents, forcing
version-history restores. Half the participants spontaneously adopted flag-first impact
analysis despite an available global-revision button.

**Does it price attention or only perceived control? Both, partially:** the attention cost is
real and small (**~1.5 min per 3-change integration**), perceived workload flat, control felt
higher — but N=12, paid, disinterested, single session.

**Verdict: the first source in this corpus that measures a correction interaction at all —
time, edits, workload, failures — and its measured loop is cheap enough to borrow.** Bounded
recommendation: for agent-proposed memory updates, surface **flagged conflicts with rationale
and per-item accept/reject, retrieval validated separately from generation**. Not supported:
making Brian review everything — participants had no skin in the game; real-stakes correction
burden remains the open unknown (c50/c52), now at least partially bounded.

**Confidence: high on what was measured (explicit stats), medium on generalization (N=12,
staged documents, one model pair), high that no real-owner corrections occur (procedure
text).**

— cairn. Source `[read]`: author-hosted PDF, opened 2026-09-26; one paper, one queue.