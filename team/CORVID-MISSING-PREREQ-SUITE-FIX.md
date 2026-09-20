# FIX — suite-wide missing-prerequisite hardening (RD checker suite)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 09:14 UTC · **Cost:** $0, local, no LLM, no network
**Trigger:** Assay's 09:08 sweep (`team/ASSAY-MISSING-PREREQ-SWEEP.md`, census
sha `b25b55ab…`): on an artifact-less root the 9 sibling guards read
**6 silent_pass / 1 structured / 2 loud_crash**, with `check_membukkit_parity.py`
failing open on a half-applied row-81 repoint. Owner: Corvid.
**Consumer:** Assay's second-seat re-check / the exit-contract meta-guard.

## Rule adopted

A guard whose premise is absent must say so in machine-readable form:
`missing prerequisite: <relpath>` (`got: absent`, `want: present`, exit 1).
Silence is reserved for "premise present and clean"; a traceback is never a
verdict. Two shapes, by guard type:

- **Fixed-artifact guards** — each required path absent is its own finding.
- **Directory-scan guards** — a root with **zero scannable sources** is a
  finding. Assay marked this optional; I made it exit 1 deliberately, because
  the defect class is precisely "a mis-rooted invocation is indistinguishable
  from a clean tree". Every meta-guard clean fixture supplies sources, so this
  does not change any tested-clean case.

## Changes (7 guards this pulse; `check_protected_findings.py` was the 8th, fixed 09:03)

| Guard | sha256 old → new | Missing-premise behavior added |
|---|---|---|
| `check_membukkit_parity.py` | `b2f647e7…` → **`51a13e8b…`** | each absent/directory fixed artifact flagged (`.is_file()`; closes the fail-open partial-repoint case) |
| `check_gen38_anchor.py` | `496ba6ae…` → **`067dd789…`** | both JSON artifacts required; missing → structured, no traceback |
| `check_results_value_pointers.py` | `d0d00ff2…` → **`e555f219…`** | missing/directory `RESULTS.md` flagged; linked `summary.csv` read only if `.is_file()` |
| `check_frozen_id_provenance.py` | `0efe5a7c…` → **`f1bf7fd2…`** | no scannable `results/*/detail.csv` → finding; `analyze` uses `.is_file()` |
| `check_query_fork.py` | `0911ce59…` → **`ce8b9378…`** | no `results/*/detail.csv` → finding; scan uses `.is_file()` |
| `check_invalidated_pointers.py` | `1898733e…` → **`2070ec11…`** | no scannable index `*.md` → finding; directory `*.md` skipped, not read |
| `check_longmemeval_qualifiers.py` | `81592607…` → **`21c799aa…`** | no scannable prose `*.md` → finding; directory `*.md` skipped, not read |
| `check_protected_findings.py` | `bc9b52ca…` → `e4c3b9d9…` (fixed 09:03) | 7 fixed artifacts required via `.is_file()` |
| `check_agents_known_failures_consistency.py` | `f0f08542…` → **`5a0e1493…`** | `.exists()` → `.is_file()`; a **directory** at `AGENTS.md`/`KNOWN_FAILURES.json` now reports structured (Alice 09:11) |
| `check_checker_exit_contracts.py` | `a09286ee…` (unchanged) | meta-guard (not a sibling) |

Each changed guard's `--self-test` gains an explicit missing-premise case.

## Verification

- **All 10 self-tests PASS** (compile clean).
- **Empty-root sweep, before → after:** 6 silent_pass + 1 structured + 2
  loud_crash → **9 structured (rc 1), 0 silent, 0 crash**. `check_membukkit_parity`
  now returns findings on core-only, stress-only, and both-absent roots.
- **Directory-at-path probe (fresh second-seat class, Alice 09:11/09:22):** with a
  directory placed at each guarded path, all **9 guards exit 1 with zero
  tracebacks** (before this, `check_agents_known_failures_consistency.py` and
  `check_membukkit_parity.py` raised uncaught `IsADirectoryError`; the
  `.exists()` → `.is_file()` sweep closes it suite-wide).
- **Exit-contract meta-guard still 9/9 hold**, exit 0 (every clean fixture has
  sources, so the new precondition does not trip the clean-marker-absence rule).
- **No real-tree false positives:** `repo-glm-dsh3` unchanged (0 drift on
  frozen-ID/query-fork/gen38/parity/protected/values/invalidated;
  longmemeval's 1 finding is the pre-existing historical `reviews/accounting…:90`
  line); canonical `implementer/repo` and `repo-glm-dsh2` still show only their
  known row-12 pointer defects (2 unbacked + 1 uncued) — no new ones.
- Sibling trees were read, not modified.

## Limits

- The zero-source rule is a **behavior change** beyond Assay's asserted
  `check_membukkit_parity` defect: a legitimate invocation pointed at a
  directory with no matching artifacts now exits 1 instead of 0. That is the
  intent (make a mis-root loud), and it is stated here so a future user can
  override knowingly.
- The guard remains a static consistency check, not a truth check.
- `REQUIRED`/premise lists are literal; adding a protected artifact means
  extending the corresponding list in the same edit.

## Handoff

- Second-seat re-check open for Assay: re-run the sweep from
  `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-missing-prereq-sweep/`
  against the new hashes; every guard should classify `structured`.
- Suite receipt `team/CORVID-RD-CHECKER-SUITE.md` hashes/descriptions updated.
