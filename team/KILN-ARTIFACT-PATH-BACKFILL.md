# S4-4 — Artifact-path backfill for the four path-less done rows

**Row:** QUEUE S4-4 · **Author:** kiln-flash · **Date:** 2026-09-16 12:25 PDT · **Cost:** $0
**Method:** for each row, read the done cell's deliverable description, locate
the artifact on disk, verify it exists, then append an
`artifact-path backfill:` note to the row's status cell (append-only; no cell
history rewritten). None of the four warranted READ-BY-BRIAN reclassification
— every deliverable existed and was findable.

| Row | Deliverable per its done cell | Backfilled path (verified on disk) |
|---|---|---|
| 16 (S4 fire-log readiness) | dry-run packet build sealed, self-check sha `f5ab5259…` | `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/sealed-s4-dryrun-20260912/` — sealed dir (mode 0700, deliberately not under `team/`: opening packets is B1 exposure). Hash labels per `team/RETRO-S1-Assay.md`: `f5ab5259eea6…` is the DERIVED sha256-of-hashes over the packet set; the file-content hash of `selfcheck.log` is `ff1296c63dd6…` |
| 39 (Sprint-2 burndown refresh) | burndown addendum in SCOREBOARD | `team/SCOREBOARD-20260912.md` (Sprint-2 rows 35–38 + row-39 mapping to SPRINT-2-OUTLINE goals; duplicate-36 numbering collision noted for GiLMore) |
| S3-4 (exposed-span rater) | exposed-span report + rater seating with disclosure | `team/RATER-HANDOFF.md` (seating + seal rules with the exposed-span disclosure) + `team/BLIND-VERDICTS-round2-conductor-claude.md` (round-2 verdict table, 60/60 AGREE + 286/286 CONSISTENT) |
| S3-10 (PO follow-up on S3-1) | follow-up post in BOARD | `team/BOARD.md` — the 2026-09-15 S3-1 tracking trail (Ledger nudges ~line 778, Corvid verifier-status ~line 802, Assay gated-wake answer ~line 806, PO calls ~line 804; line numbers drift, BOARD is append-heavy — locate by the 2026-09-15 S3-1 date span) |

Notes for the reviewer:

- Row 16's path lives in a **different tree** (`implementer/repo-glm-dsh2/`)
  than `team/` because the packet contents are the one thing raters must NOT
  read (B1 blinding). The path, not the contents, is what this backfill adds.
- Row S3-4's verdict data was flagged "with GiLMore, UNSIGNED" by the S4-3
  audit; that verification question is separate from this row's
  artifact-existence question and is untouched here.
- No row was reclassified READ-BY-BRIAN: that disposition applies where no
  artifact exists because the row's consumer was Brian reading in-session;
  all four rows produced durable artifacts.

— **kiln-flash**, S4-4. Queue edits: four status-cell appends, applied 12:25 PDT.
