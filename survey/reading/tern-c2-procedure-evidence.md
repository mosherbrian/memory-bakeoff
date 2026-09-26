# AgentRunbook-C: a procedure for reconstructing evidence

**Tern · cycle 2 · 26 September 2026.** Primary methods read: [LongMemEval-V2, §§3.3–5.1](https://arxiv.org/html/2605.12493v1). Explore; no reproduction.

**What the method establishes:** trajectories become files. A coding agent gets a retrieval workflow, a manifest and inspection helpers, then returns a note and selected spans to a fixed downstream answerer. The outcome is question-answer accuracy and query latency, not task execution. Removing the workflow worsens both reported tiers' accuracy and latency. Helper effects are mixed; the medium-tier accuracy increases without them. These are configuration-specific ablations, not a universal benefit from more tools. Failed trajectories are retained alongside successful ones.

**My interpretation, medium confidence:** reusable procedure and episodic reconstruction can cooperate. Here the reusable procedure governs how to investigate; it does not prescribe every domain answer. This is a useful third option between recording every solution as a skill and rediscovering the entire investigation each time. It supports keeping a source archive and a small repertoire of search/check routines. It does not settle their economics on Brian's work.

**Memo effect:** distinguish reusable investigation methods from reusable task solutions. Q5 should compare both with unstructured reconstruction. Q3 remains open on current applicability and maintenance cost. The paper offers no basis for calling all runbooks verified, all reconstruction expensive, or a remembered workflow presently valid.

**Next, started immediately:** read outcome-oriented procedural-memory studies for matched controls, transfer and revision failure. Panelists are concurrently examining applicability, native preference memory, SKILL.state, Perseus and pi-lcm; their contributions are the external dependency for the next joint synthesis.
