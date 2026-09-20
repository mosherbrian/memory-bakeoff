# DRAFT — pre-authorization for small reversible validated changes

**Author:** Corvid (`worker-glm-dsh3`), from Muse batch-10 disposition 2
**Date:** 2026-09-14 · **Status:** DRAFT for GiLMore/Brian adoption. Nothing is
pre-authorized by this file; it proposes the class and the gates.
**Fitted cause:** the owner queue held validated, path-limited, reversible diffs
for hours while review capacity was the bottleneck. This is a way to retire that
class without lowering the bar.

## The class (a change may skip serial review iff ALL gates are YES)

| gate | test | where it is checked |
|---|---|---|
| G1 path-limited | touches only paths the memo lists for the class (e.g. a provider file + its test), no config/credential/CI/harness-ground-truth file | the diff's target list |
| G2 one-command tested revert | `git apply --reverse --check <diff>` is clean **and** a stated restore command exists | apply/verify receipt |
| G3 named checks pass on the artifact | the specific tests + guard(s) pass on the patched tree, recorded | handoff receipt |
| G4 logged before landing | a register entry with what/why/revert/check-output exists before the change is committed | shared register |
| GX excluded | **not** a benchmark-semantics change that moves recorded results' comparability, and not a result/claim edit | owner declaration |

Any NO → normal serial review. GX is deliberate: this class is for tooling and
correctness fixes, not for anything that changes a published number's meaning.

## Register entry (append-only log)

```
PREAUTH <id> · <date> · by <seat> · what <one line>
  paths: <list>   patch_sha256: <16>
  revert: git apply --reverse --check <diff>
  checks: <command> -> <result>   receipt: <path>
  owner_ack: <who, when>
```

## Worked exemplars (the two currently-pending diffs)

| diff | G1 | G2 | G3 | G4 | GX | pre-authable if memo adopted |
|---|---|---|---|---|---|---|
| `ALICE-INSTRUMENT-FIXES.diff` (dsh3 src sync) | yes (2 src + 1 test) | yes (reverse-check clean) | yes (pytest 11 passed; golden parity) | yes (`CORVID-PATCH-HANDOFF-RECEIPTS.md`) | edge-fix only; frozen runs used `limit=5`, comparability unchanged | **yes** |
| `CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` | yes (4 providers + 1 test) | yes | yes (pytest 9 passed; product mode fails closed) | yes (same) | capability flag only; no recorded result used it | **yes** |

## What adoption would do (and not do)

- **Do:** let a validated, path-limited, reversible change land without waiting
  for a serial slot, with the four checks and a log entry as the audit trail.
- **Not do:** change the bar for benchmark records, claims, results, or anything
  touching harness ground truth — those stay serial.
- **Owner:** GiLMore/Brian adopt, shrink, or reject; the two exemplars above are
  the first candidates.

— **Corvid** (`worker-glm-dsh3`). $0, design only.
