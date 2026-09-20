# Assay second-seat — P2-entry evidence-integrity gate receipt

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, read-only
**Subject:** `team/CORVID-P2-ENTRY-GATE-RECEIPT.md` (Corvid), per its handoff
("Assay/Alice second-seat").
**Verdict: PASS / AGREE on every claim** — HEADs, the `repo-glm-dsh3` entry-gate
states, and the cross-tree result subset all reproduce exactly. No deviations.

## HEADs — match

| tree | HEAD | receipt |
|---|---|---|
| `repo-glm-dsh3` | `399337b` | ✓ |
| canonical `implementer/repo` | `ef67ec7` | ✓ |
| `repo-glm-dsh2` | `86709b3` | ✓ |

## `repo-glm-dsh3` entry gate — reproduces

14/15 green; `check_agents_known_failures_consistency` rc 1 (one false-pin
finding, expected red); `check_orphan_evidence` advisory **106 scanned / 54
uncited = 25 replica + 29 distinct**, rc 0; map-hash **0 findings**; meta **9/9
hold**. Matches the receipt.

## Cross-tree result subset — reproduces exactly

| guard | canonical `ef67ec7` | `repo-glm-dsh2` `86709b3` |
|---|---|---|
| invalidated pointers | rc 0 (uncued 0) | **rc 1 — uncued 1, dangling 0** |
| results-value pointers | rc 0 (0 findings) | **rc 1 — 2 unbacked rows (81, 82)** |
| frozen-ID provenance | rc 0 (102 dirs, 24,169 ids, all canonical) | rc 0 (same) |
| query-fork | rc 0 (26 ids, 0 forked) | rc 0 (same) |
| required metrics | rc 0 (102 summaries) | rc 0 (102 summaries) |
| AGENTS baseline | **rc 1 — 3 findings (2 stale totals + false pin)** | **rc 1 — 1 (false pin)** |

The canonical **status change is real and committed**: `RESULTS.md`'s pointer
repair is commit `9b5a829` (ancestor of `ef67ec7`), so the green result subset
does not depend on uncommitted work. The `do not cite from repo-glm-dsh2 until
its two pointer fixes land` call is supported (uncued 1 + unbacked 2, closed by
`scripts/apply-pointer-fixes.sh`).

## Observation (not a defect in the receipt)

Canonical's worktree is dirty in `deploy/r2-habit-20260912/r2h_deploy.py` (the
known uncommitted R2H REV-2 change) plus two untracked scratch files
(`MANIFEST.md`, `canonical-repo-checks.txt`). None of these touches the result
subset or the guards run, and RESULTS.md is committed, so the gate verdict stands
on `ef67ec7` as stated. Worth naming only so "canonical green" is not misread as
"canonical worktree clean".

## Limits

- Static guard runs on the current worktrees; I did not re-derive the AGENTS
  baseline contents or the orphan dispositions.
- `repo-glm-dsh2` is my own active workspace (99 dirty paths); this is a
  read-only check, no tree modified.

## Receipts

- Receipt: `team/CORVID-P2-ENTRY-GATE-RECEIPT.md`
- Runs: 6 guards × 2 sibling trees + 4 entry-gate states on `repo-glm-dsh3`;
  outputs above. Commits `399337b` / `ef67ec7` / `86709b3`; RESULTS.md fix
  `9b5a829`.

— **Assay** (`worker-glm-dsh2`). No tree modified.
