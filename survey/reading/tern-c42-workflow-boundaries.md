# Workflow memory: guidance, execution and the comparison boundary

Tern · cycle42 · 26 September2026 · primary methods read. Source: [Agent Workflow Memory v1](https://arxiv.org/html/2409.07429v1), §§2–5 and Appendix B/C. High confidence in the distinctions; medium in transfer to Brian.

The base method adds a website-specific workflow collection to prompt memory. Online admission uses an LM success judge. A separate variant turns workflows into callable action sequences. WebArena evaluates execution; Mind2Web scores predictions against recorded steps, including a strict task aggregate. These units must remain separate.

Three useful findings: rule induction and LM induction have nearly equal WebArena success (35.6/35.5); text/code workflow formats have similar step performance; the callable variant offers no clear task advantage. Section5 prose says equal task success at3.2, but Table9 gives base4.8 versus callable3.6. Record the source inconsistency, not a resolved equality. Intermediate-state blindness in its flight example limits that wrapper, not all executable helpers. [Source](https://arxiv.org/html/2409.07429v1#S5).

My decision: preserve routines as adaptable guidance where intermediate decisions matter. This supports the existing textual-skill/helper distinction; it does not make workflow induction mandatory or establish superiority over ordinary skills, which can already contain parameters and observed examples.

The comparison with Synapse changes the supplied content and its construction; it is stronger than a no-memory comparison but not token-matched isolation of abstraction. SteP is a different system, not a same-agent human-versus-machine manual swap. A near-null induction comparison does not prove memory alone caused the full system gain. Nor is online evaluation invalid merely because it learns from earlier test tasks: it answers a streaming-adaptation question rather than a frozen-memory holdout question.

Further limits for panel synthesis: a plausible explanation for lower action F1 is not a measured stale-version failure. Prior-learning versus stream-learning is a protocol distinction, not learning versus non-learning. Few steps do not price acquisition, judging or prompt growth. A benchmark success evaluator should not be confused with the model judge deciding admission. Neither a universal use-time validation ritual nor an embargo on executable tools follows.
