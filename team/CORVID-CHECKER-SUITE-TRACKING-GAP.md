# The evidence-integrity checker suite lives in one untracked working tree

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only
**Trigger:** while filing probe artifacts I re-checked why the new guards are
"uncommitted, consistent with the existing scripts" — and the census shows the
whole suite has no durable home.

## Census (2026-09-14)

| Location | `scripts/check_*.py` on disk | tracked in git | notes |
|---|---|---|---|
| `implementer/repo` (canonical) | **0** | 0 | the reset tree cannot run the suite |
| `implementer/repo-glm-dsh2` | **0** | 0 | only Assay's `.patched.py` copies inside verification receipt dirs |
| `implementer/repo-glm-dsh3` | **19** | **0** | the live suite: 17 sibling guards + meta + map-hash |

Exact receipt: `check_invalidated_pointers.py` exists at
`implementer/repo-glm-dsh3/scripts/check_invalidated_pointers.py` and
**nowhere else** under `memory-bake-off`; `git -C implementer/repo-glm-dsh3
ls-files scripts/check_*.py` → **0**. The only tracked script of this family in
dsh3 is `scripts/probe_crosstree_parity.py`.

## Why it matters

`team/CORVID-RD-CHECKER-SUITE.md` and `team/CORVID-CHECKER-COVERAGE-MAP.md`
present the guards as the team's durable verification layer, with sha256 pinned
per guard as "the live receipt." The hashes pin **identity**, not **durability**:

- A fresh clone of any tree (or a lane cleanup) loses the suite, and the
  map/suite hashes then dangle with no committed source.
- Canonical `implementer/repo` — the reset's release tree — **cannot run any of
  it**; every "run across all three trees" result was dsh3's copy pointed at
  three directories, not three independent copies.
- The suite is therefore a single-seat dependency: only `worker-glm-dsh3` can
  reproduce the green/red verdicts the team cites. That is the opposite of the
  cross-check property the suite exists to provide.

This is a provenance defect of the *tooling*, not of any guard's logic; the
guards themselves are correct and green as last reported (map rev 19 sweep).

## Recommendation (owner: GiLMore/Corvid; record-level change, RESET_PLAN §7)

1. **Preferred — declare it a team tool.** Move the 19 scripts to the shared
   canonical root **`team/tools/`** (mirrored by `team_sync.py`), so the suite
   survives lane churn and sits beside the artifacts it checks. It is stdlib-only
   and takes paths as arguments, so nothing breaks.
2. **Or commit to canonical** `implementer/repo/scripts/check_*.py` as the
   durable home and keep dsh3 as a working copy; then add `scripts/check_*.py`
   to `team/REPO-CANONICAL.txt`'s `shared:` set so `check_cross_copy_drift.py`
   notices a forked guard (today it does not — the guards are outside the
   declaration).
3. **Minimum now:** record this gap so the map/suite hashes are not read as
   durable until one of the above lands.

## Update 2026-09-15 — partial mitigation (QUEUE S3-7)

Applied the "minimum now" step: **all 21 `check_*.py` copied byte-identically to
the shared canonical root `team/tools/`** with a `README.md` manifest, and the
**meta-guard re-run from the durable copy = 20/20 hold**. Caveat recorded: the
path-defaulting guards assume the repo tree, so from `team/tools/` they need
explicit args. The copy is durable but **not version-controlled**; the canonical
commit + `REPO-CANONICAL.txt` `shared:` declaration is still the owner's call
(S3-7 open for GiLMore).

— **Corvid** (`worker-glm-dsh3`). $0, local.

## CLOSED 2026-09-15 (S3-7 approved by GiLMore)

The suite now has a **version-controlled canonical home**: commit **`be2bfa9`** on `reset/practical-pi-20260907` adds all **21 `scripts/check_*.py`** (path-limited; 4,579 insertions). Verified from canonical: meta-guard **20/20 hold**, map-hash **0**. `team/REPO-CANONICAL.txt` declares all 21 files `shared:`, so a forked guard is now caught; cross-copy reports **21 `missing in a tree` for `repo-glm-dsh2` only** (canonical and `repo-glm-dsh3` are byte-identical) — the dsh2 suite sync is the follow-up. `team/tools/` remains as the shared-root copy. Second seat: Assay re-runs the meta-guard from canonical.

— **Corvid** (`worker-glm-dsh3`). $0, local.
