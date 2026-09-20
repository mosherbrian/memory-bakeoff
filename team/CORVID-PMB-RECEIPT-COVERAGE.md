# PrecisionMemBench re-derivations — second-driver + receipt-coverage check

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, shipped artifacts only (no web, no harness)
**Subject:** `team/SPARK-PMB-PRECISION-DENOMINATOR-20260914.md` and
`team/SPARK-PMB-SESSION-REDERIVE-20260914.md` (muse-drafter), receipts
`team/row-pmb-precision/` and `team/row-pmb-session/`.

## Independent re-derivation (not a re-read)

Did not just re-run the author's scripts. Recomputed agentmemory from
`retrieval-report-agentmemory.json` directly:

```
cases 77 · nP 70 · nR 43 · nP-with-recall 43 · precision-null 7
shipped meanPrecision 0.1729
mean over all 70 precision-bearing  0.172891  ← == shipped
mean over the 43 recall-bearing      0.281451  ← the README's stated active set
mean recall over the 43              0.970653
```

So the denominator finding is **confirmed independently**: the shipped
`meanPrecision` is the all-precision mean, not the stated 43-active-case mean.
The equality is a property of the data, not an artifact of the author's script.

Then ran both shipped recomputation scripts read-only:
`verify_precision.py` → **3/3 local reports match** (agentmemory 0.1729/0.2815,
mem0 0.0558/0.0896, tenure 1.0/1.0, nP 70/69/43);
`verify_session.py` → **13/13 session rows reproduce** (incl. nearest-rank p50/p95).

## Findings

1. **Receipt-coverage gap in the precision note (session note is clean).**
   **[CLOSED 2026-09-14 — muse-drafter fetched the 10 reports; re-fetched
   byte-identical and the 13/13 table reproduces; see
   `team/CORVID-PMB-COVERAGE-CLOSURE.md`.]**
   `row-pmb-precision/` preserves only **3 of 13** `retrieval-report-*.json`
   (agentmemory, mem0, tenure). The note tabulates all 13 providers and says the
   check was done "for all 13 providers … 13/13 reports," but the other 10 rows
   (e.g. open-knowledge-format 0.47→0.64, supermemory 0.22→0.31,
   atomicmemory 0.15→0.23) are **not locally re-derivable**. The session note
   ships all 13, so this is specific to the precision note. Fix: fetch the 10
   remaining reports into `row-pmb-precision/` (same MIT source, small), or mark
   the table's 3 verified vs 10 reported-only rows.
2. **The MANIFEST already bounds it.** It says "Reproduce the full 13-provider
   table: download all `retrieval-report-*.json`…", i.e. the sample is a
   deliberate limitation — but the note's table reads as a full recomputation.
   One label closes the gap without new fetches.
3. **The arithmetic stands.** No number changes; both re-derivations reproduce
   on the receipts that are shipped. The only defect is that 10 rows' inputs are
   not shipped with the claim.

## Limits / class

- Did not fetch the 10 missing reports and did not run PrecisionMemBench or any
  provider wrapper.
- Class: `vendor-reported` benchmark, second-driver re-derivation from shipped
  artifacts; the `agentmemory` row stays a third-party vendor-operated signal
  with the stated-active precision **0.28** (published 0.17).

— **Corvid** (`worker-glm-dsh3`). $0, local.
