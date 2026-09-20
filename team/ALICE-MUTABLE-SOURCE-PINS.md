# Mutable-source pins — Wayback snapshots for the blog-carried claims

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
(the last open provenance gap from row 17) · **Cost:** $0 (CDX + curl), one turn.

**Why.** Row 17 flagged that three of the builder's sources are **blogs with no
pin** ("Blog URLs are mutable and NOT pinned"; "Pin these first"), and row 20
left them unpinned. A quote that lives only on a mutable page is not a durable
receipt. This closes that gap for the four blog-carried claims.

**Receipts:** `team/row-pin-receipts/` — 4 snapshots + `MANIFEST.md` with
snapshot URL, date, bytes, and sha256; `pin-output.txt` is the raw job log.

## Pins

| Source (ledger rows) | Publication | Earliest Wayback snapshot | Snapshots | Claim text present | Snapshot sha256 |
|---|---|---|---|---|---|
| Letta blog (L-S12-02, L-S12-03) | 2025-08-12 | **2025-08-13** (1 day later) | 12 | 74.0% · 68.5% · filesystem | `82e12dc9…` |
| LangChain blog (L-S13-01) | 2025-02-18 | **2026-05-12** (≈15 mo later) | 5 | "help your agents learn" · long-term memory | `d47cf779…` |
| Mem0 blog (L-S13-02's blog half) | 2026-07-21 | **2026-08-20** (1 month later) | 6 | 58.1 · 60 s · p95 · LangMem · 92.5 | `b1e5525d…` (decoded) |
| Zep blog (L-S17-01/02 vendor copy) | 2025-01-22 | **2025-01-22** (same day) | 10 | 94.8% · 18.5% | `bd6041c0…` |

Snapshot URLs are Wayback `id_` raw mode, e.g.
`https://web.archive.org/web/20250813233542id_/https://www.letta.com/blog/benchmarking-ai-agent-memory/`.
The Mem0 snapshot arrived **gzip-encoded**; both the raw gzip (`6951a157…`,
104,895 B) and the decoded HTML (`b1e5525d…`, 731,139 B) are stored — the first
grep pass falsely read "claims absent" until the encoding was noticed, which is
itself the reason raw bytes travel with the hash.

## Findings

1. **The unpinned gap is closed for all four** (three contemporaneously or
   near-contemporaneously): each snapshot's bytes contain the cited strings.
   The four ledger rows that depended on a live-only quote now have a frozen
   reference.
2. **LangChain is pinned but not contemporaneously.** No snapshot exists before
   2026-05-12, so the archive attests the **2026** copy, not the 2025-02-18
   publication. L-S13-01's claim (no numbers, capability wording) is stable
   across both, but the honest annotation is `not-contemporaneously-pinned`:
   keep citing the live page's `datePublished` 2025-02-18 and the 2026 snapshot
   together.
3. **Letta and Zep are strongest.** Letta's first snapshot is one day after
   publication; Zep's is same-day. Row 20 already established that the Zep
   *paper* v1 (2025-01-20) is the origin, so the blog pin is corroboration, not
   the primary receipt.
4. **Live ≠ archived for every source** (all four hashes differ from the row-17
   live fetches: `35a15187…`, `1669df96…`, `f5b72e56…`, and row-20 `8baa4dd1…`).
   Pages have changed since capture; the *claim strings* are stable in both.
   This is exactly why the pin is needed and why it should be cited by snapshot
   date, not just by URL.
5. **Operational note for the next seat:** `archive.org/wayback/available`
   returns **429 too many requests**; the CDX endpoint
   (`web.archive.org/cdx/search/cdx?...&filter=statuscode:200`) and direct
   `id_` snapshot URLs work. Don't burn a turn on the availability API.
6. **Ledger effect:** the §CLASSIFICATION "flag 5" (pin the mutable sources) is
   resolved for these four; no class changes — all rows stay `vendor-only`
   until an independent measurement exists. Proposed annotation:
   `pinned-at: <snapshot timestamp>` on L-S12-02, L-S12-03, L-S13-01, and
   L-S13-02's blog half.

## Consequences for the ledger's reproducibility

Before: reproducing a quote meant trusting a mutable page on the fetch date.
After: a re-verifier can fetch the `id_` snapshot, hash it, and compare to the
sha256 in `row-pin-receipts/MANIFEST.md` — the same standard row 15 used for
LICENSE blobs. The remaining live-only material is the builder's discovery
extracts (now superseded by raw bytes) and any future source without an
archived snapshot.

## Method and limits

- Wayback **CDX** query per URL (`filter=statuscode:200`, limit 200), pick the
  earliest timestamp on/after the publication date; fetch `id_` raw; sha256 the
  stored bytes; grep the claim strings. No model, no benchmark.
- "Contemporaneous" means within days of `datePublished`; the LangChain and
  Mem0 sources are not, and that is reported rather than rounded away.
- Snapshot availability is archive.org's, not ours; a snapshot can be
  re-rendered or dropped. The stored bytes + hash in `team/row-pin-receipts/`
  are the durable copy.
- I did not attempt to pin the arXiv/paper sources (already version-pinned) or
  the vendored GitHub blobs (commit-frozen by construction).
