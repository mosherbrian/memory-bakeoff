# Verity second-seat: candidate-card numbering (muse-drafter's collision fix)

Scope: the card-number collision fix reported in RD-THREADS (two files
claimed "Card 7"; EVOMEMBENCH re-headered to Card 8). Count check only;
no content reviewed.

## Re-derived (file → claimed number)

- STREAMMEMBENCH → 2; STALE-SUPERSEDE → 3; MEMSEC-GATEMEM → 4;
  HALUMEM → 5; STATEMEMBENCH → 6; LONGMEMEVAL-V2 → 7; EVOMEMBENCH → 8;
  MEMOPS → unnumbered.
- Exactly one claimant per number 2–8, zero collisions, zero gaps.
  AGREE with the reported sequence "2,3,4,5,6,7,8 + unnumbered MEMOPS".
- Residual (owner call, trivial): MEMOPS as "card 1 by elimination" is
  still implicit — one header edit makes it explicit. Not a defect.

$0, read-only, one turn. — Verity 2026-09-14
