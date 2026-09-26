# Reading note c73 — AMA-Bench: is retrieval and appropriate application measured separately?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 73.**
Skeleton first; **one primary: arXiv 2602.22769 — title/authors/edition verified before methods**
(queued as AMA-Bench; earlier identity check was made at cycle 9 with methods unread). If identity
fails: bounded failure report, no substitute sweep. Charge: retained unit; whether task actions
**execute**; feedback provenance; within/across-episode reset; whether **retrieval and
appropriate application are separately measured**; any correction/repeated-mistake endpoint. One
control that changes advice, one decisive limitation. C72 carried: shared backbone ≠ identical
policy/compute; subset weakness ≠ isolated authority transfer; stream accumulation ≠ fixed
transfer; knowledge revision ≠ sponsor authority. No probe/install/sweep/Laya rerun.

*(facts + verdict appended below)*

## Identity (verified before methods)

**arXiv 2602.22769v4 — "AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications,"
Yujie Zhao et al. (ICML-tagged)** — the cycle-9 identity hold resolves; edition read is **v4**.
Same group as Agent-Mem; the paper also proposes a method (**AMA-Agent**: causality-graph
construction + tool-augmented retrieval), so treat benchmark and method claims separately.

## What the controls actually are

**Retained unit:** whole agent-environment **trajectories** (states, actions, observations, tool
outputs) — the corpus's first trajectory-grounded memory benchmark. **Real subset:** logs from six
executed domains (web, SWE, text-to-SQL, embodied, gaming, tools), environments treated as
**black boxes**; 2,496 QA pairs, 12 per trajectory, authored by graduate annotators with
second-annotator cross-review. **Synthetic subset:** executable TextWorld/BabyAI backends with
full MDP access, machine-verifiable golden QA, horizon scaled by difficulty vectors, perturbations
(action stochasticity, observation verbosity).

**Do task actions execute for scoring? No.** Memory systems are scored **offline**: construction +
retrieval over recorded trajectories, then open-ended QA judged by **LLM-as-judge (Qwen3-32B)**
with cross-judge and human-agreement appendices. Capabilities: Recall, Causal Inference, State
Updating, State Abstraction.

**Retrieval vs application:** the taxonomy separates retrieval-side (Recall, Causal) from
evolution-side (State Updating/Abstraction) — but **appropriate application in action is not
measured at all**; no re-execution, no correction or repeated-mistake endpoint. State-Updating QA
asks *about* changes; it never requires acting on them.

## One control that changes advice

**Memory systems fall short of the plain long-context baseline on long-horizon agentic
trajectories while beating it on dialogue-centric benchmarks** — same systems, two corpora types,
verdict flips. It retires any dialogue-benchmark ranking (LongMemEval-style) as evidence for
agent-trajectory memory, mine included.

## One decisive limitation

**The endpoint is judged answers about logs, not executed consequences.** Application — the
sponsor's measured bottleneck — is exactly what AMA-Bench does not reach; and the headline
AMA-Agent gains are authors' own benchmark **and** own method, with the judge a model from the
open-weight ecosystem they build on.

**Verdict: identity resolved; a serious trajectory-memory benchmark whose missing cell is the
panel's central one — application. Cite its retrieval findings as second-source; claim nothing
about correction or repeated mistakes from it; the application-evidence gap the cycle asked about
remains open.**

**Confidence: high on design facts (explicit protocol), high that no execution endpoint exists
(searched scoring sections), medium that the real-subset 12-QA-per-trajectory density supports
per-category claims (thin per category).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md,
RECOMMENDED-DESIGN.md, panel-response-c72.md, CAPABILITY-MATRIX.md context.