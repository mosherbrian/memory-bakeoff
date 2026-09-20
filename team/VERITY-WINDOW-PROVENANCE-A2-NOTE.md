# Verity freeze-check: WINDOW-OPENING provenance needs its A2 line (2026-09-14)

Read-only re-measurement (implementer tree untouched):

- Live `extensions/pi-perseus-recall/vault.ts` = `50aefb3f…` (A2 v3, fbd3149).
- Live `extensions/pi-perseus-recall/index.ts` = `24296ad6…` (A1, 2e247bb).
- Both match the expected post-A2 state exactly. No drift, no surprise delta.

**Finding (doc, low):** `team/WINDOW-OPENING.md` lines 82–83 still state
`vault.ts` = `905f604c…` (the A1 value) as current, while line 211 already
anticipates "(A2, when landed, moves `vault.ts` to `50aefb3f…`)". A2 has
landed, so the anticipation is now the state and lines 82–83 read stale.
Fix (owner Kiln/Stratum, doc-only): one A2 amendment line under §(1) —
`vault.ts 905f604c → 50aefb3f (A2 v3, fbd3149, Assay 10/10)`, suite still
47/47 — or fold into Assay's pending provenance diff. Close-build reporting
already splits at the deploy per fsync tick #48, so nothing is blocked.

$0, read-only, one turn. — Verity 2026-09-14
