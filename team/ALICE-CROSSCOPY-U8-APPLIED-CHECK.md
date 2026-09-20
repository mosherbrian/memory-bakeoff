# Second-seat — applied cross-copy U8 vacuous fix (`dde0bbc6…`) + one residual

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 20:4x UTC · **Cost:** $0, synthetic real-CLI probes, one turn.
**Trigger:** Assay's fix for my U8 latent finding (`ASSAY-CROSSCOPY-U8-VACUOUS.md`)
is **live** in `repo-glm-dsh3` (`dde0bbc6…`) though the note says "not applied".
Driver: `row-crosscopy-u8-applied-check/alice_u8_applied_check.py` (`762eb282…`),
result `result.json` (`bbdd695b…`). Read-only; temp fixtures only.

## Verdict

**PASS — the fix lands as designed.** The live guard is byte-identical to Assay's
guarded file (`dde0bbc6…`), and reverse-applying `crosscopy-u8.diff`
(`42948ee9…`) is clean, so the live file *is* the patched one (Corvid applied
it). Behaviour on the real CLI:

| case | result |
|---|---|
| `shared:`-only declaration (no `tree:`) | **rc 1**, `no declared tree set … refusing to fall back to DEFAULT_TREES`, no `findings:` line (not `--fail`-gated) — the vacuous pass is closed |
| explicit `--trees` | rc 0, no discovery — the meta-guard's control is unaffected |
| real `REPO-CANONICAL.txt` | rc 0, **2 findings** (both known drifts) — unchanged |
| `--self-test` | rc 0 |

## Residual (low) — a comment-only/empty declaration still falls back silently

The new guard fires only on `shared and not trees_rel`. A declaration that exists
but carries **no directives at all** (all comments/blank) yields
`shared == []` and `trees_rel == []`, so it silently uses `DEFAULT_TREES` +
`DEFAULT_FILES`, skips discovery, and reports `findings: 2`, **rc 0** — verified.
Under U6's own principle and the U5/U8 design ("the declaration is the source of
truth"), an empty declaration is a declaration of nothing, not a request for
hardcoded defaults; deleting its contents currently disables U8 with no signal.

**Suggested fix:** when no `--trees` is given, fail if the read declaration
yields **no `tree:` lines at all** (`no declared tree set`), regardless of
whether `shared:` entries exist. That subsumes the current condition and closes
the emptied-declaration path; the `--trees` bypass is unchanged.

## Scope and limits

- The residual is latent: the shipped declaration has both `tree:` and `shared:`
  lines, so the live census is unaffected.
- I did not re-run Assay's staged 4/4 power check; I drove the real CLI on
  shared-only / empty / explicit-`--trees` / live declarations independently.
