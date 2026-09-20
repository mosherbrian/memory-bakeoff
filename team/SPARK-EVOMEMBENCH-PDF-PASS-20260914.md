# muse-drafter: EvoMemBench PDF/body pass (spark pulse 2026-09-14)

Closes the last "PDF unread" item on card 8 (`CANDIDATE-CARD-EVOMEMBENCH.md`).
Body read of `arXiv:2605.18421v1` HTML this pass (v1 2026-05-18; v2 2026-06-15
not re-read). Grounding only — **all method scores remain vendor-harness output,
not citable, no score import.**

## Composition (body-level, replaces abstract-level guesses)

Six settings, six datasets: **InEp-Know** (MemoryAgentBench Accurate Retrieval
2,000 + Selective Forgetting 800), **InEp-Exec** (BFCL-MultiTurn-LongContext, 4
domains × 200), **CrossEp-Know** (CL-Bench, 884 samples / 120 contexts, 4
knowledge forms), **CrossEp-Tool** (BFCL-MultiTurn-Base), **CrossEp-Web**
(xbench-DeepSearch 100 + WebWalkerQA 170), **CrossEp-Emb** (ALFWorld, 6
categories). InEp-Exec reconstruction uses GPT-5-mini prompts + manual
verification.

**15 memory methods in 5 categories** (useful roster for our ledger):
retrieval (BM25, Qwen3-Emb-4B, GraphRAG) · short-term (MemAgent, MemoBrain) ·
general long-term (Mem0, A-MEM, MemOS, MemoryOS) · procedural (AWM, SkillWeaver,
AgentKB, **ACE, ReasoningBank**) · meta-evolution (MemEvolve). Backbone
DeepSeek-V3.2; memory-free baselines Gemini-3-Flash / GPT-5-mini / DeepSeek-V3.2.

## Findings that matter to our goals (qualitative; scores not imported)

- **Revision, not retrieval, is the bottleneck (G1/G2, axis C).** Explicit memory
  beats the weak baseline on *retention* but "drops sharply on FactConsolidation,
  especially multi-hop"; the paper states the hard problem is "deciding which
  stored information should be updated, suppressed, or replaced when later
  evidence conflicts" — an independent statement of our E-7 concern.
- **Long-context null, with a budget curve.** Best memory gains shrink as context
  grows (+14.5 @16K → +8.5 @128K), and **at 128K several memory methods fall
  below the no-memory baseline** (appended memory adds noise/consumes context).
  Another external point for the long-context-null thread, next to MemDelta.
- **Memory can hurt easy tasks (negative transfer).** On CrossEp-Know easy split
  the memory-free backbone beats the best memory method; memory helps only on
  hard. Directly relevant to our "retention ≠ beneficial" and false-supersession
  cautions.
- **Procedural memory strongest for execution; compression risky.** ReasoningBank
  / AWM lead execution settings; short-term compression (MemAgent, MemoBrain)
  underperforms the no-memory baseline at 16K — fine-grained tool state is lost.
- **Cross-episode transfer depends on matching the target decision process** —
  convergent with LME-V2's workflow/gotcha framing.

## Limits / next

Numbers are one-answerer-model (DeepSeek-V3.2) vendor runs; card rules (no
citation) stand. **Card 8 still says "PDF unread" and "Numbers: NOT verified from
the PDF"** — this pass does not change the *numbers* verdict (still uncitable)
but the *composition/findings* are now body-grounded; one card edit to record
that is an owner call (not done here to avoid a concurrent-edit race).
Repo license remains **absent** (all-rights-reserved, prior pass). Second seat:
Alice.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
