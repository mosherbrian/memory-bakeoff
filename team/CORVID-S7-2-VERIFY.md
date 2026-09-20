# CORVID-S7-2-VERIFY — verdict on QUEUE row S7-2

**Verdict: VERIFIED PASS** (not-complementary is an honest negative; the row's
deliverable was the compose measurement on the same frozen corpus, delivered)
**Verifier:** corvid-dsh · 2026-09-17 16:26 PDT (clock read at write)
**Independence:** artifact `team/S7-COMPOSE/` authored by kiln-flash; gate
`check.py` authored by plumb-fable (S7-2G, landed 13:44:59, pre-artifact
13:57:21 per mtimes — provenance in `team/CORVID-S7-2G-VERIFY.md`). Corvid
authored neither. Gate verification was S7-2G; this is the artifact verdict
the row reserves to corvid. Re-filed from the live session after the 09-17
engine-stall loop lost the original wake.

## Declared check (run fresh from this seat, 16:24:42)

- `python3 team/S7-COMPOSE/check.py --selftest` → **rc 0**
- gate on the real artifact → **rc 0, clean**: "not-complementary, gain +0.000;
  compose mean set-F1 0.600, retrieve_correct 1, abstain_correct 5; overlap
  {'both': 1, 'only_bm25': 4, 'only_pi_lcm': 5, 'neither': 0}"

## What I checked

1. **Row terms honored.** "bm25 retrieval behind pi-lcm's abstention gate …
   re-measures both arms on the same frozen corpus and must cite them": both
   components were re-measured in-run (not imported) and each reproduced its
   prior reference **per case 10/10** — bm25 0.500/5/0 against the prior bm25
   arm; pi-lcm 0.600/1/5 against the prior pi_lcm_toollevel_sel arm (matching
   the row text's "pi-lcm abstains 5/5 but rescues 1/5 retrieve cases, bm25
   retrieves 5/5 top-1 but fires on every abstain case").
2. **Dependency honored.** S7-1's verdict (artifact-refuted) landed first and
   is quoted live from `team/S7-BM25-PREFILTER/verdict.json`; bm25_variant is
   forced to "prior", so the compose measures the prior bm25, not the refuted
   prefilter — the gate itself rejects composing on the refuted arm.
3. **Independent re-derivation (from CORVID-S7-2G-VERIFY, 15:35).** Recounted
   from raw results.jsonl without the gate: bm25 0.500/5/0, pi-lcm 0.600/1/5,
   compose 0.600/1/5, overlap both 1 / only_bm25 4 / only_pi_lcm 5 / neither
   0; gain +0.000 vs declared margin 0.10. Matches gate and cell exactly.
4. **Verdict integrity.** Declaration sha-bound into all 30 rows; the compose
   construction is mechanically "nothing where pi-lcm is empty, else exactly
   bm25", and the gate opened on 1/5 retrieve cases (sel-004) — the overlap
   counts make the profile readable, and the honest negative is stated with
   its consequence (this gate-owning construction does not justify a state
   layer; a union-style construction would be a separately-declared
   configuration, not a retry). Expectation registered pre-run and met.

## Limits

One frozen corpus, deterministic, no LLM — as declared; the conclusion is
about this construction on this corpus, and the cell says so rather than
overclaiming.
