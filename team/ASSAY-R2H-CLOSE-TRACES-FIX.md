# Assay — R2H `close` traces defect: validated patch + power check

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 (R&D pulse) · **Cost:** $0, offline
**Finding:** `team/ASSAY-R2H-CLOSE-TRACES-BUG.md` (register refresh row, open)
**Scope:** synthetic agent dir in a temp `R2H_STATE`; nothing real read.

## Defect

`cmd_close` collected "traces" with `agent_dir().rglob("traces")`, which matches
the **directory**; `p.is_file()` then dropped it. No trace file was ever
collected, and the manifest recorded `traces: none found … (recorded, not
fabricated)` — a **false-absent record** — even when trace files existed.

## Fix (`r2h-close-traces.diff`)

- pattern `("traces",)` → `("traces/**/*",)` — collects files under any `traces/`
  dir, nested included;
- a third tuple element carries the human label so the `expected_but_absent`
  string stays exactly `traces: …` (manifest field unchanged for a real absence);
- **collision guard:** newly collecting many traces can make two files share a
  basename; the copy destination is uniquified instead of silently overwriting
  evidence. (The session/notification path is unchanged.)

## Power check (real `cmd_close`, canonical vs guarded, same synthetic agent)

| Check | Canonical | Guarded |
|---|---|---|
| trace files collected | **0** | **3** |
| `expected_but_absent` | `traces: none found…` | `[]` |
| bodies exact / no overwrite (flat + nested + duplicate basename) | n/a | **exact, 3 distinct sha256** |
| notifications still collected | 1 row | 1 row |
| store db not copied; hashed only | pass | pass |
| stripped slice no nudge / raw retains nudge | pass | pass |
| no network / one bundle | pass | pass |

Guarded: **11/11**, failures `[]`, `all_pass: true`. Canonical defect
reproduces (`trace_rows: []`, false-absent entry).

**Cross-check with the already-built harness:** the committed
`r2h_close_sandbox_check.py` reports `all_pass False, traces_copied False` on
canonical and, pointed at the **applied** guarded file, `all_pass True,
traces_copied True` — the independent check now agrees the defect is closed.

**Apply check:** `git apply --check` rc 0 against a fresh copy of the deploy dir.

## Adoption — REV-2 applied (Stratum, `team/R2H-FREEZE.md` REV-2)

The freeze owner adopted this patch as **REV-2** on 2026-09-13: canonical
`r2h_deploy.py` sha256 `74e7ae86…` → `06823431…`, all other freeze artifacts
unchanged, deploy to be re-sent to Brian's work machine before day 1. Alice's
second-seat check (`team/ALICE-R2H-REV2-VERIFY.md`) independently confirmed the
applied bytes equal this patch applied to rev-1. RUNBOOK §Close already says
"any `notifications.jsonl`/traces found in the window", so no RUNBOOK edit is
required.

**Re-runnability (closes Alice's 08:13 boundary finding):** now that canonical
carries rev-2, the power check defaults to a **sealed rev-1 copy**
(`sealed-r2h-rev1/r2h_deploy.rev1.py`, sha256 `74e7ae86…`) instead of the live
file, so `python3 .../r2h_close_traces_fix_power_check.py` still re-runs from
any cwd (11/11) and regenerates the **byte-identical** diff. This is a
reproduction-input fix, not a patch revision: `r2h-close-traces.diff` is
unchanged (`f4c4b938…`). `--deploy` still accepts any rev-1 copy.
Re-derived applied state: `applied-rev2-check.json` records
rev-1 `74e7ae86…` → guarded == live canonical `06823431…` (`true`).


## Receipts

- Patch: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/r2h-close-traces.diff`
  sha256 `f4c4b938d01d4f77e99539813630224fe3f765dc5537d0c0a5318c356608cf71` (unchanged)
- Power check (default = sealed rev-1): `.../r2h_close_traces_fix_power_check.py`
  sha256 `42609f01e82e36620421260c72e326df3f0488ec8b3e5a371d0242079e11b000` (was `1ebd56f6…`)
- Sealed rev-1 input: `.../sealed-r2h-rev1/r2h_deploy.rev1.py`
  sha256 `74e7ae86b79343280715af4af77f0a407651ac06e9f2c890aa42ebacfdaa0c54`
- Sealed result: `.../sealed-r2h-close-traces-fix-20260912/result.json`
  sha256 `753c8118893849118d43560fd6fe784857fd01bf0f3dc404ac03e14998c965eb` (was `0cf35cbe…`)
- Applied rev-2 re-derivation: `.../sealed-r2h-close-traces-fix-20260912/applied-rev2-check.json`
  sha256 `77354d2888f071a9236385a50fc93f26c77866b032fe7eaa13b933f5006112d6`
- Existing-harness cross-check: `.../existing-harness-on-guarded.json`
  sha256 `06cfa8c4398eef027cc900e944c33bbbe10ae2cd4297d34711debd7e94eee540`
- Re-run (path-independent): `python3 scripts/verify-20260912-assay-row1/r2h_close_traces_fix_power_check.py`

## Limits

- Synthetic agent dir + fake store bytes; exercises `cmd_close`'s collection
  path, not a live pi installation.
- The `found[:50]` cap is unchanged; >50 trace files still truncate (now
  visibly, with distinct names, rather than silently).
