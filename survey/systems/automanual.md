# System card: AutoManual (typed rules + online builder, manual artifact)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2405.16247v4 (§§1–4, App. A–C) + author repo minghchen/automanual (layout: automanual_alfworld/miniwob/webarena builders, formulate_manual.py; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Rule schema, revision/deletion, evidence survival

- **Schema:** every rule carries Type (6 kinds: Special Phenomenon/Mechanism, Helper Method, Success Process, Corrected Error, Unsolved Error), Content (scope-first), Example (trajectory code + error-prone details), Validation Logs (episode + rule IDs tracing evolution). Managed via write_rule / update_rule / stop_generating; Consolidator adds get_trajectory / delete_rule over an Nmax cap.
- **Revision:** Builder updates per-trajectory with case-conditioned prompts (Imperfect Rules vs Imperfect Agent first, then targeted prompts); Consolidator merges/deletes over cap *after re-inspecting trajectories*, retaining details. Online beats offline (90.7 vs 96.5-class ablation direction) because rules get environment-verified.
- **Old evidence survival:** trajectories live in per-task-type skill/reflection libraries *separately* from rules, and Validation Logs trace rule lineage — so rule deletion does not on its face delete the evidence. But recoverability of a deleted rule's content is **unreported** (distinguished from absent: the libraries + logs exist; a restore path is not described). Failure evidence is first-class: Corrected/Unsolved Error rule types plus the Path Dependence case study.
- **Final artifact:** Formulator categorizes rules into a Markdown manual; smaller models execute from it (86.2% GPT-3.5 on ALFWorld — noted, not compared across settings).

## Failure evidence and host dependencies

Documented failures: Path Dependence (blind success-replication), planner ignoring rules (App. A: adherence unenforced), GPT-4-turbo dependence for reliable rules, all-rules-in-context scaling limit (authors suggest RAG), exploration insufficiency. Host deps: ALFWorld/MiniWoB/WebArena simulators, binary episodic reward, one human demo; repo is benchmark-builder prototype scripts (main_build/main_test), no host adapter, no maintained plugin.

## Vs ExpeL insights and our guidance

Typed, scoped, example-grounded rules with lineage beat ExpeL's armchair-general insights on the paper's own ablations — the mechanism difference is online verification + error-prone detail, not scale. For Brian: the schema (scope-first content + example + validation log) ports to native skills at ~zero cost; the Builder/Consolidator/Formulator loop needs simulator + rewards + GPT-4-class builder and stays watch.

## Advice: **borrow the schema, watch the loop**

Deploy rule-type + scope + example + validation-log as skill format; leave Planner/Builder/Formulator on watch (prototype, benchmark-only evidence, adherence unenforced even there). **Medium-low confidence** (methods + layout read; no runs).
