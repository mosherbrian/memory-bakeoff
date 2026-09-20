# GUARD — orphan evidence (completed runs no Markdown cites) + first census

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 · **Cost:** $0, local, read-only
**Trigger:** coverage-map gap **U1** (Muse batch-4 ACCEPT 4.3): a contradicting
or invalidated run can sit in `results/` uncited, and the existing checkers only
go citation → artifact, never artifact → citation.
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_orphan_evidence.py`
sha256 `5ebef46f0e8df28fe7e5f3c17d8e8e5f3f636c76646a77a44064238d017f00d1`
(rev 3; rev 2 `b27e337c…`, rev 1 `908c008a…`).

## What it does

For a results root, enumerate `results/<dir>` holding a **completed measurement**
(`summary.csv` or `run.json`), then check whether the directory name appears in
any Markdown file under the declared `--cite` roots. Self-citation is excluded:
Markdown **inside** a `results/` subtree never counts as a citation of the run it
describes. Citations may be links or plain mentions.

- **Advisory by default (exit 0)** because replicate/probe dirs are legitimately
  uncited; `--fail` turns it into a gate; `--allowlist FILE` (one dir name per
  line, `#` comments) records intentional exceptions; `--since-days N` is a grace
  window for fresh runs.
- Missing `results/` → structured `missing prerequisite` (exit 1); unreadable
  citation corpus → structured.

## First census (`repo-glm-dsh3`; cite roots `.` + `team/`)

**61 of 106 completed runs are uncited by any Markdown outside `results/`.**

*Self-referential caveat:* a plain mention suppresses a dir, so the count drops
as docs (including this one) name examples — the immediately following run read
**52/106**. Treat the numbers as snapshots of an advisory census, not a fixed
denominator.

| Category | Count | Examples |
|---|---|---|
| replicate runs (`-r2…-r9` or `_r2/_r3`) | ~49 | `agentmemory_raw_product_gen13_core-r2`, `perseus_vault_gen21_core_r3` |
| budget/threshold sweeps | 6 | `membukkit_budget_0.3/0.5/0.75/1.0`, `membukkit_hybrid_0.3`, `membukkit_none_1.0` |
| control/probe/calibration | 4 | `membukkit_intended_gen41_replication_control_cpu_core-r1` |
| distinct runs worth a citation decision | 2 | `core4`, `current_full_core_claudemem` / `current_full_stress_claudemem`, `stress4504` |

The shape (`61/106`, dominated by deliberately-uncited replicates) is exactly why
the default is a census: an "every completed run must be cited" gate would fire
on legitimate replication. The finding of record is the **scale of the hidden-run
surface** and the allowlist mechanism to reduce it; the two `current_full_*_claudemem`
and `core4` dirs are the first candidates for an explicit disposition.

## Verification

- `--self-test` **PASS**: an uncited completed run is found; self-citation is
  excluded; an allowlist and a plain mention each suppress; a dir without a
  completed artifact is ignored.
- Real census reproduced independently with `grep -rl <name>` over the tree +
  `team/` excluding `results/`: the sampled orphans are genuinely uncited.

## Limits

- The match is now a **token/path-boundary** match (`(?<![\w-])name(?![\w-])`),
  so `core4` is not "cited" by `core40`/`hardcore4fun`, while a `results/core4`
  path link and a bare `` `core4` `` mention both count. A differently-spelled
  path that is not a boundary-delimited mention still would not count; that is
  the conservative direction (over-reports orphans at worst).
- It says nothing about whether a cited run is *valid*; that is guards 1–3.
- The allowlist is a manual artifact; until it exists the guard should not gate
  P2/P3 (hence advisory default). An explicit `--allowlist` path that is missing
  or unreadable is now a structured prerequisite error, not a silent empty set.

## Rev 2 (2026-09-13) — Alice's false-negative finding + allowlist silence

Alice's second-seat check (`team/ALICE-ORPHAN-EVIDENCE-GUARD-SECONDCHECK.md`, sha
`5cc983f4…`) PASSed the build and found two issues:

1. **Substring match was a false-negative in the guard's primary direction.**
   `d.name in corpus` suppressed `results/core4` when the prose said *"core40 and
   hardcore4fun"*. Fixed with a boundary regex; a synthetic longer-word case is
   in the self-test. The real census rose **52 → 54** as false suppressions
   cleared.
2. **A missing `--allowlist` path was silently dropped** (empty set), so
   `--fail` would fire on intentional exceptions. Now an explicit `--missing`
   allowlist reports `missing prerequisite` (exit 1), and an unreadable one
   reports `unreadable prerequisite`.

Also corrected the note's earlier Limits claim that the substring form
"over-reports": it could under-report. sha `908c008a…` → **`b27e337c…`**.

## Rev 3 (2026-09-13) — replicate-aware reporting (census actionable, nothing hidden)

The rev-2 census of 54 orphans was one undifferentiated list. Rev 3 adds a
`classify()` layer used by `main`: an uncited run whose directory family
(trailing `-rN`/`_rN` removed) has a **cited sibling** is labeled
`[ORPHAN-REPLICA]`; the rest are `[ORPHAN] distinct`. **Nothing is suppressed** —
the whole list still prints; the label only says whether the family is already
represented by a cited run.

Current census (`repo-glm-dsh3`, cite `.` + `team/`):
**54 uncited = 25 `replica_of_cited` + 29 `distinct`.** The 25 replicas are
already represented by a cited sibling; the 29 distinct orphans (e.g. the
`perseus_vault_gen21_*` family, `core4`, `current_full_{core,stress}_claudemem`,
`stress4504`) are whole uncited families and are the actual disposition queue.
The self-test now asserts the replica-vs-distinct split.

This is reporting, not an allowlist: no run is excused, so the guard stays
advisory (exit 0) and `--fail` still gates on the full set. sha `b27e337c…` →
**`5ebef46f…`**.
