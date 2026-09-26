# Role candidates: retain the useful mechanism, scope the claim

**Tern · cycle 2 · 26 September 2026.** Primary reading plus panel synthesis. No runs, installs or source changes.

## SKILL.state

[Primary v3 methods/results/limitations](https://arxiv.org/html/2608.26263v3) describe execution from a specification, structured state and latest observation. The reported 16.2× cumulative-token reduction is real for its Warehouse / Gemini-3-Flash / 100-step comparison against the Stateful baseline; it is not a portable saving estimate. The paper discards reasoning from its execution substrate and explicitly limits the sufficient-state assumption when old observations become relevant later. An external archive would be an additional design choice, not evidence the paper supplied it.

One scope correction to Corvid's card: 68% describes a category within analyzed Gemma failure logs, not the fraction of all small-model tasks failing. The compact-budget discussion also mixes characters and tokens, so I retain the qualitative comparison without a portable budget claim. **Watch, medium fit confidence:** structured State is useful where schema and patch quality are adequate; learned Memory and recoverable History remain separate responsibilities. No Gen45 reproduction or causal diagnosis is claimed.

## pi-lcm

Read local v0.1.3 source under `/var/home/bmosher/projects/pi-lcm`: `src/db/store.ts`, `src/db/schema.ts`, and README. Kiln identified the checkout as `17dea77`; that identity is not tied here to the older bake-off adapter.

`markCompacted` updates a flag, leaving message content intact. `getMessages` retrieves rows regardless of that flag. The README documents summary expansion to original messages. Thus compaction marking is **not loss of history by construction**, contrary to an inference in the panel card. An FTS deletion trigger establishes index maintenance if a deletion occurs, not a policy that deletes old history. A summary DAG is also not necessarily a branch-aware event DAG.

A concrete source-level limitation is narrower: the dedup key uses role, timestamp and only the first 200 searchable-text characters. Distinct messages with those same inputs can be treated as duplicates on insertion. That is a possible completeness failure under specified inputs, not a measured loss in Brian's sessions. I did not run a reproduction or trace the installed capture path. The old substring-ranking study concerns a pinned adapter and cannot be assigned to this checkout's FTS path merely because both use text matching.

**Watch as a recoverable-history/compaction candidate, medium confidence.** Existing compaction use should not be removed because a retrieval adapter ranked poorly. End-to-end capture completeness, branch identity and affordable recovery are the relevant unresolved properties. Avoid both “lossless proven” and “compaction destroys history.”

## Implication for the five layers

Projection, archive and execution control can share a product yet have different guarantees. Keep Brian's roles as requirements for judging the arrangement, not as product labels that imply those guarantees. The roster can now ask specific questions instead of either blessing or rejecting an entire system.
