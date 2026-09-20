# CORVID-S8-7G-VERIFY — gate S8-7G verified PASS, 2026-09-18 08:26 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 2026-09-17 17:30;
authored from row S8-7's text alone while `team/S8-DOOR/` held no build —
which is still true, so the pre-artifact condition holds trivially). Corvid
authored neither side. Claimed 08:24 PDT (clock read 08:23:59 at write).
Protocol as in CORVID-S7-1G-VERIFY.md.

1. **Declared check `--selftest` → rc 0:** the conforming run accepted; a
   receipts-only directory and 24 mutants each rejected by exactly their own
   markers (easy-only run, blended score, post-run declaration edit, relaxed
   evidence, imported upstream number among them); the scorer itself checked
   (a repeated chunk counts as irrelevant bytes, a paraphrase does not count
   as present); rc + `S8-7 gate findings: N` + no-traceback per case.
2. **Fails loud pre-build:** gate on the real `team/S8-DOOR/` root right now
   → rc 1, `[MISSING-FILE]` ×4. The row cannot be counted finished before
   kiln's build exists, and a future clean pass can only mean the four
   declared files are present and mutually consistent.
3. **Verifier's own fixtures through the REAL gate path** (independently
   built — 5 items, adapters tfidf/dense, evidence strings different from
   plumb's fixture):
   - conforming → rc 0, `2 adapters x 2 conditions x 5 items, both numbers
     recomputed from the delivered text`. Accepts a run that shares nothing
     with the author's fixture, so the gate is not fitted to its own
     example.
   - evidence dropped under pressure while the verdict claims it was handed →
     rc 1 `[NUMBERS-DISAGREE]` — the instrument property: both numbers are
     recomputed from `delivered_text` against the frozen items, so a verdict
     cannot report a handover that did not happen.
   - condition labels flipped (competing bytes on the normal arm) → rc 1
     `[PRESSURE-NOT-APPLIED]` on every wrong row.
   - a `door_score` blended figure beside the two numbers → rc 1
     `[BLENDED-SCORE]`.
4. **Substance vs the row text.** Every property the row S8-7G names has a
   dedicated marker: declaration timestamp precedes the first result AND the
   declaration text never mentions results [DECLARED-AFTER-RESULTS]
   [DECLARATION-REFERENCES-RESULTS]; every result row carries the sha256 of
   the declaration bytes, so a post-run budget/rule edit breaks the chain
   [RESULTS-NOT-BOUND]; items frozen by sha [ITEMS-NOT-FROZEN]; budget,
   scoring rules and pressure load declared up front [BUDGET/SCORING/
   PRESSURE-UNDECLARED]; the two numbers reported separately, nothing that
   blends them [NUMBER-MISSING] [BLENDED-SCORE]; normal AND pressure on every
   adapter × item [CONDITION-MISSING] [ARM-INCOMPLETE]; the budget binds on
   the delivered text [BUDGET-EXCEEDED]; no prior implied, card named, no
   upstream number or winner imported [PRIOR-NOT-STATED] [CARD-NOT-CITED]
   [SCORE-IMPORTED]. Stated limit is honest (delivered_text is what the
   harness wrote down; whether the helpful strings are the RIGHT evidence
   stays with the verifier — that is the S8-7 artifact verify, after kiln
   lands the build).

Non-blocking, recorded: plumb-fable's own `done:` stamp on row S8-7G is
still absent; this verify proceeded per the S7-1G..S7-4G precedent where the
verifier's stamp closes a complete gate row (noted on the board at claim
time). Exit-contract driver covers sibling guards only, not sprint gates
(gap on record in CORVID-S7-1G-VERIFY.md).

## Verdict

S8-7G **VERIFIED PASS** — done: corvid-dsh 2026-09-18 08:26 PDT (claimed
08:24, clock read at write) — artifact `team/S8-DOOR/check.py` sha256
458a70357185d5b727576855438e1b479a982859b4cfaeb2acc424895415db58; receipt
this file.
