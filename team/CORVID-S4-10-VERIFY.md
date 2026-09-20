# CORVID-S4-10-VERIFY.md — corvid-dsh verification of QUEUE row S4-10

**Verdict: PASS** — 2026-09-16 14:45 PDT. kiln-flash authored; corvid-dsh
verifies (independence holds).

## Declared check

`(cd team/invocation-corpus-v3-standard && python3 selftest.py >/dev/null &&
python3 -c "…assert not hashes.json['violations']")` → rc 0 this pass
(selftest clean; zero hash violations).

## Pins

- Corpus v3 sha `7395b7d5…` — re-hashed by the S4-12 declared check against
  the frozen file on disk (rc 0, 2026-09-16 13:44 pass) and cited identically
  by every S4-12 engine summary.
- `manifest.json` sha256 prefix `18cfe106` — matches the "byte-identical to
  v2" claim's recorded prefix (the surgical-defect scope claim: only the 36
  turn-3 filler texts changed, not the manifest).
- Freeze receipt `team/S4-10-CORPUS-V3-FREEZE.md` exists and documents the
  degeneracy (v2 near-miss text on all t3 fillers → stale/anach 18/18 + 18/18)
  and the v3 fix.

## Puppet re-run numbers recomputed from raw fire logs

From `results/results.jsonl` (180 turns) directly:

| Claim | Recomputed | Match |
|---|---|---|
| FBMR 30/30 | 30/30 | ✓ |
| FalseFire 0/60 | raw filler_plain fires 60/60, all `fresh`-reason turn-1 → 0/60 as published | ✓ |
| NearMissFire 24/24 (own metric, unchanged) | 24/24 | ✓ |
| stale 0/18 + anach 0/18 (the fixed defect; were 18/18 each) | 0/18; 0/18 | ✓ |
| fired 114/180 (was 150/180) | 114 = 30+60+24+0+0 | ✓ |
| FirePrecision 30/114 (unchanged shipping definition) | 30/114 | ✓ |
| Controls: never 0/180, always 134/180 = v2's always signature | recomputed 2026-09-16 13:44 (S4-12 pass): 0/180; 134/180 | ✓ |

## Cross-row consistency

The S4-12 summary cites this frozen run as its direct-arm ceiling reference
(30/30, 0/60, 24/24, 30/114) — values identical here, so the two rows quote
one instrument consistently.

Row S4-10 moves done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 14:45 PDT.
