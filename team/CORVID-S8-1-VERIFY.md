# CORVID-S8-1 VERIFY — close-on-evidence receipt

Row S8-1 is cairn's ADMISSION DEFECT (2026-09-17 16:4x PDT): a verbatim
duplicate of S7-1, done + VERIFIED PASS, receipt `team/CORVID-S7-1-VERIFY.md`.
Per the re-measurement rule there is no expected difference from S7-1's
artifact-refuted verdict, so there is nothing to re-run and no new
verification to author.

Close evidence, read 2026-09-17 ~17:10 PDT:

- Declared artifact `team/S7-BM25-PREFILTER/` exists (producer kiln-flash,
  files 13:40-13:50 PDT).
- Declared check re-run at close: `python3 team/S7-BM25-PREFILTER/check.py
  --selftest` → rc 0 ("selftest: PASS (2 conforming fixtures accepted, one of
  them an honest refutation; ... 29 mutants each rejected by exactly their own
  markers, no traceback)").
- Verification of substance on file: `team/CORVID-S7-1-VERIFY.md`
  (2026-09-17 16:26 PDT).

Verifier of record: corvid-dsh. This receipt books the duplicate's closure on
existing evidence; it authors no new measurement. The real rank-3 successor is
a GiLMore/Brian call, per cairn's note on the row.
