# CORVID-S11-2-VERIFY — build verification, row S11-2 (KnowledgeDrift cross-system replay)

verified: corvid-dsh 2026-09-18 17:59 PDT (clock read at write) — VERIFIED PASS

Artifact: team/S10-KD-CROSS/ (design.md, declaration.json, items.jsonl,
run_kd_cross.py, results.jsonl, verdict.json, run.log + gate check.py).
Builder: kiln-flash (claimed 17:20, done 17:37 PDT). I authored neither the
gate (plumb-fable, verified 17:03, team/CORVID-S11-2G-VERIFY.md) nor the build.

Evidence, this pass:
1. Gate bytes unchanged since my pre-build verification: sha256(check.py)
   = cbfe79fe97a6d92a3559d8b4c9f7fe2898eef9bd32af730d830d86dd6251c32e —
   identical to the sha pinned in CORVID-S11-2G-VERIFY.md.
2. Declared check: `python3 team/S10-KD-CROSS/check.py` → rc 0, clean: five
   systems (bm25, claude_mem_chroma_lsa, dense_lsa, hybrid_rrf, tfidf_cosine)
   on the prior's frozen 120-probe sample; bm25 reproduces the prior item for
   item; the VERIFIED S7-4 gate runs clean on this directory.
3. Pre-registration ordering: declared_at 2026-09-19T00:32:59.727Z
   (= 17:32:59 PDT) precedes results.jsonl mtime 17:34:44 PDT.
4. Control-honesty spot-check: verdict.json per_family bm25 = Retrieval 21/40,
   Abstention 0/40, Rationale 5/40 — the prior's (S7-KD-WORLDS) cells exactly,
   so the harness did not move and system differences are system differences.
5. New-family cells spot-checked against the row's claims: dense_lsa
   0.275/0.000/0.075, tfidf_cosine 0.500/0.000/0.100 — match. Abstention
   0/40 on all five arms is the gate-recomputed flat shape; the finding (the
   externally-authored weakness is the ranked-retrieval shape itself, not one
   system) follows from the data, family-separate, old beside new as required.
6. The stretch arm claude_mem_chroma_lsa RAN (not_run empty), eval-now pinned
   2026-08-30T12Z per the row's declared condition — the S11-2G verification
   confirmed the gate enforces the not_run/capability-reason contract, so an
   unrun declared arm could not have passed.

verifier: corvid-dsh (did not author artifact or gate)
