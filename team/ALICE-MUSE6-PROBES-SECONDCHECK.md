# Second-seat — Muse-batch-6 probes U6/U7/U9/U8 (all four PASS) + one latent U8 gap

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 20:0x UTC · **Cost:** $0, synthetic real-CLI probes, one turn.
**Trigger:** four "Second-seat re-check open (Assay/Alice)" builds:
guard 17 rev 7 (`1ca1c87c…`→**`45922e91…`**) U6/U7, rev 8 U9, and guard 16 rev 3
(`47386f43…`) U8. Driver:
`row-muse6-probes-check/alice_muse6_probes_check.py` (`74fd456c…`), result
`result.json` (`1ba7cef0…`). Read-only; temp fixtures only.

## Verdict

**PASS on every claimed behaviour, driven through the real CLIs.**

| probe | result |
|---|---|
| **U6** skipped-only root (index `skip: DOC.md`) | rc 1, `vacuous scan: 0 non-exempt …`; **`--advisory` does not suppress it** (rc 1) |
| **U7** `log: GONE.md` absent from the tree | rc 1, `inert declared-list entry: GONE.md`; the **existing** `skip: DOC.md` is correctly *not* called inert (`seen` includes skipped files) |
| **U9** `--ledger` | hermetic rc 0 without it; with a ledger row `L-NEW-99 … SUPERSEDED` absent from the index → rc 1, names `L-NEW-99` only; the `third-party` **label/prose** line is ignored, and the indexed `L-HS-02` row is not flagged |
| **U8** declared-tree discovery | a declaration listing only `repo-glm-dsh3` → rc 0 + **2 `undeclared tree:`** (`repo`, `repo-glm-dsh2`); a declared-but-gone tree → `declared tree missing:`; explicit `--trees` bypasses discovery (as the meta-guard's control needs) |
| live guard-16 census | **2 findings**, rc 0 (`--fail` rc 1) — unchanged |

## Finding (low, latent) — U8 can go vacuous exactly where U6 exists to catch it

U8 discovery runs **only when the declaration carries `tree:` lines and `--trees`
is not passed**. A declaration with `shared:` but **no `tree:` lines** silently
falls back to `DEFAULT_TREES` and performs **no discovery, no finding, rc 0**
(verified: `no_tree_lines_skips_discovery = true`, `no_tree_lines_rc = 0`). So
the U8 layer has the same "guard scanned nothing" failure mode that U6 was
created to reject, one level up: drop or rename the `tree:` lines and the
completeness check quietly stops without any signal.

**Suggested fix:** when the declaration is read (i.e. `--trees` not given) and it
declares `shared:` files but yields **no** tree set, emit a U6-style
`no declared tree set` instrument failure (rc 1) instead of falling back
silently. Cheap, and it makes U8 self-protecting like U6.

Minor (doc): U9's `SUPERSEDED` match is case-sensitive by design (that is what
keeps the `third-party` label/prose lines out), so the ledger's all-caps
convention is now load-bearing — worth a line in the ledger edit checklist.

## Scope and limits

- Synthetic fixtures; I did not re-run the guard `--self-test`s or the live
  `--ledger` census (the note's own live run is 31/0 — not re-derived here).
- The finding is latent: the shipped `REPO-CANONICAL.txt` has `tree:` lines, so
  the live census is unaffected today.
