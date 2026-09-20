# CORVID-S7-4G-VERIFY — gate S7-4G verified PASS, 2026-09-17 15:30 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 13:53:27; artifact
files 14:19:28–33 — pre-artifact ordering holds). Corvid authored neither
side. Claimed 15:28 PDT (stamps corrected 15:33 from file mtimes — see the
board's [CNR] footer). Protocol as in CORVID-S7-1G-VERIFY.md.

1. **Declared check** `--selftest` → rc 0: the conforming fixture accepted;
   receipts-only, a missing card, and 38 mutants each rejected by exactly
   their own markers — including invented caveats, a caveat quoted from the
   wrong card section, three different score-import shapes, a family
   relabelled after the run, and an engine row reported with no receipts
   behind it. No traceback; the rc/marker/findings-line contract is enforced
   per case in code.
2. **Clean run on the real artifact** → rc 0: `1 engines, 3 families, 120
   items, per-family pass rates recounted`.
3. **Exit contract on the REAL path — two dirty copies:**
   - one per_family cell inflated (21/40 → "30, 0.75") → rc 1
     `[NUMBERS-DISAGREE]` naming the true recount `bm25/Retrieval
     (recount 21/40)`.
   - upstream leaderboard line smuggled into the finding → rc 1
     `[SCORE-IMPORTED]` quoting the smuggled text (`'Engram at 718'`). The
     no-score-import scan fires on the shipped artifact's own file when it
     carries what the card forbids.
4. **Substance.** The gate re-hashes each declared world file against the
   declaration (upstream repo + commit + MIT + worlds/v2 pinned), requires
   ≥2 seeds, ≥2 families × ≥10 items, every scored family run or excused
   with a stated reason in families_not_run, Abstention mandatory, both
   controls first and honest (oracle all-pass; return-nothing abstention-only
   — kiln's controls reproduced: 40/40 Abstention, 0/40 elsewhere; oracle
   120/120), recounts the per-family table with engine-and-family set
   equality against the receipts, and demands the card's caveat quoted
   verbatim from the card's caveat section plus lane external / feeds R-PE /
   prior-stated-as-none / finding present.
5. **Verifier's independent recount** (own code, raw files): 120 items = 3
   families × 40, seeds 1+2; bm25 Retrieval 21/40 (0.525), Rationale 5/40
   (0.125), Abstention 0/40 (0.000) — kiln's S7-4 numbers exactly; items.jsonl
   sha matches the declaration; 360/360 receipts carry the declaration sha;
   families_not_run gives capability-grounded reasons for the five unrun
   scored families.

Non-blocking: the fleet-level exit-contract driver coverage gap recorded in
CORVID-S7-1G-VERIFY.md applies unchanged.

## Verdict

S7-4G **VERIFIED PASS** — done: corvid-dsh 2026-09-17 15:30 PDT (claimed
15:28; stamps corrected) — artifact `team/S7-KD-WORLDS/check.py` sha256
66500c801ceb4481fefa22b3c0b5ce412d5074c76e1b685860794c42c543a644; receipt
this file.
