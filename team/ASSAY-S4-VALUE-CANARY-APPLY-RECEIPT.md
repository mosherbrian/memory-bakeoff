# S4 value-canary patch — apply receipt (one page, for the GiLMore decision)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Status:** validated, **not applied**. Decision is **Awaiting GiLMore**
(there is no ruling; the patch changes emitted packet bytes, so it needs one).
**Patch owner for application:** fsync (builder is Kiln's tree).

## What is being decided

The applied B7 gate catches the **word** `draft_id` but not a **value-only**
draft secret (`draft-<hex>`). Live-window census (334 packets,
`ASSAY-S4-LIVE-LEAK-CENSUS.md`): applied gate **8 entries / 4 sessions**;
value-shape detector **24 entries / 58 values**, of which **21 entries are
unique** (16 net) and one session has no word canary at all. A value-only secret
is currently emitted unredacted **and** the builder reports `LEAK-SCAN PASS`.

## Apply receipt (all green)

| check | builder | scanner |
|---|---|---|
| current live base | `6616c48e00e5…` | `1fc8e6c9af8e…` |
| diff | `s4-value-canary-builder.diff` `557cb5bb…`* | `s4-value-canary-scanner.diff` `60c7c14e…`* |
| base == diff's canonical base | ✅ | ✅ |
| `git apply --check` on the live tree | ✅ | ✅ |
| applied bytes == sealed guarded file | ✅ `568face44b9e…` | ✅ `33aa07cf13d9…` |

*rev-2 diff hashes (post `re.I`): builder `ba907167…`, scanner `7498e3a443…`.
Receipt: `.../s4-value-canary/apply_receipt.json` `7030287a…`.

## Commands

```bash
cd implementer/repo   && git apply <...>/s4-value-canary-builder.diff
cd implementer/repo-glm-dsh2 && git apply <...>/s4-value-canary-scanner.diff
# verify: python3 <...>/value_canary_apply_check.py  → all_pass: true
```

Rollback: `git apply -R <diff>` (or revert the commit); packet bytes revert with
it.

## What changes / what does not

- **Changes:** the leak gate and redaction add `draft-[0-9a-f]{6,}` (`re.I`) and
  drop the bare `draft_id` canary. Value-only secrets are redacted/flagged;
  word-only prose stops false-alarming. Rebuild of the frozen samples showed the
  s3 bare-confirmer class clears (ROW9, separate).
- **Does not change:** any metric formula, any frozen criterion, the rater
  source (sealed packets remain the rater's input — the gate only refuses
  leaks). Power checks: predicate **15/15**, end-to-end **4/4**, census
  **8→24 findings / 5→58 values**, no false positives on the 102-summary tree.
- **Residual (documented):** value shape only; a secret in another format still
  escapes (unchanged from the B7 gate's canary limits).

## Decision sentence

> Apply the S4 value-canary builder+scanner patch at their current hashes
> (builder `6616c48e…` → guarded `568face4…`; scanner `1fc8e6c9…` → guarded
> `33aa07cf…`), re-freeze the builder hash, and require
> `check_required`/`LEAK-SCAN` nonzero before any packet reaches a rater.

## Receipts

- `ASSAY-S4-VALUE-CANARY-FIX.md` (patch, rev 2, power checks, e2e, census)
- `ASSAY-S4-LIVE-LEAK-CENSUS.md` (live exposure; 21 unique / 16 net)
- `value_canary_apply_check.py` `b2448d57…`, `apply_receipt.json` `7030287a…`
- `ALICE-S4-VALUE-CANARY-SECONDCHECK.md` (case-sensitivity boundary, folded)

— **Assay** (`worker-glm-dsh2`). No tree modified.
