# PORTFOLIO P1 — discovery receipts for the five ❓ license rows

**Phase 1 discovery (charter `PORTFOLIO-CHARTER-draft.md`, G0-approved at
sha256 prefix `6e7f7d8df1a73878`).** Prepared by Kiln (worker-glm-2) for
**Stratum's P1 license-verification receipt** — discovery is not
verification; every row below carries the raw evidence so verification is a
read, not a hunt. Fetch method: `raw.githubusercontent.com/<repo>/<pinned
commit>/<LICENSE>` — the license **at the pinned commit**, which is what
governs our vendored copies. SHA-256 of each fetched file is recorded; any
mismatch at Stratum's re-fetch means upstream moved or the pin is wrong.

**Headline: all five ❓ rows resolve PERMISSIVE at their pins — four
Apache-2.0, one MIT. No copyleft blocker found. Verification (Stratum, P1)
should confirm the identifications below against the frozen fetches in
`docs/PORTFOLIO-P1-discovery/`.**

| # | System | Upstream | Pinned commit | License at pin | Fetched file (sha256, first 20) |
|---|---|---|---|---|---|
| 6 | habitus | `munch2u-a11y/Habitus-AI` | `f93b770e4b3c1875151dc13eb90421598c3efa5f` | **Apache-2.0** | `habitus-LICENSE.fetch` `27283c037eb34dee9235` |
| 7 | agentmemory | `rohitg00/agentmemory` | `e04ba88819c365c9acf9d6661ea802143e728bd6` | **Apache-2.0** | `agentmemory-LICENSE.fetch` `76c8d49ab42216a2533f` |
| 8 | hindsight | `vectorize-io/hindsight` | `ebad478240d3171bb88201ececda5e8d9883d22d` | **MIT** (Copyright (c) 2025 Vectorize AI, Inc.) | `hindsight-LICENSE.fetch` `01fde0bedf83bdc18506` |
| 9 | membukkit | `memseekai/membukkit` | `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` | **Apache-2.0** | `membukkit-LICENSE.fetch` `cfc7749b96f63bd31c3c` |
| 10 | claude_mem | `thedotmack/claude-mem` | `fa6a1e9ec12d23f98326a9b26e243acb0819e105` (package 13.18.0) | **Apache-2.0** | `claude_mem-LICENSE.fetch` `cfc7749b96f63bd31c3c` |

Notes for the verification pass:

- membukkit and claude_mem fetches share the same sha256 prefix — both are
  the standard unmodified Apache-2.0 text; identical text is expected, not
  suspicious. habitus/agentmemory Apache texts differ only by registry
  boilerplate length (10,788 vs 10,764 bytes).
- hindsight's MIT notice names **Vectorize AI, Inc., 2025** — the same
  upstream as the pg0 provenance receipt (`vendor/pg0-bin/UPSTREAM.md`,
  `vectorize-io/pg0` v0.15.1, used only as a local Postgres launcher in a
  network-isolated sandbox).
- The vendored trees under `vendor/` contain **no LICENSE files** — the
  benchmark intentionally vendors only runtime modules (blob-hash-verified
  per `vendor/*/UPSTREAM.md`), so upstream-at-pin is the only honest license
  surface. Local shims (`__init__.py`, telemetry/progress/usage stubs) are
  benchmark-local and carry no upstream license claims.
- Provenance cross-references: `research/UPSTREAM_SOURCES.md` (repo slugs +
  API assumptions, checked 2026-08-30), `research/CLAUDE_MEM_FINDINGS.md`
  (pin fa6a1e9e = package 13.18.0; the earlier 10.6.1 association was
  corrected upstream of this receipt), `research/HINDSIGHT_GEN31_LONGITUDINAL.md`
  (hindsight-embed source commit ebad4782).
- P1 remainder (owned per charter seat map): Stratum verifies the five
  identifications against these fetches; Zep stays PARKED per G0 (no license
  work authorized for it).
