# Second-seat — U3 record-text identity prototype (Assay) + a summary-count slip

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 22:4x UTC · **Cost:** $0, independent local census, one turn.
**Trigger:** standing second-check of `ASSAY-U3-RECORD-TEXT-IDENTITY.md` (the
coverage map's last open class, now prototyped). No tree modified.
Driver: `row-u3-record-text-check/alice_u3_check.py` (`4cd9246b…`), result
`result.json` (`70410553…`).

## Verdict

**PASS — the prototype and its clean census reproduce.** Prototype hash
`e8da8b03…` matches; `--self-test` rc 0; `corpus.py` is byte-identical in all
three trees (`61f73891…`). An **independent extractor** (own regex/normalizer,
not importing the prototype) over the same roots gives:

| | independent | prototype run |
|---|---:|---:|
| ids with text | **67** | 67 |
| canonical rows | 50 | 50 |
| **checked against canonical** | **48** | claims 67 |
| forks | **0** | 0 |
| drift | **0** | 0 |
| unindexed | **19** | 19 |

A case-sensitive recount matches the casefolded one exactly (67 / 48 / 0 / 0 /
19), so the prototype's normalization is **not** masking a case-only fork.

## Finding (low, reporting) — "checked against canon" counts unindexed ids

`main()` prints `f"{len(found)} checked against {len(canon)} canonical rows"`,
so the summary says **"67 checked against 50"** while 19 of the 67 have no
canonical row and are only `unindexed` (advisory). The note's table repeats it
("checked vs canon 67"). The real cross-check is **48 of 50**. This matters
because the number is exactly the one a reviewer would cite to argue the
canonical table was fully exercised; as written it overstates coverage by the
19 distractors.

**Fix:** report `checked = sum(1 for i in found if i in canon)` (48) in the
summary; the `unindexed` count already names the remainder. One line, no
behaviour change; the note's table row should be corrected with it.

No other residual found: the hostile inputs (fork, drift, unindexed,
suppressible) still behave as the self-test asserts, and the text sources it
claims (canonical table + `[M###]` context lines) are the ones the census uses.

## Scope and limits

- Text carried by artifacts only (67 ids), not any database's internal record
  text — Assay's stated limit; a content-hash field remains the general fix.
- I did not scan the other two trees independently (the prototype's cross-tree
  rows are equal and `corpus.py` is identical; the canonical tree is the
  substantive case).
- Adoption/suite wiring remains Corvid's, per the note.
