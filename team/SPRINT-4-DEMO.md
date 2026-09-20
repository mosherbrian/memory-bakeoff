# Sprint-4 demo — measured results

**Date:** 2026-09-16 sprint complete · **Cost:** $0 (GLM-5.3-Flash zero-quota, local runs only) · **Rule:** no outside score imported; every number below is recomputed by an independent verifier, not taken from the producer's receipt.

**The sprint goal, in one line:** measure at least two memory systems on a corrected instrument, and run the outcome comparison that was built in September and never executed. Both halves ran.

## Measured results — each with its number

**The measurement window was broken and is now repaired: +80.739%, verified.**
The campaign-1 window had closed seven hours early (the pin said midnight but was 17:00 PDT). S4-9 re-declared the window once as absolute UTC instants (`team/WINDOW-campaign-1.json`: 2026-09-12T18:05:00Z → 2026-09-16T07:00:00Z), re-ran the pairing on a frozen input snapshot (37 sessions, manifest sha `0f89ca5a…`), and produced the corrected table: 961 turns (123 memory / 815 no-memory / 23 excluded), n=122 pairs, **tokens median +80.739% (memory arm unfavorable)**, wall +149.233%, alt +3.595%. The original +77.4% headline is bannered unquotable-as-run. Corvid recomputed every number from the run outputs — all exact. *Meaning:* the trial's headline number is now quotable, and the quote is the corrected one.

**The firing test's control was scoring identically to the system; it no longer does.**
Corpus v2 gave every turn-3 filler class the same near-miss text, so the stale/anachronism controls fired 18/18 + 18/18 — the ruler measured itself. S4-10 changed exactly 36/60 turn-3 texts to class-appropriate distractors (manifest byte-identical to v2) and re-ran: stale **0/18**, anach **0/18** (were 18/18 each), fired 114/180 (was 150/180), FBMR 30/30, FalseFire 0/60, FirePrecision 30/114 on the unchanged shipping definition. A new fail-closed distinctness check guards the fix. *Meaning:* the instrument can now tell a real fire from a control fire.

**First cross-engine measurement: two controlled_core engines at an honest 0/30, one context arm at 25/30.**
S4-12 ran the frozen standard tier (corpus v3) across three locally-runnable engines at $0: `claude_mem_fts5_core` and `pi_lcm_store_reader` (both controlled_core, strict surface) scored **FBMR_topic 0/30 with a 0/60 non-empty derivation surface** — an honest zero, not a failure to measure; the bm25 baseline context arm scored **25/30**, missing exactly the five tokenizer-blind env_fact moments and firing 5/30 offtopic on entity echo. FalseFire 0/60 everywhere; determinism 9/9 tuples identical per engine; controls separate (never 0/180, always 134/180). Corvid recomputed every headline from the raw fire logs. *Meaning:* the first real comparison between memory systems on one frozen instrument — and it says retrieval-mediated context beats strict-surface controlled_core on this corpus, with the failure modes named.

**The outcome comparison that was never executed: first M1–M4 table, n=122.**
S4-13 replayed the frozen 286-event outcome bundle (286 unique ids, exactly-once; RI dedup 26→1; high-confidence band 235) and produced the first M1–M4 table over the corrected window: M1 median per-pair log-ratio **0.5918 tokens (×1.81) / 0.9132 wall (×2.49)** — reproducing S4-9's +80.739%/+149.233% exactly by a different path; M2 error-kind 13 memory vs 4 no-memory; M4 five window-level events. M3 is declared not instrumented, not invented. Descriptive only, no score import. *Meaning:* the September-built outcome protocol now has its first numbers, and they cross-check the token/wall result independently.

**Trust layer: done is now computed, and the two blind-spot classes are guarded.**
S4-8 shipped `rowcheck` (309 lines, no LLM): given a row id it resolves the row's declared artifact and declared check and exits 0 only when they hold — self-test 10/10, and it caught real defects live (a duplicate row id, two check-less rows honestly flagged BROKEN). S4-11 shipped two guards on the same exit contract: claim-lock (rejects a second `claimed:` transition — the S3-1 two-producer class) and prereg-diff (prereg vs verifier-checklist metric agreement — the FirePrecision 54/150-vs-30/150 class); both reject the dirty fixtures through the real path. The fleet poller now gates wakes on rowcheck's exit, not on status text. *Meaning:* a "done" in the queue is machine-checked evidence, and the two ways a row previously passed unnoticed are each rejected by a guard.

**Queue hygiene, measured: 26 unverified rows audited, 4 artifact-less rows backfilled, 0 residual gaps.**
S4-3 audited every done row that named no verifier (36 status-cell appends, second-seat PASS); S4-4 located and backfilled the four done rows with no artifact path; S4-1 verified row 38's research card against primary sources (arXiv/GitHub/HF/OpenReview, all exact); S4-2 proved row 23's "missing" diff exists in the done-in tree (sha match); S4-5 stripped the quiet-reply protocol from the conductor policy (grep count 0); S4-6 corrected the "pi-acp never answers" comment with the measured 0.36% no-reply rate over 1123 turns; S4-7 audited all seven role files for stale identities. *Meaning:* the queue's done-claims now match disk.

## Honestly separated: scaffolding, not results

- The S4-12 retrieval-mediated derivation protocol is the row's declared instrument choice; its ratification is a PO/Brian call, not a correctness fact (corvid's non-blocking caveat).
- M3 is not instrumented; M4 per-pair attribution is impossible by construction — both declared, not papered over.
- The metered product arm of the cross-engine comparison is deferred post-reset on Brian's GO; nothing here claims it ran.
- S4-5 scope finding: the base `conductor/POLICY.md:78` still carries the [quiet] rule (the live glm override countermands it; a `new-conductor` copy would resurrect it). Follow-up row recommended, not yet originated.

## The decision this demo exists for

The corrected, verified table is the basis for the result-fate call: **(a) publish as-is, (b) leaner recall, (c) gate campaign-2.** Paged to Brian 2026-09-16 14:4x.

## Next sprint, implied by the results

1. **Result-fate decision** — publish or gate; everything else sequences off it.
2. **Metered cross-system arm** post-reset, on the same frozen corpus v3.
3. **Sprint close/retro** — PO work; no close row exists yet.
4. **S4-5 follow-up row** for the base policy file, if the quiet-protocol resurrection risk is accepted as real.
