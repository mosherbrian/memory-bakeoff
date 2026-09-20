# Second-seat — cross-copy U8 v2 (`f8bd89a9…`): empty-declaration residual closed

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 21:1x UTC · **Cost:** $0, synthetic real-CLI probes, one turn.
**Trigger:** `ASSAY-CROSSCOPY-U8-VACUOUS.md` Rev 2 answers my applied-check
residual; the live guard is already v2 (`f8bd89a9…`).
Driver: `row-crosscopy-u8-v2-check/alice_u8_v2_check.py` (`4430865e…`), result
`result.json` (`e08c6a22…`). Read-only; temp fixtures only.

## Verdict

**PASS — the residual is closed and nothing else moved.** Live guard equals
Assay's v2 guarded file (`f8bd89a9…`); reverse-applying `crosscopy-u8-v2.diff`
(`d5438b6a…`, base = the v1 `dde0bbc6…`) is clean, so the live bytes are the v2
patch. Declaration matrix on the real CLI:

| declaration | rc | behaviour |
|---|---|---|
| **empty / comment-only** | **1** | `no declared tree set … refusing to fall back to DEFAULT_TREES` — was silent rc 0 in v1 |
| `shared:` only | 1 | same failure |
| `tree:` only (no `shared:`) | 0 | discovery runs (2 `undeclared tree:`), findings 2 — valid use, unchanged |
| `tree:` pointing at a gone dir | 0 (advisory) | 3 `undeclared tree:` + `declared tree missing:` + missing-file findings; `--fail` gates |
| explicit `--trees` | 0 | no discovery — the meta-guard's control still works |
| real `REPO-CANONICAL.txt` | 0 | **2 findings**, both known drifts — unchanged |
| `--self-test` | 0 | PASS |

The v1→v2 condition (`shared and not trees_rel` → `not trees_rel`) is the right
generalization: it makes "the declaration declares no tree scope" an instrument
failure regardless of the file list, while still letting a tree-only
declaration run on `DEFAULT_FILES`.

## Scope and limits

- Latent-only either way: the shipped declaration has both directive kinds.
- I did not re-run Assay's staged 5/5 power check; I drove the four declaration
  shapes plus explicit `--trees`, self-test and the live census independently.
- No tree modified; no further residual found in v2.
