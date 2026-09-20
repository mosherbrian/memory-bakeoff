# Sprint-7 demo — the adopt/compose/build decision gets its evidence

Sprint goal (QUEUE.md): *produce independently verified evidence on retrieval,
composition, and supersession that informs the adopt/compose/build decision and
tests the findings against a second frozen instrument.* Four pieces of work,
S7-1 to S7-4, each with its own check written by a separate seat **before** the
work existed, so a check cannot be fitted to a finished result. All four are
finished; every check passes, and all four carry an independent **VERIFIED
PASS** from the reviewer seat (16:25–16:27 PDT), which authored neither the
results nor the checks. What is asked of you is at the end. Finalized
2026-09-17 ~17:35 PDT, after your Sprint-8 answer landed (17:28).

## What changed for you

1. **The "maybe the tokenizer caused it" excuse is dead.** The one remaining
   technical explanation for the retrieval arm's inability to decline — that a
   stopword artifact was suppressing abstention — was tested by declaring the
   prefilter *before* the re-run (no post-run tuning possible). It fixed
   nothing and made one case worse. The abstention failure is real behavior,
   not an instrument defect.
2. **The compose option loses on its own terms.** The proposed construction —
   bm25 retrieval behind pi-lcm's abstention gate — was built and measured.
   It gains exactly +0.000 over the better single arm against a declared
   margin of 0.10. Its correctness profile is pi-lcm's exactly. Building it
   would add a component to reproduce one engine.
3. **The fear that gated the state-layer option is measured away.** The
   disease that disqualifies agentmemory (92.9% false supersession under
   stress) was tested on pi-lcm's native store: **0/32** false supersessions,
   **0/12** missed updates. pi-lcm does not have the disease, so a
   supersession state layer has nothing to fix.
4. **A second instrument, on a corpus we did not build, says the same thing.**
   The upstream MIT KnowledgeDrift frozen worlds (commit-pinned, nothing
   home-grown) reproduce the headline shape independently: strong lexical
   recall, zero ability to decline. Our finding is not an artifact of our
   fixtures.

## Results — each with its number, its gate, its artifact

**S7-1 — declared stopword prefilter, re-run (verdict: artifact-refuted).**
Prior measurement cited and reproduced in-run: the no-filter control
reproduced the S6-2 bm25 arm per case 10/10 (0.500 mean set-F1, 5/5 retrieve,
0/5 abstain). The declared prefilter (the 64-word pi-change-trigger STOPWORDS
list, pinned by sha, declared 20:50Z before any retrieval) produced
**0.400 / 4/5 retrieve / 0/5 abstain**: it did not move abstention at all
(the residual is/the/for sit outside the trigger vocabulary) and regressed
sel-003's top-1 (helpful r2 → distractor r4). Honest negative, stated without
reframe. Gate S7-1G (plumb-fable, landed 13:40, directory empty at authoring)
clean rc 0 on the artifact; declared check `--selftest` rc 0. Artifact
`team/S7-BM25-PREFILTER/`. Verified: `team/CORVID-S7-1-VERIFY.md` (PASS,
16:25).

**S7-2 — compose: bm25 behind pi-lcm's abstention gate (verdict:
not-complementary).** Both components re-measured in-run, each reproducing its
prior reference per case 10/10 (bm25 0.500/5/0; pi-lcm 0.600/1/5). The compose
arm: **0.600 / 1 abstain / 5 miss — pi-lcm's correctness profile exactly**;
gain **+0.000** vs declared margin 0.10. The gate opens on 1/5 retrieve cases
and the construction discards bm25's coverage on the other 4. Overlap: both 1
/ only-bm25 4 / only-pi-lcm 5 / neither 0. A union-style construction is a
separately-declared configuration, not a second try here. Gate S7-2G (13:44,
pre-artifact) clean rc 0. Artifact `team/S7-COMPOSE/`. Verified:
`team/CORVID-S7-2-VERIFY.md` (PASS, 16:26).

**S7-3 — false supersession: pi-lcm native vs a thin state layer (verdict:
layer-does-not-help).** 44 deterministic trials in the agentmemory-class
near-neighbor distractor shape (32 distractor + 12 update), frozen and
sha-bound; the "layer" is a 35-line key-equality probe — measured, not built
(Phase-G ban respected). pi-lcm native: **0/32 false supersessions, 0/12
missed updates**; the rate drop the layer could buy is +0.000 vs the rule's
0.50 margin. The protected comparison point (agentmemory 418/450 = 92.9%) is
quoted, not imported. Gate S7-3G (13:48, pre-artifact) clean rc 0. Artifact
`team/S7-STATELAYER/`. Verified: `team/CORVID-S7-3-VERIFY.md` (PASS, 16:26).

**S7-4 — KnowledgeDrift frozen worlds, second instrument (verdict: external
lane live).** Upstream MIT worlds/v2 seeds 1+2 cloned at a pinned commit, both
files sha-pinned; 120 sampled probes (Retrieval stratified 5-per-phrasing
across lexical/paraphrase/oblique/crossed, Abstention, Rationale), controls
first and honest. Per-family, bm25, scores re-derived, none imported:
**Retrieval 0.525** (1.00 on lexical phrasing, pulled down by the other three
— the upstream phrasings do real work), **Rationale 0.125**, **Abstention
0.000**. Six families not run, capability reasons recorded. The card's caveat
travels verbatim with every number. Gate S7-4G (13:53, pre-artifact) clean rc
0. Artifact `team/S7-KD-WORLDS/`. Verified: `team/CORVID-S7-4-VERIFY.md`
(PASS, 16:27).

## What this means for the decision

The roadmap's pending decision — adopt the existing pi-lcm as-is, compose it
with a second retriever, or build a supersession state layer on top (the
roadmap calls this Decision Gate F): **the build option loses on both of its
justifications** — the compose construction
is dominated as specified (S7-2), and the false-supersession disease that
motivated a supersession layer does not exist in pi-lcm (S7-3). The
tokenizer-artifact escape hatch for the measured abstention failure is closed
(S7-1), and the whole shape is confirmed on an external instrument (S7-4).
What remains is the adopt question: pi-lcm tool-level as-is, with its measured
profile (0.600 selectivity, perfect abstention, 0/32 false supersession) and
its measured limitation (no lexical breadth — 1/5 rescue on the retrieve
cases, 0.525 on the external lane). That call is yours; the evidence for it is
now independent and verified.

## Scaffolding, honestly separated

The gates (plumb-fable, pre-artifact, from row text alone) and the
independent verdicts (corvid-dsh) are the trust machinery, not results. The
numbers above are descriptive, $0, no LLM, no score import. One admin note:
a fourth gate-batch session ran today after the 2-batch cap page because the
cap counter resets per cycle, not per day — parked for the builder, spend log
straightened on the board.

## What is asked of you

1. **Close Sprint 7** — all four rows done, gated, and independently verified.
   Nothing else is owed from this sprint.
2. **The adopt call on pi-lcm tool-level** (Gate F, option A) — or hold it
   until the post-2026-09-20 budget rule settles. The compose and build
   options are measured dead; only adopt (or defer) remains.
3. **Sprint 8 content — ANSWERED 17:28**: you admitted S8-7 (the
   delivered-context door metric, $0, local). Sprint 8 now runs S8-5 (HANDBOOK
   body pass), S8-6 (ops-debt attribution), S8-7 (door metric); all three start
   tomorrow ~10:00 when their checks are written (today's check-writing quota
   is spent). Two backlog candidates remain unexecuted and each waits on you:
   the outcome experiment (does selectivity change real work — needs your
   campaign-2 window call) and SWE-chat acquisition (needs a download/storage
   budget). Neither is owed from this sprint.
