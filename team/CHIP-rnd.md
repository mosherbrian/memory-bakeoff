# CHIP — R&D ideas & outputs index (2026-09-12 ~17:30)

**Standing locations:** ideation = `team/MUSE-IDEATION-*.md` · research notes =
`team/RESEARCH-*.md` · synthesis pair = `CLAIMS-LEDGER.md` (facts) +
`ECOSYSTEM-MAP.md` (meaning) · probe code = `scripts/experiment_*/`.

## The ideas (Muse batches, adversarially disposed)

| File | What | Outcome |
|---|---|---|
| `team/MUSE-IDEATION-01.md` | 9 Muse proposals, Corvid-disposed | 3 ACCEPT (cache-leakage probe, cost-reservation at claim, stale-exposure metric) · 5 duplicate · 1 reject |
| batch 2 (PROMPT2.txt) | 5 proposals on R&D threads | 2 ACCEPT · 3 duplicate · 0 reject (~$0.0011) |

**The 5 accepted ideas:** run-integrity cache-leakage probe (done, PASS) ·
metering cost-reservation at claim time (upgrades LANE-COUNTER-DESIGN) ·
frequency-weighted stale-exposure metric · + 2 more in the file.

## The research (verified findings)

| File | Finding |
|---|---|
| `RESEARCH-4-ENGINES-SURVEY.md` | 4 local engines: licenses verified at frozen commits; all advertise LongMemEval-class results, none verified here; MemBukkit's 32.9% retracted and stays retracted |
| `RESEARCH-Q1.2-ISOLATION-PREREG/RESULT.md` | cache-leakage isolation probe: PASS, power-confirmed — the harness cannot silently carry results between runs |
| `SECOND-DRIVER-REPORT.md` (repo-glm-dsh2) | independent re-derivation: reproduces frozen core5 exactly, 7/7 providers |

## The synthesis pair (the "meaningful view" you asked for)

- `team/CLAIMS-LEDGER.md` — every public claim classified: 16 sources, 0
  verified-by-us yet, 12 vendor-only, and the copies-between-competitors
  findings (Zep blog = its own paper; Letta cites a number that isn't in
  Mem0's paper).
- `team/ECOSYSTEM-MAP.md` — the taxonomy: 18 systems slotted into approach
  clusters, verified-vs-claimed landscape, three unmeasured gaps, and what it
  implies for our own line (Perseus lineage as a removable module).

**R&D lead:** Corvid · **verification:** Alice/Assay · **cadence:** one
batched Muse call + ledger updates per R&D item.
