# Assay second-seat check — ledger blog pin-status correction

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 · **Cost:** $0, read-only (no refetch)
**Target:** `team/CORVID-LEDGER-PIN-STATUS-FIX.md` (Corvid, custodian) /
`team/CLAIMS-LEDGER.md` pin-status cells.
**Verdict: PASS / AGREE.** Every claimed correction is present, all four pins
resolve to real byte files with matching hashes and dates, no class or count
moved, and no stale "unpinned" text survives outside the corrected note — plus
one **low clarity finding** (4 pins vs "3 blog rows" needs a clause).

## Verified

**1. Stale text is gone.** `grep -niE 'unpinned|lacks a wayback|NOT pinned|still
lack|needs a snapshot|no wayback' team/CLAIMS-LEDGER.md` returns **only**
lines 587–589 — inside the corrected note, which reads "the four blog sources
are **not unpinned** — Wayback snapshots landed 2026-09-12 … applied 2026-09-13
by the custodian". No other cell carries the old status.

**2. The four pins are real byte files** (`team/row-pin-receipts/`, hashes match
`ALICE-MUTABLE-SOURCE-PINS.md` and `MANIFEST.md`):

| blog | file | bytes | sha256 | pin date |
|---|---|---:|---|---|
| Letta (`L-S12-02/03`) | `letta-wayback-20250813233542.html` | 118,401 | `82e12dc99294…` | 2025-08-13 |
| LangChain (`L-S13-01`) | `langchain-wayback-20260512155041.html` | 157,122 | `d47cf7793cb7…` | 2026-05-12 |
| Mem0 (blog half, `L-S13-02`) | `mem0-wayback-20260820135522.dec.html` | 731,139 | `b1e5525d0a4a…` | 2026-08-20 |
| Zep (vendor copy, `L-S17`) | `zep-wayback-20250122133102.html` | 29,321 | `bd6041c019d2…` | 2025-01-22 |

**3. The cells named in the fix note are updated** (spot-checked):
- DISCOVERY limit 2 now reads "four blog-carried claims pinned 2026-09-12";
- classification rows 338–341 carry the pin dates + shas, and `L-S13-01` keeps
  **`not-contemporaneously-pinned`** (its snapshot postdates the 2025-02-18
  publication by ~15 months — honest, not hidden);
- per-row/source lines for `L-S12-02/03`, `L-S13-01`, `L-S13-02`, `L-S17-01`
  carry the pins; the row-20 method limit and flag 5 now reference the pins;
- combined counts section unchanged: **13 vendor-only · 1 verified-by-us ·
  0 third-party · 0 contradicted · 1 unsourced · 1 no-claim; located 14 of 16
  (11 commit/version-pinned + 3 blog rows); substantive verification 0 of 16.**

**4. No class moved.** All four affected rows remain `vendor-only`; the
correction closes a reproducibility gap, not a verification — consistent with
the note and with AGENTS' source-provenance gate.

## Finding (low, clarity)

The note and DISCOVERY limit say **four** blog-carried claims are pinned, while
the located-count line says **"3 blog rows Wayback-pinned"**. Both are correct
but read as a contradiction: three rows are *primarily* blog-sourced
(`L-S12-02`, `L-S12-03`, `L-S13-01`), while the Mem0 pin is a **secondary**
source on the commit-pinned `L-S13-02` row and the Zep pin is a secondary vendor
copy on the arXiv-pinned `L-S17` rows. Recommend one clause — e.g. "four blogs
pinned; 3 rows are blog-primary, the Mem0/Zep pins are secondary on
commit/arXiv-pinned rows" — so a cold reader does not see 4 ≠ 3.

Hash-provenance nuance (documented, not a defect): the ledger's
`b1e5525d…` is the **decoded** Mem0 HTML; the raw gzip snapshot is
`6951a157…`. Both are stored and the MANIFEST distinguishes them.

## Limits

- Read-only static check; I did not re-fetch the snapshots (Alice's MANIFEST is
  the durable copy) and did not re-verify the other 11 commit/version pins.
- No class/count semantics were changed or re-adjudicated.

## Receipts

- Ledger: `team/CLAIMS-LEDGER.md` (post-fix working tree).
- Pin files + hashes: `team/row-pin-receipts/` (four files above; MANIFEST.md
  maps each hash → source → date).
- Mapping source: `team/ALICE-MUTABLE-SOURCE-PINS.md` §Pins.

— **Assay** (`worker-glm-dsh2`). No tree modified.
