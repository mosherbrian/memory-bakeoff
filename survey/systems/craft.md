# System card: CRAFT (validated tools + multi-view retrieval)

**kiln · 2026-09-26 · sources: paper full methods 2309.17428v2 (§§1–4, App. B–C) + author repo lifan-yuan/CRAFT (construct_toolset.py, retrieve_tools.py; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Solution→validation→abstraction→dedup→retrieval→execution

- **Generate:** min-max diverse sampling of training problems; GPT-4 writes specific solutions; bug-free + correct-output only survive.
- **Validation is double-gated:** filter-then-verify — incorrect solutions discarded *before* abstraction, then the abstracted tool must re-solve the original problem. Validation brackets abstraction on both sides, the strictest admission seen in this survey.
- **Abstract:** variable/generalize names, wrap inputs as arguments, assign name + docstring. Ablation: dropping abstraction costs the most after names.
- **Dedup:** group by (name, arity), GPT-4 keeps the most comprehensive. **Revision/history: none described** — the toolset grows monotonically (Fig. 3 scaling curve); no update, delete, or retirement path.
- **Retrieval:** model writes needed function name + docstring, multi-view match (problem/name/docstring) with majority vote, top-3; empty on total disagreement (abstention, like AutoGuide). Names carry the most weight (−6.6 SAcc without).
- **Supplied:** task APIs (vision models, pandas/sympy), ground-truth labels for validation, backbone GPT-3.5/4. Persisted: toolset files (code + names + docstrings), ~$2,500 build cost stated.

## Borrowable vs harness

Borrowable: double-gated validation order (filter, abstract, re-verify), name+docstring as the retrieval key, majority-vote abstention. Harness-bound: min-max sampling over labeled training sets, GPT-4 extraction, benchmark executors. No revision story — combine with a registry (c57) if adopted. **Medium-low confidence** (methods + code paths read; costs as stated, not transferred).
