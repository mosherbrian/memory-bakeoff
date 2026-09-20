# Ledger consistency audit — the two `unsourced` rows (second-driver provenance re-run)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 09:45 UTC · **Cost:** $0, local re-read of frozen raw bytes, one turn.
**Trigger:** my standing thread — "12 vendor-only claims: provenance chase each
to first appearance; CLAIMS-LEDGER: retire duplicates, flag contradicted pairs".
No tree modified; ledger edits are proposed, not applied (custodian: Corvid).

## Verdict

The two rows the ledger calls `unsourced` are **not in the same state**:

- **L-S16-03 (MemOS +159% / +38.97% / −60.95%): consistently `unsourced`, and
  I re-confirmed it. No action.**
- **L-S14-02 (A-MEM six-fold / 85–93%): traced on 2026-09-12, but the ledger
  still carries `unsourced` in five reader-facing places and a stale count.**
  The builder update explicitly left the class "Corvid's and Alice's to set";
  Alice's collision register proposed `vendor-only (narrowed)`; it was never
  written into the ledger. **This is a self-contradiction, not a missing trace.**

## Independent reproduction (raw bytes, not the notes)

Re-hashed all 14 frozen fetches in `team/builder-provenance-fetches/` against
`MANIFEST.md`: **14/14 sha256 + size match**. Then re-extracted the PDFs with
`pdftotext -layout`:

**L-S14-02 — located in `2502.12110v1` body (verbatim):**
> "The Multi-Hop category showcases particularly striking results, where
> Qwen2.5-15b with A-MEM achieves a ROUGE-L score of 27.23, dramatically
> surpassing LoComo's 4.68 and ReadAgent's 2.81 - **representing a nearly
> six-fold improvement**." (v1 text lines 1124–1126)

> "Our approach requires only **1,200-2,500 tokens**, compared to the
> substantial **16,900 tokens** needed by LoComo …" (v1 text line 1134)

So the "six-fold" is real but **narrow** (one model, one category, a
lexical-overlap metric). The "85–93%" is **not stated** by the paper:
1−2500/16900 = 85.2%, 1−1200/16900 = 92.9% — an aggregator's arithmetic.
Residual: only **v1** was re-read; the ledger's L-S14-01 pins **v11**, and
"v11 body not checked" still stands (builder's own caveat).

**L-S16-03 — still not in any paper, first appearance confirmed:**
`159% | 38.97 | 60.95` occurs **0 times** in each of `2507.03724` v1–v4 and
`2505.22101v1`, and **0 times** in the fetched VentureBeat HTML. It occurs **6
times** in `hf-papers-2507.03724.html`, inside a **comment** by `UglyToilet`
(fullname "hanyu Wang") posted `2025-07-08T03:16:43.528Z`; the same name is an
`admin_assigned` author on that paper page. Author-side post, not paper text —
the builder's reading reproduced exactly.

## Contradiction map (`team/CLAIMS-LEDGER.md`)

| line | current | problem | proposed |
|---|---|---|---|
| 167 | `vendor-only (unsourced)` | self-contradictory cell | `vendor-only (narrowed; 85–93% derived-not-stated)` |
| 218 | `**unsourced**` | contradicts the row it heads | `**vendor-only (narrowed)**` |
| 220 | "only aggregator pages … primary text is not located" | false since 2026-09-12 | cite `2502.12110v1` body + sha `5d94b7aa…` |
| 221 | "do not cite this until it is traced" | condition met | narrowed rule: cite the six-fold only as multi-hop/ROUGE-L/one model; never cite 85–93% as vendor-stated |
| 339 | `**\`unsourced\`**` / "no primary located" | false | `vendor-only (narrowed)`, receipt `2502.12110v1` body |
| 351 | counts "12 vendor-only … 2 `unsourced`" | stale by one | `13 vendor-only … 1 unsourced` |
| 352–353 | "Located … 13 of 16 … other 3 are the two unsourced rows and the no-claim row" | stale | `14 of 16`; "other 2 are the one unsourced row and the no-claim row" |
| 432 | action "Trace to a paper version or drop — they are `unsourced` today" | L-S14-02 done | keep only L-S16-03 (or mark L-S14-02 done) |

Consistent and untouched: line 623 (builder update), line 628/845
(L-S16-03 stays `unsourced`).

## Handoff

**Proposed, not applied** — these are rows in the `CLASSIFICATION` /
`DISCOVERY` sections, not my P1 section, and the ledger is Corvid's to merge.
The minimal fix is the eight cells above; the strongest argument for doing it is
that a cold reader at line 167 or 339 currently sees "unsourced" for a claim the
ledger itself says (line 623) was traced.

**Suggested disposition:** L-S14-02 → `vendor-only (narrowed)`, with
`derived-not-stated` attached to the 85–93% token figure; L-S16-03 stays
`unsourced` with the HF-comment first appearance recorded (it already is).
This matches Alice's collision-register amended count (13 / 1 / 0 / 0 / 1 / 1).

## Limits

- Frozen-bytes re-read only — no re-fetch, no network; the v11 body remains
  unchecked and the class does not depend on it (the claim is vendor-only
  either way).
- I did not edit the ledger; no other ledger row was audited in this pass.
