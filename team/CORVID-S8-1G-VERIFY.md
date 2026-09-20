# CORVID-S8-1G VERIFY — close-on-evidence receipt

Row S8-1G is cairn's ADMISSION DEFECT (2026-09-17 16:4x PDT): the gate for the
S8-1 duplicate. Its declared check.py is S7-1's — exists, passes, VERIFIED PASS
today under S7-1G (receipt `team/CORVID-S7-1G-VERIFY.md`, 2026-09-17 15:24
PDT). Per cairn's ruling there is no gate to author for a re-run that will not
happen; the row closes on evidence as written.

Close evidence, read 2026-09-17 ~17:10 PDT:

- Declared artifact `/home/bmosher/memory-bake-off/team/S7-BM25-PREFILTER/check.py`
  exists.
- Declared check re-run at close: `python3
  team/S7-BM25-PREFILTER/check.py --selftest` → rc 0.
- Gate verification of substance on file: `team/CORVID-S7-1G-VERIFY.md`.

Verifier of record: corvid-dsh. This receipt books the duplicate gate's
closure on existing evidence; it authors no new gate.
