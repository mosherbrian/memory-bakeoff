# Code as Policies: reactive execution with session reuse

Tern · cycle44 · 26 September2026. Primary [v4 methods III–V](https://arxiv.org/html/2209.07753v4) and Appendix E/K inspected. High confidence in mechanism distinctions; medium practical transfer.

The source explicitly appends instructions/responses to an LMP session and inserts newly generated functions into scope for future use. “Zero accumulation” is therefore incorrect. This supports session history and reusable code, not a measured long-term maintenance/retrieval system.

The generated program can repeatedly query perception and change control accordingly. Perception/control primitives and prompting examples are supplied. Quantitative robot comparisons are simulated; real platforms demonstrate capabilities without quantitative evaluation. HumanEval and RoboCodeGen assess code against tests, not physical task success. Hierarchy improves aggregate results, but not every model/generalization subtype. TableIII also has a seen spatial-geometric condition where CLIPort wins. [Source](https://arxiv.org/html/2209.07753v4#S4).

**Decision:** generated helpers can contain observation, conditionals and loops. This complements retained prose for interpretation and rationale; it does not divide intelligence into code-for-mechanics and prose-for-judgment. A function may call another language-model program, and a prose procedure can direct tests and observations. Pick the representation for the operation and its maintenance burden.

**Evidence boundary:** no lossless cross-session record or continual-library improvement curve was established in this read. Do not convert that gap into proof of absent persistence. Similarly, a generated response can be checked by execution without correctness being guaranteed. API outputs may be noisy; program execution need not yield deterministic real-world outcomes. Observability limits both code and prose.

**Transfer:** software tools can also query state and react. That is an engineering capability, not a measured benefit for Brian from this robotics paper. Avoid a new obligatory wrapper, per-use check or sandbox project. The next synthesis should state what existing agent-owned work changes, if anything, rather than build a machinery bundle from separate papers.
