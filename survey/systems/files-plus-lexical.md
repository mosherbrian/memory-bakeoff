# System card: plain files + lexical search (Pi / local models baseline)

**kiln · 2026-09-26 · source: documentation + our bake-off readouts, no hands-on probe this cycle.**

- What it is: notes + handoff files on disk, searched with grep/lexical tools (rg, BM25-style). No embeddings, no server.
- Install/maintenance: install ~zero on Pi and Strix Halo; maintenance = naming/linking discipline and a handoff note saying what to recheck. Failure modes: paraphrase misses, silent staleness of "last observed" state. Our bake-off: lexical retrieval competitive on some fixtures; state-update failures motivate handoff-over-archive.
- Fit: cheapest baseline for Pi and local models before buying embeddings/services; matches Tern memo bets #2–#3.
- Verdict: **would deploy** as the starting baseline everywhere. **Medium confidence.**
- Sources: POSITION-MEMO.md §§2–3; team/S10-KD-CROSS/verdict.json; implementer/repo/research/ROUND1_FINAL_READOUT.md (all via memo citations; I did not re-verify paths this cycle).
