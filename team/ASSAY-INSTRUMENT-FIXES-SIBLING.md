# Assay: instrument-fix sibling apply + second driver (repo-glm-dsh2)

**Seat:** Assay (`worker-glm-dsh2`, lane `acp-dsh`) · **Date:** 2026-09-14 05:2x UTC · **Cost:** $0, local unit path
**Serves:** Kiln's 04:4x handoff — "`repo-glm-dsh2` still carries the pre-fix
instruments plus the row-12 pointer defects (Assay's lane, owner's call)" — and
`team/ALICE-INSTRUMENT-FIXES.md`.

## Verdict

**Alice's validated diff applies cleanly to `repo-glm-dsh2` and the fork now
reaches canonical parity.** Canonical re-driven **22 → 26**; the sibling went
**15 → 19** on its available files, then **→ 26** once the missing canonical
contract test was synced. The three patched files are byte-identical to
canonical's fixed copies. Canonical was not touched (Kiln's `80a6b08`).

## Second driver of the canonical landing

| check | claim | re-derived |
|---|---|---|
| canonical focused suite | 22 → 26 after `80a6b08` | **26 passed** in 0.03s (re-run here) |
| patch identity | `ALICE-INSTRUMENT-FIXES.diff` sha `073376c2…` | sha256 `073376c23fd5…` matches |
| diff touches | 2 src files + 1 new test | same 3 files, +44/−6 |

## Sibling apply (`repo-glm-dsh2`, branch `work/glm-dsh2`)

| step | result |
|---|---|
| `git apply --check` | APPLIES CLEAN |
| pre-patch, fork's 2 available files | **15 passed** |
| post-patch (+ edge-cases) | **19 passed** (15 + 4 regressions) |
| root cause of the 22-vs-15 gap | fork lacked `tests/test_longcontext_null_contract.py` (7 tests); `15 + 7 = 22` |
| after syncing that canonical test | **26 passed** in 0.04s |

Commits (src/test only; the tree's unrelated probe scripts were left alone):

| commit | content |
|---|---|
| `8fcaf5a` | Alice's 4 fixes + `tests/test_instrument_edge_cases.py` |
| `810cdd3` | `tests/test_longcontext_null_contract.py` (canonical → fork) |

Byte-identity of the landed files vs canonical `80a6b08`:

| file | sha256 (both trees) |
|---|---|
| `src/memory_bakeoff/longcontext_null.py` | `cf59db82…` |
| `src/memory_bakeoff/stale_use_penalty.py` | `a1576482…` |
| `tests/test_instrument_edge_cases.py` | `24d90afb…` |
| `tests/test_longcontext_null_contract.py` | `805e03b1…` |

## Finding for the owner

**Both forks lack `tests/test_longcontext_null_contract.py`; it is canonical-only.**
It imports only `ARM_VERSION` / `LongContextNull` and passes 7/7 against dsh2's
fixed src (verified standalone before adding). I synced it into dsh2; **dsh3
still lacks it**, so dsh3's focused baseline reads 15, not 22. The count gap is
entirely that file — not a diverged instrument.

## Limits

* Unit path only: no benchmark, no runner, no LLM, no live lane; the fix A/D
  numbers that would move a P2 score are covered by the 4 regressions, not by a
  run.
* Canonical `implementer/repo` untouched; only `repo-glm-dsh2` changed, and only
  `src/` + `tests/` (3+1 files).
* The row-12 `RESULTS.md` pointer defects that Kiln's note bundled with this
  handoff are **not** addressed here — separate item, still open in dsh2.

— **Assay** (`worker-glm-dsh2`). $0, one turn, local.
