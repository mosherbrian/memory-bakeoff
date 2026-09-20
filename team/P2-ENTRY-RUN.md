# P2 ENTRY RUN — the locked baselines, measured on the real benchmark (2026-09-13)

**Plain English first.** The portfolio's question is "does any memory
system beat NOT having memory?" Last night that question became runnable:
the pinned benchmark dataset was materialized and verified, and tonight
the three locked baseline arms ran the full held-out benchmark slice —
3,351 questions, zero LLM calls, zero dollars, ~6 minutes. Results are
committed at `results/p2_entry_20260913/` (summary + per-question rows)
with the runner in `scripts/experiment_20260913_p2_entry/`. Nothing is
recommended yet: this entry run measures the baselines other systems must
beat, and it already says something useful — see "what the numbers say."

## What ran (arms, per charter Patch 3)

| Arm | What it is | Dynamic Hit@3 (n=2,631) |
|---|---|---|
| pi-lcm store reader, **tool-level** | Brian's actual recall tool semantics: exact query, then bounded relaxation | **0.2227** |
| pi-lcm store reader, raw | same store queries, no tool-level relaxation (charter row 2's A/B) | 0.0 |
| pi-lcm multi-session-history null | the same store as raw unranked history | 0.0 |
| long-context null (engine seam) | row-4 instrument: everything in the window, unranked | 0.0 |

Slice: held-out 27 personas, dynamic-conflict primary — **n = 2,631,
exactly Gen38's slice**, so these numbers sit beside the frozen anchors
(perseus 0.434, mem0 0.419, bm25 0.226).

## What the numbers say (honest reading)

1. **The tool-level reader lands beside the bm25 lexical floor (0.223 vs
   0.226)** — lexical retrieval with relaxation, no semantics. That is the
   honest strength of the raw store-reader path on conflict questions.
2. **Raw-without-relaxation is a literal 0.0**: strict AND-matching cannot
   meet long natural questions. The A/B is now measured, not assumed —
   the tool's relaxation layer is worth +0.22 Hit@3 by itself.
3. **Both nulls score 0.0 on dynamic** (chronologically-first units are
   essentially never the answer at rank ≤3) and the two null
   implementations — provider passthrough and engine seam, different code
   paths — produced identical aggregates. Internal consistency, receipted.
4. **Under the amended BAR B, nothing here is a candidate** — by design:
   these ARE the baselines. The portfolio's external candidates now have
   a measured floor to beat, on the same protocol, same scorer, same
   pins.

## Integrity receipts

- Pin gate ran first (dataset sha `8ef9ec…`, upstream `ec51d5d…`, adapter
  probes) — `results/p2_entry_20260913/pins.json`.
- Gold was never shown to any arm (scorer-only); credit by session
  identity via released identifiers; measured (3,189) / unmeasured (162)
  / measured-zero kept separate — 162 unmeasured matches Gen38's slice.
- Append mode (store grows per session, the chronology contract) is
  contract-tested; the as-committed suite is 26 passed across the three
  portfolio suites.

## Next

External candidates enter through this same runner (same protocol, same
pins, same scorer); then the stale-use penalty and BAR B arithmetic on
the combined table. Separate decision, separate slice.

— Kiln, 2026-09-13. Run ~6 min; slice ~2h; $0; all local.
