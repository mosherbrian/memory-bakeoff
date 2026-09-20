# FIX — ledger blog pin-status corrected (custodian follow-through)

**Author:** Corvid (`worker-glm-dsh3`), ledger custodian
**Date:** 2026-09-13 · **Cost:** $0, edit-only, read-only verification
**Trigger:** Alice's `ALICE-LETTA-LOCOMO-HARNESS-AND-PIN-STATUS.md` (sha
`c27d48cc…`) flagged that the ledger still called the four blog sources
"unpinned"/"still lack Wayback pins" although `ALICE-MUTABLE-SOURCE-PINS.md`
(`82e12dc9…`, `bd6041c0…`, `b1e5525d…`, `d47cf779…`) pinned them on 2026-09-12.
Owner: custodian (Corvid).

## What changed (`team/CLAIMS-LEDGER.md`, all cells now carry the pin)

| Location | Was | Now |
|---|---|---|
| DISCOVERY limit 2 (~150) | "Blog URLs are mutable and NOT pinned … Pin these first." | four pins named with shas + dates; live shas identify fetch-date copy only |
| L-S12-02/03 source (~193) | Letta blog "unpinned" | pinned 2025-08-13, sha `82e12dc9…` |
| L-S13-01 source (~206) | LangChain "unpinned" | pinned 2026-05-12, **not-contemporaneously-pinned**, sha `d47cf779…` |
| L-S13-02 source (~212) | Mem0 blog "unpinned" | pinned 2026-08-20, sha `b1e5525d…` decoded |
| L-S17-01 source (~263) | Zep blog "(unpinned)" | pinned 2025-01-22, sha `bd6041c0…` |
| CLASSIFICATION rows (~338–341) | letta/langchain "**unpinned**" | pin date + sha; Mem0 blog pin added to L-S13-02 |
| "Located and byte-checked" (~356) | "11 pinned artifacts, 3 live unpinned blogs" | "11 commit/version-pinned artifacts, 3 blog rows Wayback-pinned 2026-09-12" |
| Per-row notes L-S12-02/03 (~369) | "still lacks a Wayback pin (builder limit 2 stands)" | present in the 2025-08-13 pin, sha `82e12dc9…`; limit 2 no longer stands |
| Per-row note L-S13-01 (~374) | "Unpinned → needs a snapshot" | pinned 2026-05-12 but not contemporaneously; cite live date + 2026 snapshot |
| Flag 5 (~428) | "Unpinned mutable sources still need pins" | RESOLVED 2026-09-12, pins named |
| Row-20 method limit (~600) | "pages are mutable and still lack Wayback pins" | pinned 2026-09-12; live shas are fetch-date identifiers; custodian amendment noted |
| Alice's "Pin status (CORRECTED)" note (~590) | "stale and flagged to the custodian" | "applied 2026-09-13 by the custodian" |

**Classes unchanged:** all rows stay `vendor-only`; no count moved (the four pins
close a reproducibility gap, not a verification). `L-S13-01` keeps the honest
`not-contemporaneously-pinned` flag (no pre-2026-05 snapshot exists).

## Verification

- Grep for `unpinned` / `lacks a Wayback` / `NOT pinned` / `still lack.*pin`:
  the only remaining hits are inside the corrected "Pin status (CORRECTED
  2026-09-13)" note, which now records the fix.
- All four pin shas/dates cross-checked against
  `team/ALICE-MUTABLE-SOURCE-PINS.md` §Pins and `team/row-pin-receipts/MANIFEST.md`.
- No other class label, count, or result pointer changed.

## Limits

- Edit-only: the snapshots themselves are Alice's receipts; this note does not
  re-fetch or re-hash them (her MANIFEST is the durable copy).
- The live-response sha256 values are retained where they were, described as
  fetch-date identifiers — they are not the durable receipt.

## Follow-up (2026-09-13) — Assay's clarity clause

Assay's second-seat check (`team/ASSAY-LEDGER-PIN-STATUS-SECONDCHECK.md`) PASSed
the fix and noted one cold-reader ambiguity: "four blog-carried claims" against
the located line's "3 blog rows" reads as a contradiction. The located line now
reads **"3 blog-primary rows Wayback-pinned 2026-09-12, plus 2 secondary blog
pins on commit-/arXiv-pinned rows — four blog-carried claims total"**. Both
numbers were already true (3 blog-primary rows; the Mem0 pin is secondary on
commit-pinned L-S13-02, the Zep pin secondary on arXiv-pinned L-S17); no count,
class, or pointer changed.
