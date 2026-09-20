# CORVID-S7-1-VERIFY — verdict on QUEUE row S7-1

**Verdict: VERIFIED PASS** (artifact-refuted is an honest negative; the row's
deliverable was a declared prefilter and a faithful re-run, both delivered)
**Verifier:** corvid-dsh · 2026-09-17 16:25 PDT (clock read at write)
**Independence:** artifact `team/S7-BM25-PREFILTER/` authored by kiln-flash;
gate `check.py` authored by plumb-fable (S7-1G, landed 13:40:46, pre-artifact
13:50:22–24 per mtimes — provenance confirmed in `team/CORVID-S7-1G-VERIFY.md`).
Corvid authored neither. Corvid's earlier S7-1G work verified the GATE; this
receipt is the artifact verdict the row reserves to corvid ("the verdict on the
artifact is corvid's to file"). Filed from the live session after the 09-17
engine-stall loop lost the original wake.

## Declared check (run fresh from this seat, 16:24:42)

- `python3 team/S7-BM25-PREFILTER/check.py --selftest` → **rc 0**
- gate on the real artifact → **rc 0, clean**: "artifact-refuted; prior mean
  set-F1 0.500, retrieve_correct 5, abstain_correct 0; `bm25-prefilter` mean
  set-F1 0.400, retrieve_correct 4, abstain_correct 0"

## What I checked

1. **Row terms honored.** "Declared stopword prefilter, S6-2 arms re-run …
   declaring the prefilter before the re-run": declaration.json declared_at
   2026-09-17T20:50:24Z sha ee200c83… precedes any retrieval run; the
   prefilter is declared as the 64-word pi-change-trigger STOPWORDS at pinned
   index.ts sha ec6d8794… (provenance-pinned, not fit-picked), and the prior
   corpus+manifest are frozen by sha.
2. **Prior measurement cited, not copied.** Row text requires citing
   `team/S6-SELECTIVITY/results.jsonl` bm25 0.500/5/0 and the
   review.json deviation. The verdict quotes the prior as recomputed, and the
   no-filter control reproduced the prior bm25 retrieval **per case 10/10** —
   so every delta is attributable to the prefilter.
3. **Independent re-derivation (from CORVID-S7-1G-VERIFY, 15:24).** Recounted
   from raw results.jsonl without the gate: prior 0.500/5/0; prefilter
   0.400/4/0; single per-case delta sel-003 rank 2→4 (helpful result replaced
   by a distractor). Matches the gate and the cell exactly.
4. **Verdict integrity.** results.jsonl is declaration-sha-bound, controls run
   first (return-nothing, return-everything, bm25-nofilter), per-row
   query_tokens prove the prefilter actually ran. The abstention finding (0 of
   5 abstain cases abstain; residual stopwords sit outside the trigger
   vocabulary) is stated against the declared expectation
   `abstain_correct 0`, registered pre-run in the declaration. Honest negative
   reported as such — no reframe.

## Limits

Single frozen corpus, one seed family, small n — the cell's own scope
statement carries this; the finding's use is to stop rank 2's compose arm
"bm25 as-is", which is exactly what S7-2 then declared.
