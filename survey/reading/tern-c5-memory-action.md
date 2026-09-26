# MemoryArena: action evidence is closer, but not the same question

**Tern · 26 September 2026 · reading only.**

[MemoryArena v1, §§3–4](https://arxiv.org/html/2602.16313v1) carries memory across interdependent shopping, planning, search and reasoning subtasks, resetting it at each evaluation episode. Its long-context comparator retains raw history; other systems retrieve or consolidate. Progress and final success differ, and final-success definitions vary by domain. Preference-constrained travel has a hard-score floor, making partial constraint satisfaction informative. The results do not give every external memory system an advantage, and added memory operations can increase latency.

**Verdict: useful, bounded.** This is stronger evidence about acting with earlier information than post-hoc recall QA. However, within-episode carryover is not necessarily learning a reusable procedure for an independent future task. Low completion can combine memory, reasoning and execution failures; it does not isolate one defective memory layer. The paper's explanation of representation/training mismatch is an interpretation, not a controlled causal ablation of each mechanism.

**Memo effect:** no new product winner. Keep native history in the comparison and distinguish saved-state continuation from reusable learning. Brian's priority remains avoiding repeated procedural discovery, not maximizing a heterogeneous benchmark average. The next synthesis needs both within-task action evidence and transfer to genuinely new repetitions, including upkeep cost.
