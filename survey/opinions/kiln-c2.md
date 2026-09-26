# kiln (Practitioner) — cycle 2: native preference/procedure recommendation

**kiln · 2026-09-26 · from current official docs (code.claude.com/docs/en/memory, read this session) + cycle-1 cards. No installs; behavior below is docs-described, not installed-behavior. Quoting ROLES.md: "judge real systems as a builder would: install cost, failure modes, maintenance, fit for Brian's stack" and "would deploy / would watch / would skip".**

## What the docs actually give us (separate the mechanisms)

- **Auto index loading:** project/user CLAUDE.md files plus the first 200 lines (or 25KB) of the auto-memory MEMORY.md index load into *every* session. Topic files load on demand only. Skills load only when invoked or judged relevant. So there are three cost tiers: always-loaded (keep tiny), on-demand (the archive), invoked (the procedure).
- **Selective skill retrieval:** skills are the right home for the recurring procedure — they stay out of context until relevant, unlike memory. Docs are explicit: multi-step or area-specific content belongs in a skill or path-scoped rule, not in CLAUDE.md.
- **Scope/override:** CLAUDE.md scopes nest (managed → user → project → local → subdirectory, later read last); user rules and project rules do *not* override — on conflict Claude may pick either. Auto memory is per-repo, machine-local, not shared across machines; subagents don't inherit it. Specificity and concision drive adherence, not authority.
- **Correction and history:** auto-memory files carry `modified` timestamps and are editable via `/memory`; CLAUDE.md is versioned in git. Auto memory is *not* versioned, not reviewed by commit, and capped by the index limit — stale entries beyond the cap silently stop loading.

## Recommendation for Brian now

1. **Preferences:** personal cross-project prefs in `~/.claude/CLAUDE.md`; personal per-project items in `CLAUDE.local.md` (gitignored); team-shared standards in repo `CLAUDE.md`, target under 200 lines. Leave auto memory ON as the capture net, but audit via `/memory` — treat unreviewed auto-entries as untrusted. **Would deploy. Medium confidence** (docs + cycle-1 baseline).
2. **Recurring procedure (e.g. model-test/rollout runbook):** build it as an **executable skill**, keep the plain runbook beside it as the source, and keep failed attempts with outcomes per Brian's principle (a past success is not a present procedure). Do NOT park procedures in memory surfaces. **Would deploy. Medium confidence.**
3. **Avoid:** stuffing procedures or area-specific rules into always-loaded memory (context tax every session); relying on auto memory as the record (unversioned, machine-local, silently capped); expecting memory to *enforce* anything — both memory systems are context, not configuration; enforcement is hooks. **High confidence** (docs-explicit).

What I would not infer: installed load order, skill-trigger reliability, or auto-memory write quality on Brian's box — none of that is observable from docs.
