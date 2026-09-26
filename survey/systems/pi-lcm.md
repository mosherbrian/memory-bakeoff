# System card (deep-dive): pi-lcm

**kiln · 2026-09-26 · sources: survey/inputs/PI-LCM-TWO-ROLES-20260918.md, survey/inputs/PI-LCM-HIST-RETRIEVAL-DISPLACEMENT.md (S11-3 design), Phase 2 roadmap §layer 1, Gen45 pilot via reconciliation. No installs; primary-code docs not re-read this cycle — gaps marked.**

## The two roles (never grade one by the other's numbers)

- **Compaction layer in Brian's stack:** carries our eager-compaction + prefix pre-warming work; it stays for LATENCY. Settled stack choice, not re-decided by retrieval scores. Per TWO-ROLES, no `team/` doc ties it to compaction — the fleet reasons about it only as a contestant, which is how the category error happens.
- **Memory contestant in the bake-off:** measured as a store like the rest, and its retrieval numbers are poor-to-mixed (S6-2 tool-level retrieval 0.600 mean set-F1; S9 door rung2 0/5 helpful-evidence-first vs bm25 1/5, claude-mem 3/5).

## Storage vs compaction vs ranking (as far as the inputs establish)

- **Lossless storage:** roadmap's layer-1 candidate (canonical event DAG). Whether the implementation actually delivers branch-aware replayable history is **unknown from my reading** — I did not inspect primary code docs this cycle.
- **Compaction:** the eager-compaction role is attested by Brian's own statement (via TWO-ROLES), not by a benchmark. Keep it; measure latency separately if ever questioned.
- **Search ranking:** the S11-3 result is the sharpest mechanism evidence: an exact-AND gate matching scope tokens as SUBSTRINGS inside compound subjects (`delta` in `delta-mailbox`), giving 22/33 (66.7%) false supersessions on broader histories (rename + roster families 11/11 each; whole-token ledger-amend 0/11) while updates still supersede 13/13. So: whole-token-neighbor safe, substring-neighbor unsafe — the agentmemory disease shape, not update-blindness. This supersedes the comforting S7-3 0/32 null as the reference point for any state-layer claim.

## Builder's verdict

- **Compaction role: would deploy (keep). High confidence** — settled, latency-motivated, unrelated to memory scores.
- **Memory role: would watch. Low confidence** — needs Phase-D admission before any claim; the substring-gate failure is a concrete mechanism to retest, not a death sentence.
- Fit for Brian's stack: keep the layer, don't buy the store on current evidence.

## Open unknowns (not inferred)

Primary store/compaction implementation docs unread; Gen45 composed-view failure (7/12 vs 12/12) constrains the composite, not the substrate; no full five-layer test exists.
