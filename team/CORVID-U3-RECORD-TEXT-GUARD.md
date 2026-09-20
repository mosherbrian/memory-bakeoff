# GUARD — record-text identity (guard 18, U3)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-13
**Adopted from:** Assay's validated prototype `record_text_identity_prototype.py`
`5ae37253…` (`team/ASSAY-U3-RECORD-TEXT-IDENTITY.md`); second-seated by Alice
(`ALICE-U3-RECORD-TEXT-SECONDCHECK.md`). **Cost:** $0, local.
**Closes:** coverage-map Layer C's last open class **U3** (the open half of Muse
3.2 — same `M###` id, different record text).

## What it does

`scripts/check_record_text_identity.py` (`0b8fd3aa…`) scans
`.json/.jsonl/.csv/.md/.txt` for `- [M###] <text>` context lines and the
canonical `M### -> text` table in `src/memory_bakeoff/corpus.py`, then:

- `record-text fork: <id>` — the same id carries >1 distinct normalised text
  (the U3 defect proper) → exit 1;
- `record-text drift: <id>` — an artifact's text disagrees with the canonical
  table → exit 1;
- `unindexed record text: <id> (advisory)` — id with text but no canonical row
  (generated distractors) → reported, suppressible with `--no-unindexed`.

Suite dialect: missing / unreadable / non-directory canonical table or scan root
is a structured prerequisite, not a crash; `--self-test` drives clean, fork,
drift, advisory-suppression, and both prerequisite shapes through the real path.

## Wiring

- **Meta-guard:** added as the **17th control** — `check_checker_exit_contracts.py`
  `956f5338…`, **17/17 hold**; fixtures `corpus.py` + a matching/mismatching
  `DOC.json`, marker `forks/drifts: [1-9]`, argv `--canonical`.
- **Coverage map rev 17:** Layer B row 17 added; **U3 closed**; Layer C now
  empty; title/counts 17→18 guards.

## Census (repo-glm-dsh3, default canonical)

`67 ids with text, 48 checked against 50 canonical rows, 0 forks/drifts,
19 advisory unindexed (M441–M499 distractors), rc 0` — matching Assay's
three-tree census (canonical/dsh2/dsh3 all 0/0).

## Limits

- Covers only text the artifacts actually carry (67 ids) plus the canonical 50;
  it does not read any database's internal record text. A content-hash sidecar
  would generalise it to stores that do not ship the text — still the longer-term
  fix.
- Distractor text has no canonical source, so it is advisory, not checked.

## Verify (read-only)

```bash
cd implementer/repo-glm-dsh3
python3 scripts/check_record_text_identity.py --self-test
python3 scripts/check_record_text_identity.py          # 0 forks/drifts, rc 0
python3 scripts/check_checker_exit_contracts.py        # 17/17 hold
```

— **Corvid** (`worker-glm-dsh3`). $0, static. **Second-seat re-check: Alice PASS**
(`ALICE-U3-GUARD-SECONDCHECK.md`) — live guard `0b8fd3aa…`, `--self-test` rc 0,
census "67 ids / 48 checked", meta-guard `956f5338…` 17/17; independent real-CLI
probes of drift / missing-canonical / directory-canonical / `--no-unindexed` all
hold, no traceback; no new residual.
