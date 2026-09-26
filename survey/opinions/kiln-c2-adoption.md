# kiln (Practitioner) — c2 adoption recommendation

**kiln · 2026-09-26 · recommendation only, nothing deployed. No installs/probes. Quoting ROLES.md: "judge real systems as a builder would: install cost, failure modes, maintenance, fit for Brian's stack".**

## The arrangement (four lanes, four jobs)

1. **Mandatory instruction** — the tiny set that must hold every session (repo `CLAUDE.md`, <200-line target, plus `~/.claude/CLAUDE.md` for personal defaults). Use for: build/test commands, never-push-to-main class rules. Not for procedures, not for preferences with expiry dates. Maintenance: prune on every contradiction; conflicting entries resolve arbitrarily, so fewer entries beat better entries.
2. **Plain textual skill** — the default home for each recurring procedure (model-test, rollout): steps in words, versioned beside the code it operates on, failed attempts kept with outcomes. Zero tooling cost, reviewable in a minute. This is what reduces re-learning first.
3. **Executable helper** — promoted from a textual skill only after it has succeeded repeatedly by hand: a script the skill invokes (runner, checker), with its own failure output. Never assume a skill executes code — most should stay textual. Promotion criterion: the same textual steps worked ≥3 times unchanged and the failure mode is machine-checkable.
4. **Auto-memory** — capture net only: leave it on, audit via `/memory`, treat unreviewed entries as untrusted. Never the record, never enforcement.

## Why this shape

Per Brian's ordering it attacks cost #1 (procedures) with the cheapest durable form and cost #2 (preferences) with scoped notes, while adding no audit job: the only recurring maintenance is pruning CLAUDE.md contradictions and promoting skills that earned it — both one-minute reviews, not a measurement program. pi-lcm keeps its compaction role untouched; its store is not part of this arrangement.

**Medium confidence** — assembled from current official docs, the primary-notes reading, and cycle-1/2 opinions; no hands-on deployment claimed.
