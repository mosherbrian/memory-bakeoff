# System card: StateMem / StateMemBench (explicit state discipline)

**kiln · 2026-09-26 · ~500w · advice only, no installs. Source: full methods read, arXiv:2608.19652v1 (Fan et al., UIUC; §§1–7 + appendices E–G skimmed via HTML). Roadmap inputs + BRIAN-PRINCIPLES as context. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack".**

## Identity (academic method + benchmark, not a product)

StateMemBench: 234 multi-session scenarios (190 short ~165 turns, 44 long fused ~600 turns) across research/shopping/finance, five trap modes (status, salience, sequence, compound, anti-trap) generated as symbolic event programs with deterministic replay as gold. StateMem: a state-first method — TurnEncoder (one LLM call/turn → units of (id, content, priority hard/soft, source, deps)) → Update (apply flagged supersessions; deterministic Rechecker traverses the dependency graph O(|E|), marks affected units needs_recheck, zero LLM calls) → Test time (deterministic assembly of the valid-state block + one answer call with recompute guidance). Superseded units persist inactive for audit; needs_recheck units stay active but flagged.

## Concrete update/read and scope semantics

- **Update authority:** the TurnEncoder (LLM) flags supersessions and volunteers replacements; the deterministic layer only applies and propagates. Authority is split — LLM proposes, rules dispose — which bounds but does not remove extraction risk.
- **Scope:** units carry priority (hard/soft) and source; dependencies are typed (derived_from, coupled_with). Dates are metadata-level only — unlike MemStrata's validity intervals or Zep's edge valid-time, there is no valid-time axis; currency comes from status flags, and conflicts are *supplied explicitly* by construction ("Since we have 1600 annotators…"), never inferred. Transfer to Brian's world, where contradictions must first be detected, is therefore untested by this paper.
- **Read:** deterministic valid-state assembly (grouped by priority/source, flagged units shown with triggers) plus one recompute-guided answer call.

## Closed-pool evaluation limits (load-bearing)

Grading is closed-pool: gold vs precomputed drift answer vs distractors — it separates drift from nonsense but never tests open generation, and the authors state StateMem mirrors the trap policy family, so margins read as an **upper bound** (§6.1 generalization test noted). Drift rates are judge-labeled ceilings (binary κ=0.67, cross-family 0.37; humans assign less). Single run per config. Two results cut both ways: dependency propagation *over-propagates* on anti-traps (−12.5pp; removing it scores higher) — explicit invalidation needs the restraint the anti-trap mode tests; and the lightweight answer-time wrapper (Trace ≤250 words + 4 Resolve precedence rules, +155-token instruction, **no extra LLM calls**) beats full StateMem when the transcript fits (≥0.567 vs 0.283 on Qwen) — persistence pays only past context limits. Structure's isolated share is +15 to +32 points over a length-matched control.

## Fit for Brian / advice: **watch, medium-low confidence**

Closest paper to our roadmap's layer-2 question, and the wrapper's four precedence rules (later-supersedes-earlier, rules-over-instances, recompute-derived, retire-only-on-explicit-supersession-or-expiry) are the most portable artifact — a prompt-level discipline Brian could adopt without any system. But it is not deployable software (no repo evaluated here), needs an LLM per turn plus answer call, and its conflicts arrive pre-labeled. Take the precedence rules as a textual procedure (cf. c5 pattern); leave the machinery on watch until a persistent-store need passes context limits.
