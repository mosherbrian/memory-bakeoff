# CORVID-S7-2G-VERIFY — gate S7-2G verified PASS, 2026-09-17 15:26 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 13:44:59; artifact
files 13:57:21–22 — pre-artifact ordering holds on mtimes). Corvid authored
neither side; independence holds. Claimed 15:25 PDT (stamps corrected 15:33
from file mtimes — see the board's [CNR] footer).

Protocol identical to `team/CORVID-S7-1G-VERIFY.md`; this receipt records what
was run and what came out.

1. **Declared check** `python3 team/S7-COMPOSE/check.py --selftest` → rc 0:
   3 conforming fixtures accepted (complementary, honest negative, and a
   conforming run on S7-1's prefiltered arm); receipts-only and unreadable
   prior rejected; 30 mutants each rejected by exactly their own markers; no
   traceback. Both-holds requirement proven in code (accept = rc 0 + zero
   markers; reject = rc 1 + exact marker set + `S7-2 gate findings: N`).
2. **Clean run on the real artifact** → rc 0: `not-complementary, gain
   +0.000; compose 0.600/1/5; overlap {both 1, only_bm25 4, only_pi_lcm 5,
   neither 0}`.
3. **Exit contract on the REAL path — two dirty copies of the shipped
   artifact, corvid's own adversarial edits:**
   - verdict flipped to `complementary` over the +0.000 data → rc 1,
     `[VERDICT-CONTRADICTS-RULE]`, findings line, no traceback.
   - compose arm hand-improved where pi-lcm abstained (the "a hand-improved
     compose arm is not evidence" attack, injected into the real rows) → rc 1
     with three markers: UNKNOWN-ID (the injected ids are outside the case
     stores — the gate even identifies the fabricated ids as foreign),
     COMPOSE-NOT-COMPOSED, NUMBERS-DISAGREE.
4. **Substance.** The gate recomputes the prior and all three arms from raw
   files, sha-binds rows to the declaration, re-checks the S7-1 dependency
   against `team/S7-BM25-PREFILTER/verdict.json` ON DISK (a quoted verdict
   that disagrees with the file is `BM25-VARIANT-UNJUSTIFIED`; composing on
   the refuted prefilter is rejected — exactly the chain kiln's close notes
   describe), requires the compose arm to be mechanically the composition,
   recomputes the two-by-two complementarity table, and derives the verdict
   from the pre-declared margin. RANKING-LANGUAGE marker bars the finding
   from becoming an engine ranking (Brian's 2026-09-16 decision #1).
5. **Verifier's independent re-derivation** (own code, raw files only):
   bm25 0.500/5/0; pi_lcm 0.600/1/5; compose 0.600/1/5; overlap 1/4/5/0;
   gain over the better single arm +0.000 vs declared margin 0.10. Matches
   the gate's clean summary and kiln's S7-2 close note number for number.

Non-blocking: same fleet-level contract-driver coverage gap as recorded in
CORVID-S7-1G-VERIFY.md (4 team/tools guards without exit-contract controls;
driver itself fail-closed rc 1 on INCOMPLETE). The S7 gates' contracts are
proven directly here.

## Verdict

S7-2G **VERIFIED PASS** — done: corvid-dsh 2026-09-17 15:26 PDT (claimed
15:25; stamps corrected) — artifact `team/S7-COMPOSE/check.py` sha256
c34c7e1fd37662f39964569bf210cc60386c193be897cdbd469dcd07e07348e3, all runs
above against exactly these bytes; receipt this file.
