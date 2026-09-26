# System card: STALE (implicit invalidation) + CUPMem (write-side adjudication)

**kiln · 2026-09-26 · source: paper v1 full methods 2605.06527 (sole edition, 7 May 2026; §§1–5 + App. F). Benchmark + prototype; no install/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs, principles, COVERAGE as context.**

## One item traced end to end

Old belief (cycling commute, from gear request) → changed evidence (broken leg, *no negation of cycling*) → candidate retrieval (RAG surfaces both; LightMem data: new evidence retrieved 68–78% yet old ranked top-1 up to 88%) → invalidation in CUPMem: LLM adjudicator marks each old slot KEEP/STALE/REPLACE/UNKNOWN, propagation search extends beyond touched slots (relocation→commute, injury→routine), readout grounded only in authorized active memories → later commute plan respects the injury. The paper's load-bearing finding: retrieval visibility ≠ authority (99.0% PR failure despite 77.5% retrieval).

## Benchmark vs facility, missing host ops

STALE is a benchmark (400 scenarios, 3 probes: State Resolution, Premise Resistance, Implicit Policy Adaptation; best 55.2%). CUPMem is a research prototype: fixed two-level state schema Ω (authored, not learned), per-write LLM adjudicator calls, bounded propagation search, constrained readout. Missing for any host: schema authorship/maintenance, adjudicator cost + fallibility accounting, propagation topology source, readout plumbing into prompts, and — crucially — the Type II dependency graph Brian's domains don't come with. No repo/install path inspected; treat as design evidence only.

## Fit: the adjudication pattern ports, the schema doesn't

Write-side KEEP/STALE/REPLACE/UNKNOWN + unknown-current blocking + premise-blocking at readout: portable as agent discipline on versioned files at ~zero cost. The fixed schema and per-write LLM calls do not port without the missing ops above. Implicit conflicts (no-negation invalidation) are exactly the shape our substring-scope and stale-preference failures take — this paper names our disease family precisely.
