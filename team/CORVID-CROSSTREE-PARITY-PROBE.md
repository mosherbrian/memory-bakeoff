# Cross-tree parity probe — live 3-tree receipt + Layer A hardening (Muse batch-7 ACCEPT 1+2)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, no LLM, no runs
**Subject:** `scripts/probe_crosstree_parity.py` (committed `57ac038`, deliberately
unwired) — the two batch-7 ACCEPTs: test-ID census + frozen scorer-equivalence.

## Live receipt (read-only on the sibling trees)

```
python3 scripts/probe_crosstree_parity.py --self-test            # self-test: PASS, rc 0
python3 scripts/probe_crosstree_parity.py \
  implementer/repo implementer/repo-glm-dsh2 implementer/repo-glm-dsh3
```

- **Census (A):** canonical is a strict superset of both forks — `0` fork-only
  test IDs. canonical-only = **52** vs dsh2, **56** vs dsh3. The 4-ID
  difference is exactly `tests/test_instrument_edge_cases.py` (dsh2 received it
  from Assay's sync, dsh3 did not) — consistent with the known
  `80a6b08` divergence.
- **Scorer-equivalence (B):** canonical and dsh2 emit the golden fixture
  **byte-for-byte**; **dsh3 diverges** — `limit=0` offers both observations and
  `limit=1` reports `tokens_offered=4` (full history) vs canonical `2` (offered
  window). This is the pre-`80a6b08` `src/memory_bakeoff/longcontext_null.py`,
  confirmed live rather than from a chat log.
- **Cost/size:** one 3-tree pass ≈ 8 s wall (two nested `pytest --collect-only`
  subprocesses dominate).

## New finding — the probe is not guard-ready (Layer A violation)

The suite's Layer A contract (`CORVID-CHECKER-COVERAGE-MAP.md`) requires a
guard to fail **structured**, never traceback, on a missing prerequisite. The
committed probe crashes on both:

| input | committed behavior | required |
|---|---|---|
| no tree arguments | `IndexError` traceback, rc 1 | `missing prerequisite: no tree arguments`, rc 1 |
| a nonexistent tree path | `FileNotFoundError` traceback, rc 120 | `declared tree missing: <path>`, rc 1 |
| one tree | works (base-only checks) | unchanged |

So batch-7 ACCEPT 1+2 is built but **cannot be wired as a guard until
hardened**; wiring the census half as-is would nest `pytest` inside the
meta-guard's own pytest subprocess and make the guard itself crashy.

## Hardening delivered (diff only; owner/QUEUE decision)

- `team/CORVID-CROSSTREE-PARITY-HARDEN.diff` — sha256
  `54392ee56efe2fcf20a6ac8405b9511a65855fbfec302aba34917c8dafbe9969`.
  Adds `preflight(trees)` (no-args + missing-tree structured failures) and two
  `--self-test` cases that drive the real entry point.
- Verified on the hardened copy (sha `6840a4a771a13a12e83dcdccc51a85a9ab6a976064db4c0e2e3ba1f2592f9894`):
  `--self-test` PASS; `main([])` → rc 1 `missing prerequisite: no tree arguments`;
  missing tree → rc 1 `declared tree missing:`; the valid 3-tree path is
  **unchanged** (still rc 1 on the known dsh3 divergence).
- **Not applied.** `scripts/probe_crosstree_parity.py` is left at HEAD
  `ddaa6001…`; the working tree carries only pre-existing unrelated edits.

## Adoption recommendation

- **Distinct from guards 15/16:** they hash *files* across copies; this compares
  *behavior* (scorer output) and *test inventory* — Muse 3+4 "hand-transcribed
  patch mutation" is not caught by a file-hash drift guard.
- **Cheap guard half:** the golden-equivalence check (no nested pytest) is a
  plausible guard 19 / meta-guard control once hardened; second seat Assay.
- **Census half:** keep as a **scheduled standalone census**, not a guard —
  running `pytest --collect-only` in three trees inside the meta-guard's own
  pytest subprocess is the nesting risk, and the 8 s cost is per-wiring, not
  per-commit.
- **Sequence matters:** the probe is red today **by design** on dsh3. Wiring it
  before the dsh3 `src` sync (open for GiLMore) would turn the meta-guard red
  for a known, already-tracked reason. Sync first (`team/ALICE-INSTRUMENT-FIXES.diff`),
  then wire.

— **Corvid** (`worker-glm-dsh3`). Read-only source/exec checks, $0.
