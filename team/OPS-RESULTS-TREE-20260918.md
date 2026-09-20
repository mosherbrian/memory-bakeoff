# Two results trees on this machine, zero contradictions — pick the canonical one

**Filed by:** cairn/operator (Claude session), 2026-09-18 16:4x PDT
**For:** corvid-dsh, who ranks `BACKLOG-NEXT.md` — this is evidence, not a
candidate and not a ranking. Rank it, fold it into another row, or reject it.
**Cost to produce:** $0, local reads only. No tree was modified.

## Why this exists

The S10-3 evaluator canary reports **21 guard failures on the live tree**, and
that number was escalated with per-guard triage assigned to cairn/Brian. Most
of it is not 21 defects. Eight failures are the same sentence:

    missing prerequisite: results/<something>

`results/` does not exist under `team/`, which is what the guards resolve
against. It is **a missing pointer, not missing data** — and the data is on
this machine twice.

## What is actually here

| tree | size | entries | git HEAD |
|---|---|---|---|
| `~/pilot-gen45/results` | 318 MB | 236 | `9dfea2c` Materialise the MemConflict checkout… |
| `~/memory-bake-off/implementer/repo/results` | 147 MB | 237 | `be2bfa9` Add evidence-integrity checker suite… |

A full recursive comparison of the two (`diff -rq`, every file, both
directions):

    content differences .............. 0
    only in pilot-gen45 .............. 49   (24 stdout.txt, 24 history.ndjson,
                                             1 raw_capture — all raw run capture
                                             under pi_state_control_gen45 and
                                             pi_model_assisted_evidence_gen58)
    only in implementer/repo ......... 1    (results/p2_entry_20260913)

**Not one file disagrees.** Neither tree contradicts the other; each is a
superset of the other in a different place. pilot-gen45 carries raw per-run
capture the repo tree drops; the repo tree carries one entry pilot-gen45 does
not.

Every prerequisite the failing guards name is present in both and byte-identical
where checked directly (`memconflict_gen38_full_release/scientific.json`,
`claude_mem_compare_core/summary.csv`,
`agentmemory_raw_product_gen13_stress-r1/lifecycle.json`).

## What was considered and rejected

**Copying `results/` from the Mac.** Brian asked whether we should. No: the Mac
copy at `/Users/bmosher/source/repos/memory-bakeoff` is stale at Gen114 — the
live repo has been on this Linux box since 2026-09-07 — and this disk is at
**98%, 17 GB free**. A third copy of a tree that already exists twice is how
copies drift and nobody can say which is canonical.

**Symlinking `team/results` at one of them, by this operator.** Rejected as not
mine to decide. Pointing the guards at the wrong tree would make them PASS on
the wrong evidence, which is worse than failing: a green check standing on the
wrong data is the failure class this project exists to study. Which results
tree is canonical is a research-integrity call.

## The decision, stated so it can be made in one read

Neither tree is complete on its own, and they do not conflict. So the choice is
between:

1. **Point at `implementer/repo/results`** — the tree the repo itself carries,
   already referenced by `team/PHASE2_ROADMAP.md` (a symlink into
   `implementer/repo/research/`). Loses the 49 raw-capture files unless they are
   brought across.
2. **Point at `pilot-gen45/results`** — the fuller raw record. Loses
   `p2_entry_20260913` unless brought across.
3. **Reconcile first, then point.** 50 files, no conflicts, so a union is
   mechanical rather than a judgement — but it makes a third tree unless it is
   merged into one of the two.

Whichever is chosen, the guards need `results/` reachable from `team/` for the
eight `missing prerequisite` failures to clear. The remaining failures are
separate and NOT this: `check_no_pipes_in_seats` names a literal pipe in row
S10-1G (real board defect), `check_r2h_rater_blind` reports `[EXPOSED]` against
session `7dfbfe83-1789253983` (corvid's own — a blind-rating integrity matter,
not an ops one), and `check_checker_exit_contracts` reports
`check_answer_provenance` has no control fixture (this operator's, known).

## What is NOT claimed here

That either tree is correct, complete, or the one the published findings were
computed from. Only that they are byte-identical wherever both have the file,
and that the guards currently see neither.
