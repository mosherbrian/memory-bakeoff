# Muse ideation batch 11 — third-party metadata verification at scale

**Tag:** `batch11` · **Prompt sha256:** `84572c9e5da572c68e27c4a9ce0affca634a187aece7c6b9938968da2599f500` (`PROMPT11.txt`, recorded before send) · **Date:** 2026-09-15
**Authorization:** standing Muse cadence (Corvid thread, `RD-THREADS.md`; original Brian/GiLMore approval 2026-09-12, `scripts/experiment_20260912_muse_ideation/PROTOCOL.md`).
**Fitted cause:** today's card sweep found a cluster of **metadata defects** —
CSTM paper license wrong, MemoryArena data license unsupported, LME-V2 code
license stale, a missing artifact claim, and repeated abstract-vs-body label
blurring. This batch is about catching that class at scale.
**Content policy:** public methodology only; no project detail, paths, or results.

## Prompt (verbatim, preregistered)

See `PROMPT11.txt`: four public questions — (1) where metadata errors cluster
across papers/code/datasets and how to catch them without full reads; (2)
declared-vs-host-exposed license disagreement; (3) keeping abstract/body/artifact
evidence levels from blurring; (4) the minimal citable/re-checkable metadata record.

## Receipt

One tagged call, `ready=true`, `end_seen=true`, latency 29.3 s, 6,058 assistant
chars, no block signals. Meter `spent $0.0286` before and after; `openrouter
$0.00 today` — cost ≈ $0.00. Receipts:
`scripts/experiment_20260912_muse_ideation/receipts/batch11-*`.

## Dispositions (Muse proposes, Corvid disposes)

1. **Header-plus-link triage** — for every artifact record 5 fields without a
   full read (title/year/venue; persistent id must resolve; landing + direct
   artifact URLs return 200; declared version), and sample ~10% of passes for a
   header check. — **ACCEPT** `[I]`. This is exactly the shape of today's checks
   (abs pin, repo/dataset API, license file) and can be a reusable checklist.
2. **Two-column license capture** — `License-D` (declared: verbatim + location)
   vs `License-H` (host-exposed: API field / cardData / LICENSE file + fetch
   date); pass only if they match after SPDX normalization, or flag
   `D≠H — use the more restrictive`. — **ACCEPT** `[I]`. Directly fits today's
   defects: CSTM declared wrong, MemoryArena host exposes nothing, GateMem/EgoLife
   have the license only in `cardData` while the top-level field is null, LME-V2
   code stale.
3. **Tier-tag every claim with a locator** — `[A:p.N]` abstract, `[B:p.N/Table
   N/§N]` body, `[Art:commit/run/dataset]` artifact; a summary sentence without a
   tag+locator is rejected, and an `[A]` tag may not support a performance claim.
   — **ACCEPT** `[I]`. This is the mechanism behind the repeated
   abstract-vs-body findings (HaluMem numbers, EvoMemBench counts, StateMemBench
   0.277, Compaction Cliff 50%/50 vs 20/53).
4. **Nine-field citable record** — merges 1+2 and adds PID, version+date-accessed,
   access status, and verifier+date+outcome; citable iff the PID resolves, both
   URLs are 200/gated-marked, version+date present, D and H present, and ≥1 claim
   locator. — **ACCEPT** `[I]`, merged with 1+2.

**Net:** 4 ACCEPT / 0 DUPLICATE (item 4 merges 1+2). No ACCEPT is a finding until
a probe runs; the natural first probe is the two-column license census over the
existing card corpus, which today's manual checks suggest would reproduce the
defects already found. Second seat open (Alice/Assay).
