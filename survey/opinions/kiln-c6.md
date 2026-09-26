# kiln (Practitioner) — c6: when the stored recipe meets a changed hallway

**kiln · 2026-09-26 · ~500w · one worked case, judgment only. Sources: survey/inputs/PI-LCM-HIST-RETRIEVAL-DISPLACEMENT.md (S11-3, read c2), TWO-ROLES, BRIAN-PRINCIPLES. No probes/installs. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack".**

## The case: pi-lcm's stored retrieval rule under broader histories

- **Intended outcome:** the store's implicit procedure — ingest writes in order, re-query returns the currently-true write — should displace an original only for a genuinely newer state of the same fact (update), never for a different fact that merely looks similar (distractor).
- **Reuse:** the identical store and query path across all streams; the S7-3 controlled result (0/32 false supersessions, 12/12 updates) was the recorded recipe everyone relied on.
- **Changed condition:** S11-3 broadened the environment — 4-write streams, three near-neighbor distractor families (renamed mail target, companion ledger line, joint roster) instead of one whole-token-scope shape.
- **Revision demanded:** 22/33 false supersessions (rename 11/11, roster 11/11, ledger-amend 0/11), updates still 13/13. The mechanism is named: the exact-AND gate matches scope tokens as substrings inside compound subjects.

## Judgment: narrow first, repair second, do not retire

- **Narrow (now):** the S7-3 null holds only for whole-token-scope distractors — scope the recipe's claim to that envelope and mark broader histories untested-by-it. This is free and prevents the next reader from over-trusting the null.
- **Repair (if the store role matters):** whole-token matching at the gate, retested against the same 33-distractor corpus. But note the fit question: pi-lcm's settled role is compaction-for-latency, not store-of-record — repairing retrieval ranking on a latency layer may be work spent in the wrong place.
- **Retire (if):** a repair attempt fixes rename/roster while breaking the 13/13 update rate — then the gate is load-bearing in both directions and the store should stop pretending to adjudicate supersession at all (return candidates with clocks, let a state layer decide).

## Measured vs inferred (kept separate)

- **Measured:** 22/33, 0/13, per-family splits, controls (`never-supersede`/`always-supersede`) green, 46/46 sanity top-1, deterministic re-runnable trials. None of this is mine; it is S11-3's.
- **Inferred (builder judgment, low–medium confidence):** that whole-token gating repairs without update cost; that the compaction role is unaffected (different code path — engine vs store ranking — but I have not traced the call graph); that command-level success (ingest + top-1 retrieval) says nothing about outcome correctness — S11-3's updates all "succeeded" at retrieval while the answers went wrong, which is exactly the memo's caution.

## Minimal observation that should trigger each

- **Narrow:** one re-query where a compound-subject neighbor displaces the original — observed 22 times; trigger already pulled.
- **Repair:** a task that actually needs the store to adjudicate currency (none named yet on Brian's stack).
- **Retire:** any repair that trades update blindness for neighbor safety.

## Uncertainty deepened: compaction path independence (read-only source check)

The card inferred the compaction role was unaffected. Verified at method level: `CompactionEngine` touches the store only through seq-ordered accessors (`getUncompactedMessages`, `getUnconsumedSummariesByDepth`, `createSummary`, `markCompacted`) — no FTS `MATCH`, no ranking, no recency-ordered search in the compaction path. The S11-3 substring-gate failure lives in the query/ranking path, which compaction never calls. Inference upgraded to **high confidence**: no repair or retire decision about retrieval ranking touches the latency role. (Caveat unchanged: this is v0.1.3 HEAD `17dea77`, pin-vs-HEAD correspondence still unverified.)

**Net for Brian:** the procedure-maintenance pattern from c5 survives this case intact — failure surfaced the staleness, the corpus gives the retest, and the cheapest correct move (narrowing the claim) costs one honest sentence. **Medium confidence.**
