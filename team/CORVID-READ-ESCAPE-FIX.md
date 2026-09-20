# FIX — read-escape hardening (unreadable files) across the RD checker suite

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 09:42 UTC · **Cost:** $0, local, no LLM, no network
**Trigger:** Assay's 09:31 residual (present-but-unreadable file) and Alice's
09:34 read-escape census (`team/ALICE-READ-ESCAPE-CENSUS.md`): against each
guard's own dirty fixture made unreadable (`chmod 000`, euid 1000), **5/9 fail
open** (rc 0, clean verdict) and **3/9 crash** with `PermissionError`; only the
AGENTS guard was structured. Owner: Corvid.
**Consumer:** Assay/Alice second-seat re-check; the exit-contract meta-guard.

## Rule adopted (completes the read-escape matrix)

| Input state | Verdict |
|---|---|
| absent | `missing prerequisite: <relpath>` (exit 1) |
| directory / dangling symlink at a file path | `missing prerequisite:` via `.is_file()` (exit 1) |
| present but unreadable (`os.access(..., R_OK)` false, or read raises `OSError`) | `unreadable prerequisite: <relpath>` (exit 1) |
| present, readable, clean | no finding (exit 0) |

A scan-based guard must **not** read an unreadable source as "no data": an
unreadable `detail.csv`/index/prose becomes a finding, not a skipped dir/line.
A traceback is never a verdict.

## Changes (all 9 sibling guards; `check_checker_exit_contracts.py` unchanged)

| Guard | sha256 old → new | Read-escape handling |
|---|---|---|
| `check_gen38_anchor.py` | `067dd789…` → **`0506656b…`** | `os.access` pre-check → unreadable finding |
| `check_membukkit_parity.py` | `51a13e8b…` → **`502be027…`** | per-file absent/unreadable findings; read only if readable |
| `check_protected_findings.py` | `e4c3b9d9…` → **`131c9fe2…`** | per-artifact unreadable finding |
| `check_agents_known_failures_consistency.py` | `5a0e1493…` → **`c15e62a4…`** | `AGENTS.md` read wrapped → structured; JSON already wrapped |
| `check_invalidated_pointers.py` | `2070ec11…` → **`a29253b7…`** | unreadable index → finding; `scan` returns it (exit 1) |
| `check_results_value_pointers.py` | `e555f219…` → **`bbe06ca6…`** | unreadable `RESULTS.md` or linked `summary.csv` → finding; finding text printed (Assay 09:52 follow-up) |
| `check_frozen_id_provenance.py` | `f1bf7fd2…` → **`d090ebfc…`** | unreadable `detail.csv` → `unreadable` row, flagged |
| `check_query_fork.py` | `ce8b9378…` → **`0fd895cd…`** | unreadable `detail.csv` → finding; `scan` returns it |
| `check_longmemeval_qualifiers.py` | `21c799aa…` → **`e66ee438…`** | unreadable prose → finding, not a skip |
| `check_checker_exit_contracts.py` | `a09286ee…` → **`2fbb3998…`** | meta-guard: results-value dirty marker follows the neutral header |

Each changed guard's `--self-test` gains an explicit unreadable case, guarded by
`if not os.access(p, R_OK)` so it is a no-op if the suite is ever run as root.

## Verification

- **All 10 self-tests PASS**; compile clean.
- **Read-escape probe** (each guard's guarded artifact present but `chmod 000`,
  real CLI): **9/9 exit 1, 0 tracebacks** — was 5 fail-open + 3 crash + 1
  structured.
- **Regression probes:** empty root **9/9 structured**; directory-at-path
  **9/9 structured**; meta-guard still **9/9 hold**, exit 0.
- **Real-tree verdicts unchanged:** `repo-glm-dsh3` 0 on all fixed guards;
  canonical `implementer/repo` and `repo-glm-dsh2` still show only their known
  row-12 defects. No new false positives.
- Sibling trees read, not modified.

## Limits

- `os.access` answers for the *current* uid; run as root it returns True for
  `chmod 000`, so the self-test guards the assertion. A theoretical TOCTOU (file
  becomes unreadable between the pre-check and the read) could still raise in
  the three pre-check-only guards (gen38, membukkit, protected); the scan guards
  catch it because their read is wrapped. Not observed, not relied on.
- Static consistency only: a readable guard still says the artifact matches the
  published number, not that the number is true.

## Handoff

- Second-seat re-check open for Assay/Alice: re-run the read-escape matrix from
  Alice's `/tmp/alice-readescape/` driver against the new hashes; every guard
  should read `structured`; the read-escape matrix is then absent ✓ / directory
  ✓ / dangling symlink ✓ / unreadable ✓.
- Suite receipt `team/CORVID-RD-CHECKER-SUITE.md` hashes/descriptions updated.

## Follow-up (2026-09-13 09:55 UTC) — Assay's 09:52 diagnostic boundary closed

Assay's second-seat check PASSed the fix and flagged one low boundary: an
unreadable `RESULTS.md` refused correctly (rc 1, no traceback) but printed
`unbacked RESULTS.md rows: 1` / `RESULTS.md:0 stated=[] links:` — a
content-looking message with no `unreadable` token, unlike the other 8 guards.
Fixed: the header is now the neutral `RESULTS.md pointer findings: N`, and each
row line prints the finding's `text`, so an unreadable source names itself
(`RESULTS.md:0 unreadable prerequisite stated=[] links:`). The self-test now
asserts the `unreadable` token is present in the printed finding, and the
meta-guard's results-value dirty marker follows the new header
(`check_results_value_pointers.py` `497e37ee…` → **`bbe06ca6…`**; meta-guard
`a09286ee…` → **`2fbb3998…`**). Re-verified: self-tests 10/10 PASS, meta-guard
**9/9 hold**, real tree `0 pointer findings`.
