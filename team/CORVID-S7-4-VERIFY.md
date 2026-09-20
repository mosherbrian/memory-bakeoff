# CORVID-S7-4-VERIFY — verdict on QUEUE row S7-4

**Verdict: VERIFIED PASS** (the row's deliverable was per-family results on the
upstream frozen worlds, scores re-derived with no import, delivered)
**Verifier:** corvid-dsh · 2026-09-17 16:27 PDT (clock read at write)
**Independence:** artifact `team/S7-KD-WORLDS/` (including the upstream clone)
authored by kiln-flash; gate `check.py` authored by plumb-fable (S7-4G, landed
13:53:27, pre-artifact 14:19 per mtimes — provenance in
`team/CORVID-S7-4G-VERIFY.md`). Corvid authored neither. Gate verification was
S7-4G; this is the artifact verdict the row reserves to corvid. Re-filed from
the live session after the 09-17 engine-stall loop lost the original wake.

## Declared check (run fresh from this seat, 16:24:42)

- `python3 team/S7-KD-WORLDS/check.py --selftest` → **rc 0**
- gate on the real artifact → **rc 0, clean**: "1 engines, 3 families, 120
  items, per-family pass rates recounted"

## What I checked

1. **Row terms honored.** "Per-family results on worlds/v2 seeds, scores
   re-derived, no score import": the worlds are the upstream MIT frozen
   500-fact files (seeds 1+2) cloned from
   github.com/techtheist/KnowledgeDrift @ commit edff308e…, both sha-pinned in
   the declaration — nothing home-grown. Ops replayed in stream order per the
   upstream protocol (flat-store column), each probe answered at its own
   stream position.
2. **Frozen instrument.** 120 items (Retrieval stratified 5-per-phrasing
   across lexical/paraphrase/oblique/crossed, plus Abstention, Rationale;
   20/seed/family) frozen pre-run and sha-bound into 360 receipts. Controls
   first and honest: return-nothing passes every Abstention and no Retrieval
   item; oracle passes all.
3. **Independent re-derivation (from CORVID-S7-4G-VERIFY, 15:35).** Recounted
   from raw results.jsonl without the gate: bm25 Retrieval 21/40 = 0.525
   (1.00 lexical, dragged by paraphrase/oblique/crossed — the upstream
   phrasings do real work), Rationale 5/40 = 0.125, Abstention 0/40 = 0.000.
   Matches the gate and the cell exactly. My adversarial copies of the gate
   reject an inflated per-family cell ([NUMBERS-DISAGREE] naming the true
   21/40) and a smuggled leaderboard line ([SCORE-IMPORTED]) — the no-import
   term is enforced, not decorative.
4. **Substance and caveats.** Abstention 0.000 is the second instrument
   independently reproducing the S6-2 headline shape (lexical recall without
   abstention) on a corpus we did not build — exactly the row's purpose.
   Six families not run, with capability reasons recorded in
   families_not_run (history/suspects/trace/temporal/endorsement absent from
   the engine): a capability absence is not scored as a behavior. The
   KnowledgeDrift card's caveat is quoted verbatim in verdict.json and travels
   beside every number.

## Limits

One engine (bm25), 2 of 8 world seeds, 3 run families — all declared in-band;
the cell scopes the conclusion to this instrument rather than generalizing.
