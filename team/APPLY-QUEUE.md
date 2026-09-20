# APPLY QUEUE — executable landing checklist (for the landing steward)

**Author:** Corvid (`worker-glm-dsh3`) · **Date:** 2026-09-14 · **Cost:** $0, local
**Purpose:** one ordered checklist so the validated-change backlog can be landed
(or rejected) in one window, instead of aging in the log. Every item below is
validated; each has a one-command apply, a post-apply test, and the expected file
hashes (via `probe_patch_handoff_receipt.py`). Tree: `implementer/repo-glm-dsh3`,
base HEAD `57ac038` + the two known uncommitted edits (`external.py`,
`test_preflight_hardening.py`).

## Landing-steward sweep — 2026-09-15 (Corvid, QUEUE S3-5)

**Queue depth: 2 ready → 0 ready (both applied to the working tree, reverse-check
clean; commit is the owner's per AGENTS).**

- Item 1 `ALICE-INSTRUMENT-FIXES.diff` → **APPLIED**; `test_instrument_edge_cases.py`
  + `test_longcontext_null_contract.py` → **11 passed**; reverse-check clean.
- Item 2 `CORVID-PRODUCT-INGEST-FIX-COMBINED.diff` → **APPLIED**;
  `test_preflight_hardening.py` → **9 passed**; all five `run_provider(..., "product")`
  → `ineligible`; reverse-check clean.

**Effects measured after apply:**
- `check_cross_copy_drift` findings **6 → 4**: the two instrument `(NEW)` drifts
  are gone; remaining are the 2 owned `known-drift` plus 2 fork-only `(NEW)`
  (`providers/__init__.py`, `test_known_failures_baseline.py` — P2-chain
  consequences, not addressed by these diffs).
- Cross-tree parity probe: the dsh3 **`GOLDEN-DIVERGE` is gone** (golden half now
  matches canonical); only the P2-chain `CENSUS-DIVERGE` remains. Promotion-gate
  Candidate B's golden half is now wireable.
- Meta-guard **20/20 hold** after the changes.

**Still not landed (owner decisions, not diffs):** `extensions/` sync (dry-run
Rev 3), `team_sync` (already 5/5).

### Sweep 2 — 2026-09-15 (landing steward, QUEUE S3-5)

Applicability re-check over every `team/*.diff` (`git apply --check` /
`--reverse --check` on this tree): **0 READY**, 3 `applied`
(`ALICE-INSTRUMENT-FIXES`, `CORVID-CROSSTREE-PARITY-HARDEN`,
`CORVID-PRODUCT-INGEST-FIX-COMBINED`), and 4 `other`:

- `CORVID-BASELINE-PRODUCT-INGEST-FIX.diff` and
  `CORVID-AGENTMEMORY-PRODUCT-FIX.diff` — **REJECTED as superseded** by the
  combined diff (their test context no longer applies; the combined form carries
  both changes).
- `CORVID-ROW42-CORPUS-FIX.diff` — applies to `team/invocation-corpus-v1/`
  (different root; already applied there).
- `METERS-TOPUP.diff` — `~/conductor-chat/meters.py` (other tree).

**Depth: 0 ready.** No new validated work arrived since sweep 1; the applied
changes remain uncommitted (owner, per the commit-ready state above).

### Commit-ready state (owner: one commit)

The two applies are uncommitted working-tree changes on `repo-glm-dsh3`
(HEAD `57ac038`):

```
 M src/memory_bakeoff/longcontext_null.py      # ALICE-INSTRUMENT-FIXES.diff
 M src/memory_bakeoff/stale_use_penalty.py     #   "      "
?? tests/test_instrument_edge_cases.py         #   "      " (new)
 M src/memory_bakeoff/providers/bm25.py        # CORVID-PRODUCT-INGEST-FIX-COMBINED.diff
 M src/memory_bakeoff/providers/dense.py       #   "
 M src/memory_bakeoff/providers/tfidf.py       #   "
 M src/memory_bakeoff/providers/hybrid.py      #   "
 M src/memory_bakeoff/providers/external.py    #   "  (+ the pre-existing habitus edit)
 M tests/test_preflight_hardening.py           #   "  (+ the pre-existing habitus edit)
```

Suggested message: `Apply validated queue: dsh3 instrument sync + product-flag
fail-closed (landing steward, QUEUE S3-5)`.

Note: HEAD predates this session's work, so **none of the tooling/notes in this
queue are committed either**; that is the separate checker-suite tracking gap
(`CORVID-CHECKER-SUITE-TRACKING-GAP.md`).

## Apply in this order

### 1. `team/ALICE-INSTRUMENT-FIXES.diff` — dsh3 instrument src sync
```
git apply team/ALICE-INSTRUMENT-FIXES.diff
PYTHONPATH=src:vendor/membukkit/src python -m pytest -q \
  tests/test_instrument_edge_cases.py tests/test_longcontext_null_contract.py   # expect 11 passed
git apply --reverse --check team/ALICE-INSTRUMENT-FIXES.diff                    # expect clean
```
Expected post-apply hashes: `longcontext_null.py cf59db82…`, `stale_use_penalty.py a1576482…`,
`test_instrument_edge_cases.py 24d90afb…`. **Effect:** clears 2 of the 4 declared
cross-copy drifts and makes the parity golden half wireable (follow-up, owner).

### 2. `team/CORVID-PRODUCT-INGEST-FIX-COMBINED.diff` — product flags fail closed
```
git apply team/CORVID-PRODUCT-INGEST-FIX-COMBINED.diff
PYTHONPATH=src:vendor/membukkit/src python -m pytest -q tests/test_preflight_hardening.py   # expect 9 passed
git apply --reverse --check team/CORVID-PRODUCT-INGEST-FIX-COMBINED.diff                    # expect clean
```
Expected post-apply hashes: `bm25.py 98c50ca5…`, `dense.py 0b0ed20a…`,
`tfidf.py cdff3a18…`, `hybrid.py 6f124395…`, `external.py cd84d3d8…`,
`test_preflight_hardening.py 7d616f82…`. **Effect:** the four baselines and
AgentMemory return `ineligible` in product mode (no fake product label).

**Use the COMBINED diff, not the two singles.** `CORVID-BASELINE-PRODUCT-INGEST-FIX.diff`
and `CORVID-AGENTMEMORY-PRODUCT-FIX.diff` both insert test assertions after the
same habitus line, so applying them in sequence conflicts on
`tests/test_preflight_hardening.py`. The combined diff is the conflict-free form
and **supersedes both** (their src changes are identical and included).

## Already applied — do NOT re-apply (reverse-check clean)

`CORVID-CROSSTREE-PARITY-HARDEN.diff` · `CORVID-ROW42-CORPUS-FIX.diff`
(team corpus) · `scripts/fix-habitus-adapter.diff` ·
`scripts/fix-results-pointer-defects.diff`.

## Not a diff

`team/REPO-CANONICAL.txt` fork-lag declaration is already applied (rev 23);
`extensions/` drift (`CORVID-EXTENSIONS-CROSSTREE-CENSUS.md`) is still an owner
decision (dry-run Rev 3), not queued here.

## Rejecting

Any item may be rejected with a one-line reason appended to its note; the queue
is cleaned in the same edit. The point is that no item stays silently pending.

— **Corvid** (`worker-glm-dsh3`).
