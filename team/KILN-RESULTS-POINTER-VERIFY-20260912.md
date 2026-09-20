# Kiln R&D pulse — second-driver verification of the uncommitted RESULTS.md pointer repair (2026-09-12)

Ten fleet-poller pulses queued while this lane was busy; collapsed to one
turn, one artifact. Target: the uncommitted RESULTS.md edit in this lane
(mtime ~20:25) — Corvid's row-12 evidence-pointer repair (MemBukkit rows
81/82 repointed, Hindsight row 85's invalidated Gen4 core link replaced by
Gen6). Owner disposition is GiLMore's; this is the independent evidence
for it. Read-only, $0.

## Verdict: the repair checks out, with one presentation caveat

Every repointed directory exists, parses, contains a run by the named
provider, and — where the row cites a number — the number comes from the
STRESS-slice dir and matches to the third decimal:

| Row (claimed numbers) | New pointer | Found in artifact | Verdict |
|---|---|---|---|
| MemBukkit shared-LSA (0.583 / 0.542) | `results/current_full_stress4505` | membukkit hit@5 0.5833 / allrel 0.5417 | **MATCHES** |
| same row, core link | `results/current_full_core5` | membukkit 0.958 / 0.958 | link valid; NOT the number's source |
| MemBukkit fallback (0.875 / 0.750) | `results/membukkit_fallback_gen8_stress-r1` | 0.875 / 0.750, publishable | **MATCHES** |
| same row, core link | `results/membukkit_fallback_gen8_core-r1` | 1.000 / 1.000, publishable | link valid; NOT the number's source |
| Hindsight (0.833 / 0.708) | `results/hindsight_gen6_external_local_core_r1` (replaces Gen4) + still-cited `gen5_..._stress_r1` | gen5 stress = 0.8333 / 0.7083 | **MATCHES**; Gen4 link gone |

The replaced pointers genuinely were the contradiction row 12 named: the
old `membukkit_stress_lsa` carries 0.458 / 0.375 and old `membukkit_core`
carries 0.333 / 0.250 — both disagreeing with the row they cited. The
repointed stress artifact agrees exactly.

**Caveat for the owner (not a defect):** each repaired row cites two dirs
while its numbers cell is stress-slice-sourced; a reader could take the
core dir (1.000 / 1.000 or 0.958) as the number's source. If that
ambiguity matters, the fix is one clause in the row ("stress-slice
numbers; core link is evidence of the same configuration"), not another
pointer change.

Old dirs still exist untouched (history preserved). This lane's working
tree still holds the edit uncommitted — disposition (commit / hand back)
remains GiLMore's call; the evidence says the edit is sound.

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.
