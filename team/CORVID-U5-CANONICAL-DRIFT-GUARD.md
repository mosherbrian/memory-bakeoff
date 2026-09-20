# GUARD — cross-copy policy drift (guard 16, U5)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-13 · **Cost:** $0, static, read-only
**Trigger:** Alice's U5 feasibility audit (`team/ALICE-U5-CANONICAL-DRIFT-AUDIT.md`,
sha `84fdaeeb…`): the coverage map's open U5 (repo-level duplicated-canonical
drift) is live. Owner of the *governing-file* edit stays Kiln/GiLMore; this
artifact makes the drift machine-visible and declares the canonical copies.
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_cross_copy_drift.py`
sha256 `f8bd89a90c2a08fbdd0b083c3c2df608e1cab0bac769f27c915f03930ad39eb3`
(rev 5; rev 4 `dde0bbc6…`, rev 3 `47386f43…`, rev 2 `f683903b…`, rev 1 `1283f215…`).

## Declaration

`team/REPO-CANONICAL.txt` declares the three checkouts, the canonical tree
(`implementer/repo`), the shared files, and the two known/owned divergences.

## Census (Corvid re-derived, matching Alice's hashes)

| File | dsh3 | canonical | dsh2 | Verdict |
|---|---|---|---|---|
| `AGENTS.md` | `84432d4d` | `84432d4d` | `84432d4d` | identical |
| `tests/KNOWN_FAILURES.json` | `7da171eb` | **`1164fbc8`** | `7da171eb` | **drift** |
| `RESULTS.md` | `abe0832f` | `abe0832f` | **`ec3452cd`** | **drift** |
| `README.md` / `DECISION_MEMO.md` / `STATUS_AND_FINDINGS.md` | identical | identical | identical | identical |

**Why it matters:** the AGENTS guard reports **3 findings on canonical**
(2 stale totals + the false-pin claim) but **1 on the forks** (false pin only).
So a guard verdict is tree-dependent, and a reader comparing trees sees a
different state. The `KNOWN_FAILURES.json` divergence is the cause; the
`RESULTS.md` divergence is the known dsh2 row-12 defect.

## Guard behavior

- Hashes each declared file in each tree; >1 distinct hash → `cross-copy drift`
  finding with every tree's prefix; a file missing from a tree → finding.
- **Advisory by default** (exit 0) because the live drift is owned; `--fail`
  gates. Self-test: identical trees clean, drift flagged, missing file flagged.
- Live census: **2 drifts** (`KNOWN_FAILURES.json`, `RESULTS.md`), rc 0.

## Recommendation (for Kiln/GiLMore; not applied)

- **U5-A (short):** update canonical `AGENTS.md` to the pruned totals
  (1621/10/3/0) and propagate to the forks, so all three agree.
- **U5-B (durable):** drop hard-coded totals from `AGENTS.md` and point at
  `tests/KNOWN_FAILURES.json` as the single source; then the AGENTS guard has
  nothing to drift.
- Either way, run `check_cross_copy_drift.py --fail` as the closure gate.

## Limits

- Compares **bytes/hashes**, not semantics; identical files can both be wrong.
- The default file list is a declaration, not a discovered set; a new shared
  policy file must be added to `team/REPO-CANONICAL.txt` and the guard's list.
- It does not decide which copy is correct; the declaration names canonical.

## Rev 2 (2026-09-13) — the declaration is now the source of truth

Assay's second seat (`ASSAY-U5-DRIFT-GUARD-SECONDCHECK.md`, patch
`d8b69b39…`, Alice second-seat PASS `c598effb…`) found two issues, both folded:

- **F1 (real):** rev 1 never read `team/REPO-CANONICAL.txt`; `DEFAULT_FILES` was
  hardcoded and `known-drift:` was unconsumed, so a new `shared:` line had no
  effect. `_read_declaration()` now parses `shared:` (file list) and
  `known-drift:` (owned divergences); the live census labels both known drifts
  `(known-drift)`, and a drift outside the declaration shows `(NEW)`.
- **F2 (low):** an all-unreadable shared file read clean. Now an
  `unreadable in a tree` finding.

Verified independently by Corvid: live census 2 findings, both `(known-drift)`,
rc 0 / `--fail` rc 1; `--files RESULTS.md` labels `(NEW)`; an unreadable
synthetic file yields `unreadable in a tree`; self-test PASS.
`1283f215…` → **`f683903b…`**.

**Still open (governance, not the guard):** the canonical divergence itself is
unfixed — canonical `KNOWN_FAILURES.json` is pruned while the forks are not, so
canonical still reports 3 AGENTS-guard findings vs 1 on the forks. Owner fix
(U5-A/B) is Kiln/GiLMore; then `--fail` is the closure gate.

## Rev 3 (2026-09-13) — U8: declared tree set + checkout discovery

The compared tree set now comes from the declaration's `tree:` lines (previously
hardcoded `DEFAULT_TREES`), and the guard discovers every `implementer/repo*`
checkout: one absent from the declaration is `undeclared tree: <path>`, and a
declared tree that is gone is `declared tree missing: <path>`. This closes
coverage-map **U8** (Muse 6.5a) — a new fork can no longer go uncompared. The
self-test covers discovery / undeclared / missing; the meta-guard's **explicit**
`--trees/--files` control is unaffected (16/16). Live census unchanged: **2 known
drifts, 0 tree gaps**, rc 0 / `--fail` rc 1. Guard `f683903b…` →
**`47386f43…`**.

## Rev 4 (2026-09-13) — U8 vacuous-scan hole closed

Alice's `ALICE-MUSE6-PROBES-SECONDCHECK.md` found rev 3's discovery ran only when
the declaration carried `tree:` lines: a `shared:`-only declaration silently fell
back to `DEFAULT_TREES` with no discovery and rc 0 — the undeclared-tree check
could go vacuous exactly where it is needed. Assay's validated
`crosscopy-u8.diff` (`42948ee9…`, guarded `dde0bbc6…`) is applied: a
`shared:`-bearing declaration with no tree set now emits `no declared tree set: …
refusing to fall back to DEFAULT_TREES` with **rc 1**, not gated by `--fail`,
while explicit `--trees` still bypasses the declaration. Independently
reproduced by Corvid on a staged `implementer/repo*` layout (shared-only → rc 1;
full declaration → 0 findings rc 0; `--trees` bypass → rc 0; `--self-test`
PASS). Live census unchanged; meta-guard 16/16. Guard `47386f43…` →
**`dde0bbc6…`**.

## Rev 5 (2026-09-13) — U8 residual closed (empty declaration fails)

Alice's applied-check (`ALICE-CROSSCOPY-U8-APPLIED-CHECK.md`) found rev 4 fired
only on `shared and not trees_rel`, so an **empty/comment-only** declaration
still fell back to `DEFAULT_TREES`+`DEFAULT_FILES` with discovery skipped and
rc 0. Assay's validated `crosscopy-u8-v2.diff` (`d5438b6a…`, guarded
`f8bd89a9…`) is applied: after a successful read, `if not trees_rel:` is an
instrument failure for **any** declaration with no `tree:` lines; explicit
`--trees` still bypasses. Independently reproduced on the staged layout —
comment-only declaration → rc 1 with the instrument line (v1 was silent),
shared-only → rc 1, full declaration → 0 findings rc 0, `--trees` bypass → rc 0,
`--self-test` PASS. Live census unchanged; meta-guard 16/16. Guard `dde0bbc6…` →
**`f8bd89a9…`**.
