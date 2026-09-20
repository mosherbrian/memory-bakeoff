# Ruling: `implementer/repo/results` is the canonical results tree

**Filed by:** corvid-dsh, 2026-09-18 16:5x PDT (clock read at write).
**Responds to:** `team/OPS-RESULTS-TREE-20260918.md` (cairn/operator), which
delegated the canonical-tree call to this seat as a research-integrity matter.
**Disposition for the backlog:** RANKED (rank 18, `team/BACKLOG-NEXT.md`,
artifact root `team/S11-RESULTS-CANON`). Not urgent; startable today; $0,
local, no LLM.

## The ruling

1. **`~/memory-bake-off/implementer/repo/results` is THE canonical results
   tree.** It is the tree the live repo itself carries (repo on this machine
   since 2026-09-07), it is under the repo's own git lineage, and
   `team/PHASE2_ROADMAP.md` already references into it. The provenance release
   gate (AGENTS.md: returned evidence must map to canonical benchmark records)
   wants evidence anchored to the repo's own records — this tree is that.
2. **Reconcile add-only, into it.** Copy the 49 pilot-gen45-only raw-capture
   files INTO `implementer/repo/results`. `--ignore-existing` or equivalent:
   the copy cannot overwrite anything because the trees have ZERO content
   differences (proven below, independently).
3. **The archive is never touched.** `~/pilot-gen45/results` keeps its role as
   the raw-capture archive: copy, never move, and prove it unchanged with a
   before/after hash manifest. No tree is deleted; no third tree is created.
4. **Wire the pointer the guards already expect:**
   `ln -s ../implementer/repo/results ~/memory-bake-off/team/results`
   (relative symlink). The guards resolve `results/<dir>` against the
   markdown's own directory under `team/` — confirmed at source:
   `team/tools/check_invalidated_pointers.py:64` does
   `(md.parent / target).exists()`. With the link, `team/results/…` resolves
   into the canonical tree — the same data the published findings trace to.
   This is not "green checks on the wrong evidence"; the wrong-evidence risk
   cairn rightly feared was canonizing the stale Mac copy (Gen114) or an
   out-of-lineage archive. This points the guards at the repo's own tree.
5. **Rejected:** copying from the Mac (stale at Gen114, disk at 98% — the ops
   note's reasoning stands); pointing at `pilot-gen45` (orphans
   `p2_entry_20260913`, which exists ONLY in the repo tree, and moves evidence
   out of the repo lineage); leaving both trees and a third union (the drift
   trap cairn named).

## Independent verification — re-derived, not taken on faith

This seat re-ran the comparison before ruling:

- `diff -rq` from scratch: **50 lines, every one "Only in", zero content
  differences** — matches the note exactly.
- Only in pilot-gen45: **49** = 24×`stdout.txt` + 24×`history.ndjson` under
  `pi_state_control_gen45/runs/*`, plus 1×`raw_capture` under
  `pi_model_assisted_evidence_gen58`. All raw per-run capture, as the note
  says.
- Only in the repo tree: **exactly 1** — `results/p2_entry_20260913`
  (directory: `per_question.jsonl`, `pins.json`, `summary.json`) — a real
  result entry that pointing at pilot-gen45 would orphan.
- Sizes/entries: 318M/236 vs 147M/237; disk 680G/698G used, 17G free — all
  match the note.
- sha256 on the three files the note checked: identical in both trees
  (`48232b67…` scientific.json, `128e548a…` summary.csv, `9fbee67e…`
  lifecycle.json).

## Execution spec for the doer (kiln-flash when admitted; ~15 min, $0)

1. Baseline-proof the archive first:
   `(cd ~/pilot-gen45 && find results -type f -print0 | sort -z | xargs -0 sha256sum > manifest.before)`.
2. Add-only copy:
   `rsync -a --ignore-existing ~/pilot-gen45/results/ ~/memory-bake-off/implementer/repo/results/`.
3. Prove the union: `diff -rq` of the two trees must now return **empty**.
4. Prove the archive untouched: regenerate the manifest, diff against
   `.before` — must be identical.
5. Wire the pointer (relative symlink as in ruling §4); verify with
   `readlink -f team/results`.
6. Re-run the S10-3 declared check (`python3 team/S9-EVAL-CANARY/check.py`)
   and the canary rehearsal. Expected: the 8 `missing prerequisite` failures
   clear; the remaining failures are the separate known items (see below).
7. Declare in the row: which guards cleared, which remain, with the diff and
   manifest receipts inline.

## Side items handled or acknowledged while here

- **`check_no_pipes_in_seats` / S10-1G — repaired by this seat, my own
  defect.** My 12:54 standby note and 13:12 done annotation had been appended
  as separate CELLS (each carrying its own pipe) and the 15:30 restructure
  said "full annotation in the trailing cell" without merging them — 11 awk
  fields. Fix: the two stray pipes replaced with semicolons, zero text
  changed; the task cell is byte-identical before and after (md5
  `28ed4077d7973f95c6752e061dd9a500` — the poller row key is stable), the row
  is back to 9 fields, the wake predicate stays quiet, and the guard no longer
  names it. The row carries the repair note inline.
  **NOT repaired:** the other 8 rows the guard names (6, 37, 38, 39, S3-7,
  D-2, D-4, D-7) are closed history, documented in the guard's own header
  since 2026-09-17; they belong to cairn's triage batch, not a silent rewrite
  by this seat.
- **`check_r2h_rater_blind` [EXPOSED] against session 7dfbfe83 — already
  disclosed, nothing new.** D-11 records that this seat's rater eligibility
  ENDED 2026-09-17 15:19 and the R2H blind rater is plumb-fable (measured
  blind, guard exits 0 for that seat); kiln and cairn are exposed too via the
  original task cell. The guard failing on this session is the known recorded
  state doing its job. This seat does not touch `team/R2H-FREEZE.md` and does
  not quote the arm map anywhere.
- **`check_answer_provenance` control fixture** — cairn's, in progress per
  the ops note. Not mine.
