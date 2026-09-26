# System card: Reflexion (trial/evaluator protocol, reset boundaries)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2303.11366v4 (§§1–5, App. B–D) + author repo noahshinn024/reflexion (layout: alfworld/hotpotqa/programming/webshop runs dirs; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Buffer reset/persisted, retries, feedback, host supply

- **Buffer:** episodic reflections appended per trial, hard-capped sliding window (Ω = 1–3: last 3 in AlfWorld, max 1 in programming). Crucially, the buffer is **reset per task** — it persists across *trials of one task*, never across tasks or into a later environment. There is no cross-task store in the paper design.
- **Retries invoked by:** the loop itself — run until Evaluator passes or trial budget exhausts (12 trials AlfWorld; 3-consecutive-failures stop on HotPotQA; test-suite-gated on code). No external scheduler; the harness *is* the loop.
- **Feedback exists as:** binary/heuristic signals (AlfWorld loop-detection: same action×3 cycles or >30 actions), exact-match grading (HotPotQA), self-generated unit tests (≤6, AST-filtered, code). The paper's own FP analysis bounds the trust: self-tests pass wrong code 16.3% (MBPP) vs 1.4% (HumanEval); without test guidance, reflection *hurts* (52% vs 60% baseline); weak models gain nothing (starchat 0.26→0.26); WebShop shows no improvement where exploration diversity is required.
- **Host must supply:** a resettable episode, an evaluator signal per trial, and a trial budget. That is a benchmark harness, not a memory system.

## Recovery note vs long-lived memory

Reflexion is a **current-task recovery note with a bounded buffer and a stop rule** — closer to our c27 trail note plus retries than to any durable store. Nothing in the design answers cross-task reuse, changed environments, or retirement; the 91% HumanEval figure is pass-after-trials, not first-attempt learning, and nothing carries to the next problem.

## Prototype vs maintained adapter

Author repo is a 2023 research prototype (per-task run scripts + runs directories). No maintained host adapter inspected; any Brian transfer is custom glue: resettable task + checker + bounded retry loop + a buffer that is deliberately thrown away.

## Advice: **borrow the loop shape for checkable tasks, never as memory**

The transferable part is narrow and honest: on tasks with a real checker, keep last-N reflections in-context across bounded retries, stop on consecutive failures, and distrust self-generated tests at measured FP rates. As "reusable learning" it contributes nothing — by design it resets. **Medium confidence** (protocol read closely; transfer scoped to checkable tasks).
