# kiln (Practitioner) — c80: guard first, compiler delivery alongside

**kiln · 2026-09-26 · ≤350w · existing notes only. Quoting ROLES fit duty. Roadmap inputs, principles, matrix, recommended design as context.**

## ONE design (characterizable, unbuilt)

- **Components:** (1) project-scoped cc-safety-net rulebook, one rule (python-not-python3), fixture-tested, additive-only; (2) Perseus compile of the same project directives to CLAUDE.md/AGENTS.md with installed SessionStart + UserPromptSubmit render hooks on Claude; native file + reload on Pi.
- **Contracts:** rulebook denies covered invocations pre-execution (fail-open on invalid config, visible via status/doctor); compiler re-renders per prompt on Claude, file-drop on Pi; budget analyzer exists as a command but is *not* wired into either path (integrating it remains work). Integrity drift checks default off; `render --strict` gates warnings, not tokens — neither gate rides the default hooks.
- **Owner (proposed):** survey operator seat for pilot duration; long-term owner unresolved, explicitly not Brian by default.
- **Tests (described, unexecuted):** blocked python3 case, allowed python case, out-of-scope unaffected, render freshness after source edit, degraded-state visibility, legacy-file sweep. No obedience or benefit measurement claimed.
- **Custom glue remaining:** hook installation per machine, Pi reload discipline, rulebook authoring for the one rule. Nothing else built.

## Default vs alternative; gaps left

Default first pilot is above: enforcement + delivery on current hosts, no new runtime. Optional alternative: Letta week (runtime migration) or claude-mem delivery — both unneeded until the default's gaps bite. Left open in requirements 2–5: enforced load bounds (no mechanism adopted), protected rules beyond managed-policy scope (uninstalled), semantic relevance/selection (judgment, not mechanism), cross-host refresh on Pi (convention). None blocks the pilot: each is a named unknown with an owner question, not a missing prerequisite — the pilot tests whether enforcement + delivery move the two pains, and stops there. **Medium-low confidence.**
