# LongMemEval qualifier census — our own docs still cite an unqualified score

**Author:** Corvid (`worker-glm-dsh3`), R&D pulse 2026-09-12
**Instrument:** `implementer/repo-glm-dsh3/scripts/check_longmemeval_qualifiers.py`
(self-test PASS; output `scripts/check_longmemeval_qualifiers-output.txt`)
**Scope:** team/*.md + `implementer/repo-glm-dsh3` docs; raw vendor-fetch dirs
excluded. **Cost:** $0, read-only.

**Plain English (for Brian):** Three different benchmarks all get called
"LongMemEval" — our oracle split, the S-variant retrieval haystack, and the
judged QA pipeline. I built a small check that flags any line pairing
"LongMemEval" with a score but naming no split. It found that after the audit,
**five lines of our own prose still cite a vendor LongMemEval score without
saying which one** — the exact ambiguity the audit exists to prevent.

## Genuine hits and the recommended qualifier

| File:line | Short text | What the number actually is | Fix |
|---|---|---|---|
| `CLAIMS-LEDGER.md:175` (L-S17-02) | "LongMemEval: up to +18.5% accuracy" | Zep paper's LongMemEval; split unspecified | add `(split unspecified; competitor table lists Zep LongMemEval-S 71.2 under the official judge)` |
| `ECOSYSTEM-MAP.md:221` | "README LoCoMo 88.83 / LongMemEval 89.20" | MemOS's own OmniMemEval framework; split unspecified | add `(split framework unspecified)` |
| `ECOSYSTEM-MAP.md:222` | "LongMemEval up to +18.5% accuracy" | same as L-S17-02 | same qualifier |
| `RESEARCH-PROVENANCE-AUDIT.md:68` | "LongMemEval R@5 95.2%" | **LongMemEval-S** retrieval (`recall_any@K`) | rename to `LongMemEval-S` |
| `RESEARCH-4-ENGINES-SURVEY.md:83` | "LongMemEval-class result (agentmemory 95.2%, MemBukkit 92.6%…)" | both are LongMemEval-S, different metrics | say `LongMemEval-S` and keep the metric distinction |

Zep-related re-derivations (`ALICE-REDERIVE-ZEP-HEADLINE.md:22-23`) also carry
the split-unspecified number; they are Alice's artifacts, flagged for her, not
edited here.

## Instrument caveat (so it is not over-trusted)

The guard also flags:
- `LongMemEval-class` summary prose and lines where an unrelated number sits
  near the word (`CHIP-rnd.md:22`, `RD-THREADS.md:214`, `SCOREBOARD:295`,
  `ACCOUNTING_glm-5.3.md:90`);
- the ledger's own collision register (`ALICE-LEDGER-COLLISION-REGISTER.md:51,53`),
  whose whole point is to disambiguate the splits.

So its exit code is a **prompt to read**, not a verdict: 13 raw hits, 5 genuine
unqualified-score lines. The false-positive classes are named in the script's
docstring and here so the check does not decay into noise-blindness.

## What would close it

Add a split qualifier to the five lines above. That is a one-line edit each, in
three owners' files (ledger = Corvid, map = Stratum, provenance audit = Corvid);
no number changes, only the label. The guard then exits 0 for the genuine class.

— **Corvid**. The audit told us the split matters; this is the receipt that our
own summaries had not fully absorbed it.

## Status — fixes applied 2026-09-12 ~18:45

- **Fixed by Corvid:** `CLAIMS-LEDGER.md` L-S16-02 summary + per-row detail
  (`split unspecified`) and L-S17-02 (`split unspecified; competitor table…`);
  `RESEARCH-PROVENANCE-AUDIT.md:68` (`LongMemEval-S`);
  `RESEARCH-4-ENGINES-SURVEY.md:83` (both numbers `LongMemEval-S`).
- **Fixed independently by Stratum:** `ECOSYSTEM-MAP.md` 225-226
  (`split unspecified`; map change log line 209, 18:42).
- **Genuine residual:** `ALICE-REDERIVE-ZEP-HEADLINE.md:22-23` (Alice's
  artifact; the Zep-paper LongMemEval split is unspecified).
- **Guard self-correction:** the first pass missed `L-S16-02` because
  `PersonaMem v2` satisfied a too-broad `v2` qualifier. The guard now requires
  a qualifier adjacent to LongMemEval and accepts `(split unspecified)` as a
  documented disclaimer.
- **After the fixes:** 9 residual guard hits; only 2 are genuine (Alice's). The
  rest are the named false-positive classes plus this note quoting the defects.
