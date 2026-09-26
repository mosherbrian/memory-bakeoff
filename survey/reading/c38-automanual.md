# Reading note — AutoManual: multi-agent wiki authoring as an API — what do the controls isolate?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 38.**
One primary methods/control read (Tern): **AutoManual — Chen et al., arXiv 2405.16247v4
(NeurIPS 2024)** — "Constructing Instruction Manuals by LLM Agents via Interactive Environmental
Learning"; environments **ALFWorld / MiniWoB++ / WebArena (Reddit)**. **Skeleton correction
note:** my first-draft header guessed id 2506.24743 with a NetHack framing — wrong identity,
retracted here; the read below is the actual source (confirmed via arXiv API title match).
Architecture as commissioned: **Planner acts (code plans), Builder updates rules, Formulator
writes the Markdown manual.** Questions: **separate building from evaluation**; the
**Planner/Builder/Formulator contribution** (who carries the win?); **same-executor and
human-written-manual controls**; what is **supplied** (demonstrations, environment knowledge,
rewards); **smaller-model transfer**; **acquisition cost** (App. D reports ~$14 for
building+formulating, ALFWorld context — verified at source); and what "changed environment"
means for the manual's validity. The sharp question: **what does case-conditioned prompting
actually isolate?**

C37 qualifications carried: HotpotQA full-vs-retrieval-only is **+8 (39−31), not +3** — +3 is
full-vs-insight-only (ALFWorld +4); my c37 sentence compressed the two comparisons and is
corrected here. Appendix C has hardware, D/E settings, but **no located full acquisition
ledger**. Same-task adaptation remains learning; the single-attempt holdout is useful evidence,
not a universal admission rule.

**Frame held before the read (kept minimal, no invented mechanism).** A manual is **explicit,
human-readable procedural knowledge with revision history** — closest artifact yet to Brian's
files-as-procedures lane; the cycle asks which control proves the manual carries the win.
Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## What the controls isolate (2405.16247v4, §3.1–3.4, §4.1–4.2, App. D, F) `[read]`

**Identity note:** the arXiv id is **2405.16247** (my skeleton's 2506.24743 returned "article
not found"; confirmed via arXiv API, v4 matches Tern's edition).

**Building ≠ evaluation, cleanly:** Building = Planner (code plans) + Builder (rule CRUD) +
Consolidator (merges/deletes past 12 rules) on **36 training tasks**, GPT-4-turbo throughout;
Formulator compiles rules → Markdown manual; Testing = a test-time Planner with the manual on
**134 unseen validation tasks**. Test Planner may **replan up to 3 times** — not a strict
single-attempt holdout.

**Headline and controls:** 97.4% (GPT-4-turbo) / **86.2% (GPT-3.5-turbo test — manual authored
by GPT-4 lifts the smaller model from ReAct's 41.9%)**; MiniWoB++ 98.3/92.7. Baselines
re-implemented with the same models; **examples: 12 for ReAct/Reflexion/ExpeL, 6 for AdaPlanner,
1 for AutoManual** (simplest task) + a few initial rules derived from it. **No human-written-
manual control exists.** Planner+Lib (skills+reflections, no rules): 66.5% — the "path
dependency" contrast. ExpeL re-implementation scores 52.2 (its trajectories are single actions,
not code) — well below ExpeL's own-paper numbers, a cross-paper comparability flag.

**Ablations (ALFWorld):** offline rule management 90.7 vs online 97.4 — rules need in-loop
environment verification; **no skill/reflection libraries 89.5** (rules alone lose details);
**no case-conditioned prompts 93.8 vs 97.4**; manual formatting adds over raw rules and cuts
error steps.

**What case-conditioned prompting isolates:** the Builder first **attributes the major error —
"Imperfect Rules" vs "Imperfect Agent"** — and only then gets a targeted prompt. It is a
**write-gate by attribution**: don't author a lesson from an execution flub. +3.6 points; same
axis as ReMe's retry-gate and PAHF, implemented as error triage.

**Record schema is the richest read this far:** each rule = type (6 types incl. *Unsolved
Error*), content **beginning with its applicability scope**, a trajectory-grounded example, and
**validation logs with episode/rule IDs tracing its evolution** — provenance and scope at write.

**Acquisition cost — located:** App. D: **"API call cost for building and formulating stages is
about $14 in total"** (ALFWorld build; test-time cost not included). The only paper in the sweep
with a real acquisition price.

**Changed environment:** means *build a manual per environment*; nothing claims a manual
survives mid-use environment change; online validation covers the build environment only.

**Verdict: strongest artifact-shaped procedural-learning evidence in the sweep — with toy-domain
magnitudes.** Confidence: high on mechanism/ablation directions and the $14, medium on
magnitudes (ALFWorld/MiniWoB; replan-at-test; weak ExpeL baseline).

— cairn. Source `[read]`: arXiv HTML 2405.16247v4, opened 2026-09-26; c37 marginal correction
carried (HotpotQA full-vs-retrieval-only +8; +3 is vs insight-only; exam frame not a universal
admission rule).