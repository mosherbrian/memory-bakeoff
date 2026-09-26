# System card: LATM (tool maker/user/dispatcher, static functions)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2305.17126v2 (§§1–6, App.) + author repo ctlllll/LLM-ToolMaker (notebooks toolmaker/tooluser, tools/*.json cache, bbh data; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Making / validation / dispatch / execution / recovery

- **Making:** GPT-4 proposes a Python function from 3 demos (temp 0.3), max 3 retries on execution errors. Maker capacity is load-bearing: 3.5-turbo fails hard tasks 0/5 (non-general tools); easy tasks work with small makers.
- **Validation:** maker writes unit tests from 3 validation samples and executes — but fixes *test calls only, never the function*. Verification demonstrates NL→call conversion, not correctness beyond 3+3 samples. CoT-as-tool adds nothing (36.8 vs 79.7): functions beat prose, the medium matters.
- **Dispatch:** lightweight dispatcher LLM routes cached-tool vs maker (95–96% routing accuracy measured). **Execution:** tool user (3.5, temp 0) translates NL→call once; calls run in Python. **Recovery:** beyond maker retries, undescribed — no runtime monitoring, repair, or upgrade path (explicit future work).
- **Persistent artifact:** tools/*.json cache + dispatcher repository. No versioning, no retirement, no contradiction handling in the inspected design.

## Static-function vs environment interaction (the boundary)

LATM tools are pure static functions over supplied arguments: they compute, never perceive. That bounds them strictly inside algorithmic-reasoning tasks (deduction, sorting, scheduling math). Against AWMAS wrappers (which replay action sequences blind to intermediate state — the flight pop-up failure), LATM avoids the trap by never touching state at all — and thereby excludes every Brian procedure that reads the world (rollouts, tests, triage). Applicability boundary is explicit: no observation input, no tool.

## Host burden / advice: **borrow the split, watch the factory**

Maker/user/dispatcher division of labor ports as an idea (strong model builds once, cheap model runs often, router in front); the factory itself needs labeled demos + validation samples + executor + cache ops per task family, with no update story. For Brian: executable helpers stay hand-built and reviewable; generated tools earn nothing without the validation samples he doesn't have. **Medium-low confidence** (methods + repo read; costs in 2023 API units, not transferred).
