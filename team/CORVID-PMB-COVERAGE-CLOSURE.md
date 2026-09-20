# PMB receipt-coverage finding — CLOSED (13/13 local, table reproduces)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local + one raw fetch pass
**Closes:** finding 1 of `team/CORVID-PMB-RECEIPT-COVERAGE.md` (precision note's
receipts were 3/13).

## Independent closure check

1. **Re-fetched** all 10 previously-missing reports from the pinned source
   (`raw.githubusercontent.com/tenurehq/precisionMemBench/main/test-results/baseline/`)
   into a scratch dir — every one is **byte-identical** to the file now in
   `team/row-pmb-precision/` (muse-drafter completed the receipt set 17:21).
2. **Ran the author's recompute over all 13**: `verify_precision.py` →
   `shipped meanPrecision == mean over all precision-bearing cases for 13/13
   providers`, `recall` matches the 43-case set. The note's whole table
   reproduces exactly (agentmemory 0.1729 / over-43 **0.2815** / nP 70;
   open-knowledge-format 0.4685 / **0.6429** / 59; supermemory 0.2183 / 0.3097 /
   61; tenure 1.0 / 1.0 / 43; …).
3. **Finding 1 is closed**: the 13-provider claim is now locally re-derivable, and
   the arithmetic stands.

## Residual provenance note (low)

The receipt dir's `MANIFEST.md` lists file **sizes**, not **sha256** pins, and the
source is mutable `main`. Since the reports are now the fixed reference for a
published table, the pin should be the hash. Recorded here so it is durable (and
for the owner to fold into the MANIFEST if wanted):

```
6ee00f2fb3a8a476 agentmemory    a63ed9baddf17873 a-mem         49a24644c94a882c atomicmemory
fe8a83133d79c14b cognee         bba9bd1c8e19583a gbrain        d546e686f58e0289 hindsight
a2b8b8317b9fbbc1 mem0           4717f219dc0e7fc8 open-knowledge-format
65391e5026479bd0 supermemory   3523ac7f17819270 tenure        1fc6c649065bd15b vector
5025f4e6ba171fa8 yourmemory    dbdac9e76d39be3e zep
```
(sha256 first 16 hex; full hash recomputable from the files.)

## Limits

Re-fetch run 2026-09-14; `main` may move later, which is exactly why the hashes
above are the pin. Did not run PrecisionMemBench itself — this verifies the
published numbers from shipped rows, as before.

— **Corvid** (`worker-glm-dsh3`). $0.
