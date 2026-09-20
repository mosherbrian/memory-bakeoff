# CORVID-S8-4 VERIFY — close-on-evidence receipt

Row S8-4 is cairn's ADMISSION DEFECT (2026-09-17 16:4x PDT): a verbatim
duplicate of S7-4, done + VERIFIED PASS, receipt `team/CORVID-S7-4-VERIFY.md`.
Per the re-measurement rule there is no expected difference from S7-4's
external-lane result, so there is nothing to re-run and no new verification to
author.

Close evidence, read 2026-09-17 ~17:10 PDT:

- Declared artifact `team/S7-KD-WORLDS/` exists (producer kiln-flash).
- Declared check re-run at close: `python3 team/S7-KD-WORLDS/check.py
  --selftest` → rc 0 ("selftest: PASS (the conforming fixture accepted; ...
  38 mutants each rejected by exactly their own markers, no traceback)").
- Verification of substance on file: `team/CORVID-S7-4-VERIFY.md`
  (2026-09-17 16:27 PDT).

Verifier of record: corvid-dsh. This receipt books the duplicate's closure on
existing evidence; it authors no new measurement. The real rank-5 successor is
a GiLMore/Brian call, per cairn's note on the row.
