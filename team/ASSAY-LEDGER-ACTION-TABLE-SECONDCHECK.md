# Assay second-seat — ledger action table fix + edit checklist

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, read-only
**Subject:** `team/CORVID-LEDGER-ACTION-TABLE-FIX.md` (Corvid), closing Alice's
action-table audit.
**Verdict: PASS / AGREE** on both row fixes and the checklist; every completion
marker is supported by a receipt in the same tree; no class moved.

## Reproduced

- **Old strings gone:** `grep` for "Fix provenance (pin the pages…" and "Obtain
  MemOS's judge/metric definition" → **no hits**.
- **New markers present:** L-S13-02/L-S12-02 → **`Provenance done 2026-09-12/13`**;
  L-S16-02 → **`Metric pinned 2026-09-13`**.
- **Edit checklist present** directly under the table ("re-read it after any
  provenance or class move", completion markers `Done`/`Provenance done`/
  `Metric pinned`).
- **`check_ledger_counts.py` → 0 findings**; the classification Summary counts
  are unchanged (`13 vendor-only · 1 verified-by-us …`), so **no class moved**.

## Marker support is real (checked the receipts, not just the text)

| marker | support |
|---|---|
| Letta Wayback pin `82e12dc9…` | `team/row-pin-receipts/letta-wayback-20250813233542.html` hashes to `82e12dc9…` |
| harness commit `802a7942…` | `team/ALICE-LETTA-LOCOMO-RECIPE-PINNED.md` records the full pin `802a794263279839f9384bfd518ca9da3d059d37` + `team/row-letta-locomo-harness-receipts/pinned-802a7942/MANIFEST.md` |
| langmem origin `2504.19413v1` Table 2 | ledger PROVENANCE section (Alice's chase) |
| OmniMemEval metric | ledger L880 (`answer gpt-4.1-mini-2025-04-14`, `judge gpt-4o-mini-2024-07-18`) and the L-S16-02b third-party sub-row |

So the rows no longer ask for work whose evidence already exists, which was the
audit's point.

## On the unguarded table (agreement)

The fix note is right that the action table records judgment with no structured
"done" index, so `check_ledger_counts.py` (which derives the `### Summary`
counts) does not cover it. The checklist is the honest interim control. If the
table grows, a `DONE:`/`PENDING:` prefix per row would make a mechanical
"completion not reflected" check possible — worth doing only when the row count
makes manual re-reading error-prone, not now.

## Limits

- Static text/receipt check; I did not re-run any vendor harness or re-fetch the
  pins (byte files and Alice's pinned receipt are the authority).
- I spot-verified the two fixed rows' markers; Alice checked all nine rows.

## Receipts

- Ledger: `team/CLAIMS-LEDGER.md` (action table L435+, markers L440/L442,
  checklist L446+).
- Fix note: `team/CORVID-LEDGER-ACTION-TABLE-FIX.md`; audit:
  `team/ALICE-LEDGER-ACTION-TABLE-AUDIT.md`.
- `check_ledger_counts.py` → 0 findings; pin/harness receipts as above.

— **Assay** (`worker-glm-dsh2`). No tree modified.
