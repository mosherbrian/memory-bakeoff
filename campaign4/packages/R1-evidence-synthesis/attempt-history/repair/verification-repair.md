# R1-synthesis-repair-1 — independent post-repair verification

- **Verifier:** corvid-dsh (worker kiln; I authored neither the initial nor the
  repaired synthesis). **Original PASS preserved** verbatim at
  `attempt-history/initial/verification.md` (`a1e84e60…`); it is not revoked.
- **Worker claim:** `ex-R1-synthesis-repair-1-w1.json` (`completed`); artifact
  hashes **verified equal**: `synthesis.md` `098bdc1c…`, `evidence-table.tsv`
  `3dd4c926…`, `limitations.md` `44b6f91d…`.
- **Read before repaired output:** both full S13 gate records at their
  per-entry pins — `team/CORVID-S13-1G-VERIFY.md` (`22c995f`, `c8b32bb6…`) and
  `team/CORVID-S13-2G-VERIFY.md` (`22c995f`, `bf8d2599…`); both hash-match
  `sources-repair.json` (126 entries, per-entry commit authoritative).
- **Verdict: INCOMPLETE (outcome failed)** — the substantive S13 coverage repair
  is correct and criteria 1–4 are met in `synthesis.md`, but the repaired
  `evidence-table.tsv` **reintroduces a column-mapping defect that breaks
  criterion‑1 traceability**, so the repair is not passable as delivered.

## What the repair got right

- **Corrected coverage.** The old synthesis substituted S12-1G plus the S13
  runner mismatch for the criterion's "both rejected/unsatisfiable gate
  episodes." The repair now traces the **actual** pair, and the asymmetry is
  accurate against the pinned records:
  - **S13-1G — unsatisfiable.** Round 1 demanded an expression tree
    (`{"op","args"}`); round 2 demanded `{"score","reject"}` + `threshold_grid` +
    item `id` + baseline `abstained`/`useful_retrieval`. The frozen S11
    declaration carries a declarative config (`decision:"supported_fraction_lt_
    threshold"`, `content_stopwords`, `min_document_frequency`), grid under
    `thresholds`, items under `item_id`, baselines under `passed`. No faithful
    build can exit 0. **Correct.**
  - **S13-2G — satisfiable only by fabricated sections.** Round 1 inventory =
    12 names (4 non-mechanisms: two heading prefixes, a recommendation heading,
    a filename); round 2 regressed to 73 names ("Caveats", "JavaScript", …).
    Honest audits rejected by 4 then 66 missing-section findings. **Correct.**
  - Fixture-vs-real-input class tied to S12-1G rounds 2–3; S12-1G's later PASS
    once bound and the S13 attempt-2 runner mismatch stated as contrast.
    **Correct.**
- **No new run / no overclaim.** `synthesis.md` and `limitations.md` state
  arithmetic was read, not executed; the gate reviews are cited as *reported
  review evidence*, not independently replayed. No fresh experiment, question,
  or data. `sources-repair.json` adds only the two existing Sept-20 reviews.
- **Reference/disposition honesty.** "fix specified, unimplemented" matches the
  records: both gates end at ADDENDUM 2 VERIFIED FAIL with fixes proposed and no
  later pass; no disposition was omitted.

## Blocking defect — evidence-table.tsv columns are mislabeled

The original rows populated header columns **1–7 correctly** and were missing
only column 8 (`counterevidence`). The repair's stated premise
(`limitations.md`: rows were "missing `commit`") is factually wrong — `commit`
was already column 3. The repair inserted the commit value at position 4
instead of appending the missing field, shifting every semantic value right by
one for the 14 pre-existing rows:

| column (header) | repaired value, row 1 | should hold |
|---|---|---|
| `field_or_line` | `485d783d` (the commit) | `row 1: current answer + limitation` |
| `outcome` | `row 1: current answer + limitation` | `no task-outcome evidence in interval` |
| `population_sample` | `no task-outcome evidence in interval` | `S11 rows only (…)` |
| `limitation` | `S11 rows only (…)` | the "answer page states …" text |
| `counterevidence` | the "answer page states …" text | (genuine counterevidence) |

The two **new** rows (16–17) use the correct convention (`field_or_line` = the
field text), so the file is internally inconsistent: column 4 is a commit for
14 rows and a field descriptor for 2. Field counts are uniform (8) but the
headers do not describe the data. This fails the repair task's explicit
"evidence TSV column consistency" check and the contract's criterion‑1
requirement that each claim carry a precise field/line — mislabeled
`field_or_line`/`outcome` cells defeat exactly that traceability.

**Correct fix (small, no new work):** restore the original 14 rows' columns 1–7
from `attempt-history/initial/evidence-table.tsv` and append the 8th
(`counterevidence`) field (empty where none); do not insert at position 4.
Update the `limitations.md` repair note to describe the defect accurately
(missing `counterevidence`, not `commit`).

## Original five criteria

1. **Traceable coverage — met in synthesis.md, broken in the TSV** (above). The
   prose now covers the six answer-page questions, S13 transfer, and both S13
   gate episodes; the TSV mapping is not traceable as labeled.
2. **No overgeneralization — met.** Operational gate/runner defects are counted
   as process, never efficacy.
3. **Counterevidence/arithmetic — met.** Failures and denominators retained;
   my spot-checks of S13/S11/S7-COMPOSE/S10-KD-CROSS/S11-LAYER-HIST/S9-DOOR-RUNG2
   against `git show` bytes still match.
4. **One next step — met.** Unchanged preregistered memory-on/off comparison
   with falsification/stop; alternatives ranked; compaction caveat.
5. **Independent judgment — this document.** Original PASS preserved.

## Disposition

Substantive repair: **sound**. Deliverable: **INCOMPLETE** on the table defect;
Tern accepts. No worker artifacts edited; no git, runtime, or source changes.

*Files reviewed: `package.md`, `repair-decision.json`, `sources-repair.json`,
`repair-worker-task.txt`, `repair-verifier-task.txt`, `synthesis.md`,
`evidence-table.tsv`, `limitations.md`, `attempt-history/initial/*`,
`team/CORVID-S13-1G-VERIFY.md`@22c995f, `team/CORVID-S13-2G-VERIFY.md`@22c995f.*
