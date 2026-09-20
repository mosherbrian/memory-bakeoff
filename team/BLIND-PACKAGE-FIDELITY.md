# Blind-package fidelity receipt (construction check)

**Author:** Corvid (`worker-glm-dsh3`), package preparer
**Date:** 2026-09-14 · **Cost:** $0, local, read-only
**Purpose:** a second, independent control on the blind package (alongside
`probe_blind_package_scan.py`, which checks verdict **absence**): this checks the
items are **faithful** to their sources — no decision was altered and only a
verdict field was removed.

## Transformation applied

- Task A items (`smoke-firing-decisions.jsonl`) = source run decisions joined to
  the corpus prompts/summaries. **Removed:** `expected`, `match`, `seconds`.
  **Kept:** the observed `got` as `observed_decision`. **Added:** `item_id`.
- Task B items (`row41-events.jsonl`) = the de-identified bundle events.
  **Added:** `item_id`; **no field removed or altered.**

## Check result

```
smoke items = 36 · mismatches = 0
  each observed_decision == source got; prompt + record_summaries == corpus;
  no expected/match/seconds key present
row41 items = 10 · mismatches = 0
  every source key present with the same value; only `item_id` added
```

## Hashes

| artifact | sha256 |
|---|---|
| source run decisions `/tmp/row36-postfix-1842/results.jsonl` | `fab95753945b65787268a63625c2f5870cdf712d17a4ffa8645b2950dbec7cbc` |
| `team/invocation-corpus-v1/corpus.jsonl` | `65ba859278827719f8ae532e5278edec429951d64bed878c41f618bc9a3adf6c` |
| source `team/outcome-pilot-bundle-20260914/events.jsonl` | `7cd03aa575261f9a3a6d2abe177490616810b7c46fb48122778bc0c426ba4d14` |
| package `team/blind-package-20260914/smoke-firing-decisions.jsonl` | `bb7724e9d083014bff8b18e526c37d3574c309e6b64108bcaf1e676eb5f17e5b` |
| package `team/blind-package-20260914/row41-events.jsonl` | `4ab49b2c839cb0941e15629fcb60c58468f38a69663bb6d2c3d02e87598c30b2` |

## Notes / limits

The source run file lives under `/tmp` and is ephemeral; this receipt pins its
hash at check time. This check was run by the package preparer, so it is a
construction receipt, not an independent second seat; the independent control is
`probe_blind_package_scan.py` (verdict absence), and the judge's own task was the
substantive one. This file is **outside** the package (the package's hashes are
unchanged).

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
