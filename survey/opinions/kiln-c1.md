# kiln (Practitioner) — cycle 1 opinion: What practitioners get wrong about agent memory

**kiln · 2026-09-26 · Explore, docs only, no installs/experiments. Quoting survey/ROLES.md: "What practitioners get wrong about agent memory".**

## The mistake

Practitioners buy retrieval and celebrate "the agent retrieved it", while the failures that cost Brian are elsewhere: stale state treated as fact, no handoff saying what to recheck, and memory lifecycle (admission/revision/forgetting) silently doing the wrong thing. Tern's memo already makes this point (Overrated: R53 relevant-note reads with no outcome advantage; R61 formatting dominating the endpoint) — I endorse it. **Medium confidence**, source: memo §§5–6 + cited R53/R61 acceptances (read via memo, not re-verified this cycle).

## What I'd do instead (builder's view)

1. Ship the boring layer first: scoped notes with source + date on Claude Code native surfaces; files + lexical search on Pi/local. **Would deploy. Medium confidence.** (Docs: https://code.claude.com/docs/en/memory ; bake-off lexical findings via memo §3.)
2. Ship handoffs, not archives, for ongoing work: current state, what was last observed, what to recheck, pointer to evidence. **Would deploy. Medium confidence** (inference from harness guidance + our state-update failures, both via memo §2).
3. Treat procedures (checklists/skills) as separate from facts; don't stuff runbooks into a vector store. **Would watch. Low–medium confidence** (memo §4 direction).
4. Defer a memory service until a named miss (paraphrase, temporal, shared access) justifies the ops cost. **Would watch/skip for now. Low confidence** in any product pick (Zep paper via memo; lifecycle risk from our bake-off).

All four are documentation + prior-readout based; explicitly **no hands-on experience claimed** this cycle, and I ran no probe per the 15-minute docs-only commission.

## The one recommendation this changes

Add Tern memo's "Overrated" measurement caution as the default bar for anything beyond scoped notes + handoff: it should move fewer repeated corrections, successful constrained actions, stale-state mistakes, or handoff recovery — not retrieval hit-rate. Tern accepts the relevance but rejects a universal deploy gate ( proportional, reversible exploration remains allowed) — accepted; the bar above is a default expectation, not a block on small reversible probes.

*Amendment 2026-09-26: corrected two card errors — repo CLAUDE.md (versioned) vs auto-memory under the user project-memory directory (not versioned); hosted vs self-hosted service obligations. No new probe.*

## Disagreement with Tern

None sharp this cycle; risk I may be underweighting: automatic episodic capture (corvid's brief) could recover value nobody curates. I keep Tern's deliberate-notes-first bet but flag it as the dissent to watch.
