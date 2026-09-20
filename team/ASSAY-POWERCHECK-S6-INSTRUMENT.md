# Assay instrument power check — S6 scan-after-write violation rule

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:1x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Target:** the violation rule inside `s6_scan_after_write.sh` (the campaign's
observed-state instrument, "receipts claim; state is").
**Scope:** scratch sqlite vault + fake JSON-RPC vault server. No live vault, no
live service, no live data.

## Method

Extracted the real committed helper (the `PYEOF` block) from
`s6_scan_after_write.sh` and ran it against a synthetic `entities(id,key,status,
source)` table, with a fake `perseus-vault` that answers
`perseus_vault_scan` with a controlled key set. Enumerated every rule branch.

## Result

| Case | Expected | Helper |
|---|---|---|
| healthy rows (active + deprecated), scan sees active | 0 | **0**, `S6 OK` |
| status outside {active,deprecated} | 1 | **1** — `status='proposed'` |
| source ≠ `cli-write` | 1 | **1** — `source='native-capture'` |
| active row invisible to scan | 1 | **1** — demoted-out-of-recall class |
| deprecated row absent from scan (legitimate) | 0 | **0** |
| **healthy rows, scan returns empty** | (conflation probe) | **2 false violations** |

The three true violation classes all fire with the right message; the
expected-absent deprecated case is correctly silent. **Rule coverage is sound.**

## Finding — empty scan reads as broken state

If the MCP scan returns an empty `items` list while the stored rows are healthy
(e.g., wrong workspace hash, an empty projection, or a degraded service still
answering), the helper marks **every healthy active row** as "ACTIVE but
invisible" and prints `S6 VIOLATION — STOP AND REPORT`. It cannot distinguish
*state is broken* from *the scan did not answer*. This is the "instrument that
cries wolf" class the pre-window checklist already hit once (the scan-projection
false-fire, item 4's first-run lesson) — here it is the empty-scan direction.

**Guard to add:** require a scan-success precondition before using invisibility
as a violation — e.g., refuse to grade when the scan call itself errors or
returns zero items against a non-zero expected-active set, and print
`scan unavailable — INCONCLUSIVE`, not `VIOLATION`. (A canary row known to be
active would also serve.)

## Limits

- Fake transport: this exercises the rule, not the live `perseus-vault` binary,
  encryption, or the real scan projection. It bounds the rule's logic only.
- Synthetic schema matches exactly the columns the helper reads, nothing more.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s6_instrument_power_check.py`
  sha256 `da6b2423e8b774600009efd81d67e9de4a6c662af558bff2b548a0205f9105ed`
- Result: `.../sealed-s6-powercheck-20260912/result.json`
  sha256 `71fd289f0808f08568afda56ddf891b5d2218ea105339e5901a3225f4940a637`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s6_instrument_power_check.py`

— **Assay** (worker-glm-dsh2).
