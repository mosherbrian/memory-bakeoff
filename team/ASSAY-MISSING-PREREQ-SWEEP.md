# Assay — missing-prerequisite sweep of the RD checker suite

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, offline, synthetic/empty roots only
**Motivation:** my 08:55 pulse found `check_protected_findings.py` crashes on a
deleted source; `check_agents_known_failures_consistency.py` was just fixed to
report `missing prerequisite` structurally. The exit-contract meta-guard tests
each guard on clean and dirty fixtures — **not** on a root where the guarded
artifacts are simply absent (the mis-rooted / partially-deployed invocation).
This sweep asks that question for the whole suite.

**Headline:** across the 9 sibling guards, run on an empty root with none of the
guarded artifacts — **6 silently pass (rc 0)**, **1 reports structurally**, and
**2 crash with an uncaught traceback**. The sharpest is
`check_membukkit_parity.py`: present artifacts are checked with real power, but
**one or both absent files read as "0 findings, clean"**.

## Census — each guard's real CLI on an empty temp root

| Guard (`repo-glm-dsh3/scripts/`) | sha256 | empty-root rc | class |
|---|---|---|---|
| `check_agents_known_failures_consistency.py` | `f0f08542…` | 1 | **structured** (`missing prerequisite: …`) |
| `check_frozen_id_provenance.py` | `0efe5a7c…` | 0 | silent_pass¹ |
| `check_gen38_anchor.py` | `496ba6ae…` | 1 | **loud_crash** (traceback, no verdict) |
| `check_invalidated_pointers.py` | `1898733e…` | 0 | silent_pass¹ |
| `check_longmemeval_qualifiers.py` | `81592607…` | 0 | silent_pass¹ |
| `check_membukkit_parity.py` | `b2f647e7…` | 0 | **silent_pass² (defect)** |
| `check_protected_findings.py` | `bc9b52ca…` | 1 | **loud_crash** (traceback, no verdict) |
| `check_query_fork.py` | `0911ce59…` | 0 | silent_pass¹ |
| `check_results_value_pointers.py` | `d0d00ff2…` | 0 | silent_pass¹ |

¹ For directory-scan guards, an empty root can be a *vacuous truth* ("no data,
no findings") — defensible, but note it: a wrong-root invocation is
indistinguishable from a clean tree. Named boundary, not asserted defect.
² For fixed-artifact guards, absence is a real failure the guard exists to
catch — see below.

`self_test` passed for every guard (rc 0), so these are missing-input paths the
self-tests do not cover.

## Focused defect — `check_membukkit_parity.py` fails open

`scan()` only calls `check_file(p)` **if `p.exists()`**, and `check()` inside a
present file requires both providers. A missing file is skipped with no finding.

| Root state | rc | stdout verdict | expected |
|---|---:|---|---|
| both files present, equal | 0 | `findings: 0` | 0 ✓ |
| **core only, stress absent** | **0** | **`findings: 0`** | **findings ≥ 1 ✗** |
| **stress only, core absent** | **0** | **`findings: 0`** | **findings ≥ 1 ✗** |
| both files present, stress diverges | 1 | `{'metric': 'hit@5', 'membukkit': 0.4, 'dense_lsa': 0.5833}` | 1 ✓ (power confirmed) |
| **both absent** | **0** | **`findings: 0`** | **findings ≥ 1 ✗** |

So the guard has genuine detection power when the two repointed artifacts exist,
but it cannot report their absence: a mis-rooted run, or a tree where the row-81
repoint was only half applied (`current_full_stress4505` present,
`current_full_core5` absent, or vice versa), reads **green**. That is the same
"This check cannot report its own failure" class the team has now found four
times this cycle (AGENTS guard, S6 INCONCLUSIVE, my protected-findings crash,
this).

## Recommendation (owner: Corvid; suite-level, no metric semantics change)

Add a shared precondition step, in the same shape as the AGENTS guard fix:
a guard whose premise is a **fixed artifact list** must treat a missing path as
a structured finding (`missing prerequisite: <relpath>`, exit 1), not a skip and
not a traceback. Priority order:

1. `check_membukkit_parity.py` — **silent pass** on partial trees (highest: it
   guards a protected finding and the exact artifacts the row-81/82 pointer
   defect touched).
2. `check_gen38_anchor.py`, `check_protected_findings.py` — loud but
   unstructured; route to the same `missing prerequisite` verdict.
3. Directory-scan guards — optional; if desired, warn when a root yields zero
   scannable sources so a mis-root is visible.

Not applied: the guards are Corvid's and any change moves their hashes. This is
a finding + proposal, consistent with the one-writer-per-tree rule.

## Limits

- Empty/synthetic roots only; no live data, no tree moved, no guard edited.
- A silent `0` is not by itself wrong for scan guards (see ¹); the asserted
  defect is scoped to `check_membukkit_parity.py`, with the others named as
  boundaries with their classification.
- The sweep is a census, not a gate (exits 0 by design).

## Receipts

- Sweep: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-missing-prereq-sweep/check_cli_missing_prereq_sweep.py`
  sha256 `d307556d3e211c68c194a0244d7ca6eb80f7abec0292bdf7c86705d29424e3b5`
- Census result: `.../sweep.json` sha256 `b25b55abd2b261ea1ec10b5a23e35df7edea01370a20451910672b4b62a5ef0f`
- Membukkit focused probe: `.../membukkit_missing_probe.json` sha256 `d008a864a661e262e1339ab19c93befd937f1a7c9a528d4e8bf63018d84cb310`
  (guard sha `b2f647e7a639dc167ba0238aeaf251783ec086f6109520fe52f5b474cf3a7657`, matches the suite receipt)
- Re-run: `python3 check_cli_missing_prereq_sweep.py`

— **Assay** (`worker-glm-dsh2`). No tree modified; all guards unchanged.
