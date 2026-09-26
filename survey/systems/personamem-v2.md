# System card: PersonaMem-v2 (trained agentic memory, distinct paper)

**kiln · 2026-09-26 · sources: paper full methods 2512.06688v1 (§§1–4) + HF dataset page (bowen-upenn/PersonaMem-v2). NOT the original paper, NOT v3. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Human-readable lifecycle (as described)

- **Writes:** per 5k-token chunk, the model distills implicit signals into a single memory, capped at 2k tokens; rewrite each step (M_i from C_i + M_{i-1} only — Markovian, causal, capped). Old content survives only by being re-carried; no compaction log described.
- **Replacement/history/source pointers:** replacement is whole-rewrite; history of the memory itself: none described. Source pointers back to chunks/sessions: **not described** — the 2k memory is the *sole* answer context, so provenance ends at the memory text. Contrast Hindsight documents, ReMe session files, pi-lcm message IDs.
- **Update trigger:** sequential pass over history (training/inference construction); sleep-time offline cycle hypothesized, not demonstrated. No event-driven or correction-driven update described.
- **Trained components:** Qwen3-4B + SFT cold start + GRPO (MCQ verifiable + open-ended LLM-judge rewards), MemAgent multi-turn framing. Training price: 8×H100, ~500 steps, 32×8 rollouts. Reuse price: 2k-token memory as sole context (16× fewer tokens), same model per user, no retraining per user.
- **Host work:** chunking pipeline, per-user memory store, judge infra (training only); inference = write + answer calls with the same model.

## Framework vs facility; training vs reuse costs

Research training framework + public dataset — no product, plugin, or host adapter described. Privacy-aware *dataset content* (forget requests, sensitive info) is not a deletion mechanism. Training is heavy and one-time-ish; reuse is cheap by design (2k cap) — but the cap is also the risk: silent drop of the disconfirming detail has nowhere to be audited back to, given no source pointers.

## Numbers (noted, fenced)

55.2 MCQ / 60.7 open-ended vs GPT-5 45.6/46.2; reasoning-bottleneck finding; stereotype reliance (48.9→33.0 anti-stereotypical); ownership 17.5%. Benchmark-internal; no Brian transfer claimed.

## Advice: **watch the lifecycle shape, not the weights**

Capped rewrite + Markovian update + human-readable sole-context memory is the most deployment-shaped lifecycle on the roster — and the missing source pointers are its sharpest flaw for our provenance bar. Nothing to install; the trainable part is out of scope for Brian. **Medium-low confidence** (methods read; facility absent by design).
