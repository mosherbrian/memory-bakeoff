# Assay — U3 prototype: record-text identity is checkable now (not "no source")

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local
**Thread:** Assay — instrument power checks.
**Subject:** coverage-map Layer C's last open class, **U3** (the open half of
Muse 3.2): "same `M###` id, different record text across corpora ... needs
artifacts to carry record-content hashes; **no current source**."
**Verdict:** two current sources exist for this corpus, so a U3 probe **is**
buildable now; the live census is clean.

## Correction to the coverage map

- `src/memory_bakeoff/corpus.py` is a canonical `M### -> text` table
  (M001–M050; identical in all three trees, sha `61f73891…`);
- the reader fixtures carry `- [M###] <text>` lines — core/stress
  `contexts.json`, per-request fixtures, and the gen15 reader results (67 ids
  with text).

So U3 does not need new artifact fields to start; it can check **textual identity
of the text artifacts already carry**, and cross-check it against the canonical
table. (A content-hash field would generalize it to databases that do not ship
the text; that remains the longer-term fix.)

## Prototype

`record_text_identity_prototype.py` sha256 `5ae37253…` (rev 2; rev 1
`e8da8b03…`) flags:

- `record-text fork: <id>` — the same id carries >1 distinct normalized text
  across files (the U3 defect proper);
- `record-text drift: <id>` — an artifact's text disagrees with the canonical
  `corpus.py` row;
- `unindexed record text: <id>` — id with text but no canonical row
  (generated distractors M051–M500) — advisory, suppressible with
  `--no-unindexed`.

`--self-test` PASS (4 classes: clean; fork; table drift; non-table id advisory
and suppressible).

## Census (three trees, 2,902 files scanned in ~2.4 s)

| tree | ids with text | checked vs canon | forks/drifts | unindexed |
|---|---:|---:|---:|---:|
| `implementer/repo` | 67 | 48 | **0** | 19 |
| `repo-glm-dsh3` | 67 | 48 | **0** | 19 |
| `repo-glm-dsh2` | 67 | 48 | **0** | 19 |

48 unique ids (528 id-per-file occurrences) cross-checked against the 50
canonical rows, **0 mismatches**; the 19 unindexed ids are stress distractors
(M441–M499), expected.

## Rev 2 — summary count corrected (Alice's second seat)

Alice's `ALICE-U3-RECORD-TEXT-SECONDCHECK.md` reproduced the census with its own
extractor (67 ids, **48** checked, 0 forks/drift, 19 unindexed; case-sensitive and
casefolded agree) and found a **reporting** slip: the prototype printed
`len(found)` twice, so the summary said "67 checked against 50 canonical rows"
when only 48 had a canonical row. Fixed to count the ids that actually match the
canonical table; prototype now `5ae37253…`. No detection behaviour changed.

## Receipts

- prototype rev 2 `5ae37253…`; sealed `selftest.txt` `aba6c402…`,
  `census.txt` `dc39679b…` under
  `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-record-text-identity/`.

## Limits

- Covers only text that artifacts actually carry (67 ids) plus the canonical 50;
  it does not read any database's internal record text.
- Distractor text has no canonical source and is reported advisory, not checked.
- No suite wiring; the power check is the `--self-test`. Owner for adoption:
  Corvid.

— **Assay** (`worker-glm-dsh2`).
