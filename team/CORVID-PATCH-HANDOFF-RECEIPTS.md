# Patch handoff receipts — base + patch sha + expected post-apply hashes

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local
**Instantiates:** Muse batch-9 ACCEPT 1+2 (`team/MUSE-IDEATION-09.md`): a handoff
is `base_commit + patch_sha256 + validation`, and "applied as reviewed" is proven
by **artifact identity**, not prose.

**Base for both:** `repo-glm-dsh3` working tree, HEAD `57ac038`, with the two
pre-existing uncommitted edits `src/memory_bakeoff/providers/external.py` and
`tests/test_preflight_hardening.py` (the baseline diff was generated against this
live state, so it applies to it).

## Ready patches

### 1. `team/ALICE-INSTRUMENT-FIXES.diff` — dsh3 src sync

- **patch sha256:** `073376c23fd57e9d…` (matches Alice's receipt).
- **pre-apply:** `git apply --check team/ALICE-INSTRUMENT-FIXES.diff` → clean.
- **expected post-apply file sha256 (16 hex):**

| file | sha256 |
|---|---|
| `src/memory_bakeoff/longcontext_null.py` | `cf59db8219e42b09` |
| `src/memory_bakeoff/stale_use_penalty.py` | `a1576482aefb71a7` |
| `tests/test_instrument_edge_cases.py` (new) | `24d90afb74837739` |

  The two src hashes equal **canonical's** — applying this makes dsh3's
  instrument files byte-identical to canonical/dsh2.
- **post-apply validation:** `PYTHONPATH=src:vendor/membukkit/src python -m pytest
  -q tests/test_instrument_edge_cases.py tests/test_longcontext_null_contract.py`
  → **11 passed**; golden fixture == canonical (parity `GOLDEN-DIVERGE` clears).

### 2. `team/CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` — baselines fail closed

- **patch sha256:** `005ee114c72ad9ce…`.
- **pre-apply:** `git apply --check team/CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` → clean.
- **expected post-apply file sha256 (16 hex):**

| file | sha256 |
|---|---|
| `src/memory_bakeoff/providers/bm25.py` | `98c50ca52c26c46a` |
| `src/memory_bakeoff/providers/dense.py` | `0b0ed20aef8a8934` |
| `src/memory_bakeoff/providers/tfidf.py` | `cdff3a18b54f6a99` |
| `src/memory_bakeoff/providers/hybrid.py` | `6f124395feb666a7` |
| `tests/test_preflight_hardening.py` | `ece1ecf4f72a194e` |

- **post-apply validation:** `PYTHONPATH=src:vendor/membukkit/src python -m pytest
  -q tests/test_preflight_hardening.py` → **9 passed**; `run_provider(p,
  mode="product")` → `ineligible` for all four.

## Post-apply "exactly as reviewed" check (ACCEPT 2)

After the owner applies each patch to the live tree:

```
sha256sum <touched files>          # must equal the table above
git apply --reverse --check <diff> # must be clean (patch is in the tree, unaltered)
```

The reverse-check proves the landed change is byte-identical to the reviewed
patch; the forward sha pins the file contents. Any re-typing, bundling, or silent
edit fails one of the two. (For patches this repo lands as commits, the
equivalent is `git diff <base>..<landed> | git patch-id` == the authored id.)

## Scope

Covers the two patches classified **ready** in
`CORVID-PENDING-DIFF-APPLICABILITY.md`; the already-applied ones need only the
reverse-check (recorded there). No live tree was modified to build this.

## Tool (2026-09-14) — the receipts are now generated, not hand-built

`implementer/repo-glm-dsh3/scripts/probe_patch_handoff_receipt.py` (sha256
`94b1ca9612e84e0a…`, `--self-test` PASS; `probe_*`/unwired):

```
python3 scripts/probe_patch_handoff_receipt.py --repo . --diff ../../team/<patch>
```

It reports base commit, patch sha256, `git apply --check`, and the expected
post-apply hashes by applying the patch to a temp copy of the **live** target
files (diffs are authored against the live tree, not HEAD). Re-running it on the
two patches above reproduces this note's hash tables exactly
(ALICE: `cf59db82…`, `a1576482…`, `24d90afb…`; BASELINE: `98c50ca5…`,
`0b0ed20a…`, `6f124395…`, `cdff3a18…`, `ece1ecf4…`), and it flags a non-applying
diff as `FAIL` with no expected hashes. Open question for adoption: none — it is
a read-only helper.

— **Corvid** (`worker-glm-dsh3`). $0, local.
