# Reading note — Cradle: screenshot-driven computer control with a code skill library — what do the ablations isolate?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 57.**
One source, edition pinned: **Tan et al., "Cradle: Empowering Foundation Agents Towards General
Computer Control," arXiv 2403.03186v3 (2 July 2024)** — the later ICML 2025 edition exists and
**will not be merged**. Focus: methods and memory/skill-related controls only.

C56 corrections carried: **CLIN does test later reuse** (adaptation via meta-memory under
shared rules) — my c56 line overstated; **missing direct selection-accuracy measurement is not
absence of selection-related evidence**; LATM does not validate this exact local software
workflow; no universal validation-step assumption.

**Frame held before the read (minimal):** Cradle is the panel's first screenshot-only computer
control system with an explicit **skill library written as code**. The panel's question is not
the game headlines: which ablation isolates **accumulated procedure value** (skills acquired
and reused later) from within-task reflection, and what environment change, if any, is
actually tested. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Skills as code, curated — but no control turns the library off (2403.03186v3, §3.2–3.3, §4.3, App. A/B/D) `[read]`

**Supplied vs acquired, kept honest.** Procedural memory stores **skills as code** (keyboard/mouse
wrapped in Python functions), retrieved two-stage: ada-002 embedding cosine top-K over skill
documentations, then GPT-4o picks from the subset. Skills are **learned from tutorials, manuals,
self-exploration — or pre-defined**: Stardew ships atomic+composite skills preloaded, RDR2 has a
pre-defined fight wrapper, CapCut's tool-use skill is pre-defined. Episodic memory = key
screenshots + periodic summaries. The appendix concedes GPT-4o "failed to precisely select" from
a growing library — hence the embedding prefilter; **selection accuracy is never measured**
(related evidence, not direct — per c56 correction).

**The ablations (Table 6) isolate module bundles, not the library.** React-like keeps **skill
curation** and drops reflection+episodic memory; Reflexion-like adds those back; Voyager-like
removes vision. The React→Reflexion delta is **reflection + episodic memory** (follow-tasks
improve; harder tasks still fail); the vision delta is large. **There is no same-agent
empty-vs-populated skill-library condition, and no cross-session reuse measurement** — within-run
reuse happens, but acquired-skill value is never separated from pre-defined skills, and
"generalizability" in the abstract means **the framework transfers across environments, not that
skills transfer**.

**What environment change is actually tested: none.** Games and software are fixed; icon
recognition gaps are patched with pre-computed template matching. The instructive failure is
upstream: **Claude 3 Opus's unreliable OCR produced incorrect skill generation, which then
persisted and sank complex tasks** — misperception writing durable procedures is a named failure
mode, with no correction mechanism tested.

**Costs:** interaction-step counts per task (5 trials, 500/100-step caps); API rate limits shaped
the design; no dollar ledger.

**Verdict: Cradle demonstrates the panel's target architecture end-to-end — procedures embodied
as code, curated, retrieved, executed under screenshot-only control — while contributing no
control that isolates accumulated procedure value.** The ablations tell you reflection and
episodic memory matter and vision is load-bearing; the skill library's marginal worth stays as
assumed as ever in this corpus (same gap c45 flagged), and pre-defined skills quietly carry much
of the demonstrated capability. For Brian: the persistence-of-bad-skill failure is the one
finding to respect — write-from-perception needs a provenance and a re-check path, which is
c52's inference-tagging point in a new costume. Confidence: high on ablation structure and
pre-defined-skill prevalence (explicit), high that no library on/off control exists (searched),
medium on step-count comparability across tasks.

— cairn. Source `[read]`: arXiv HTML 2403.03186v3 (edition pinned; ICML 2025 edition not
merged), opened 2026-09-26; c56 corrections carried (CLIN does test later reuse via
adaptation/meta-memory; selection-evidence ≠ direct accuracy; LATM not this workflow; no
universal validation assumption).

— cairn. Source: arXiv 2403.03186v3, opened today; edition discipline noted.