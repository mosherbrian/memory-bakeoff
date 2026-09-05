# Gen96 — Round-3 Adapter / Retrieval-Budget Feasibility

**Contract:** `round3-adapters-v1`
**No engine runs.** Bindings reused, strategies preserved, budgets audited.

## Bindings reused, not reinvented

Scope bindings come from `scope_bound` (frozen Gen77, measured Gen78).
Configuration bindings come from `configuration_bound` (frozen Gen79, measured
Gen80). Neither is re-derived. Every engine binds **both** axes on write and
query, and a check compares **identity keys** rather than payload shapes — mem0
nests its query identities under `filters`, hindsight adds `tags_match`, and
neither is an asymmetry.

**Each engine keeps its own retrieval strategy.** `assert_no_mode_substitution`
raises if a read path is swapped for one that merely reports more — the
substitution Gen92 declined.

## A defect the checks caught before any engine ran

Building the combined binding, a plain dictionary merge of mem0's scope and
configuration **query** payloads silently dropped the scope filter, because both
nest under `filters` and the second overwrote the first.

That is **the Gen76 failure exactly** — an engine never given a scope to honour —
and it would have produced a Round-3 run whose scope column was meaningless.

`merge_payloads` now merges nested payloads and **raises on any primitive
collision**, which is the Gen79 hard constraint stated as a check rather than a
comment. Two tests cover both.

## The budget audit, which is what this generation is for

The interference scorer separates **true forgetting** from **distractor
displacement** by asking whether the result window was **saturated**. That
question only means something if the engine was given a window it could fill.

| engine | parameter | kind | window expressible |
|---|---|---|---|
| perseus | `limit` | native result count | yes |
| mem0 | `limit` | native result count | yes |
| agentmemory | `limit` | native result count | yes |
| **hindsight** | `max_tokens` | **token budget** | **no** |

**Hindsight cannot express "return at most N results."** Its recall takes
`bank_id`, `query` and `max_tokens`. Verified against the frozen adapter rather
than its description: `recall_arguments` **accepts a `limit` argument and never
passes it**, and the Round-2 harness truncated the reply with `[:LIMIT]`
afterwards.

Two consequences follow, and both are recorded rather than smoothed over:

**Every `requested_limit: 5` in hindsight's Round-2 records is the harness's
scissors, not the engine's window.** The frozen contract line
`post_filtering: "none; native order and native limit are preserved"` is accurate
for the other three engines and **inaccurate for hindsight**, because there is no
native limit to preserve.

**`saturated` is `NOT_DEMONSTRABLE` for hindsight.** A count equal to the harness
limit would describe the truncation, not the engine — so the forgetting /
displacement distinction cannot be drawn for hindsight from a result count alone.

## Therefore: within-engine scale curves

**Comparable windows cannot be expressed.** One engine is bounded by a token
budget and three by a result count; those are different quantities, and no
setting of one equals a setting of the other. Manufacturing an equality by
swapping hindsight to a different read path would answer a question about that
path instead.

So Round 3 is designed around **within-engine scale curves** — how each engine's
behaviour changes as its own distractor load rises — and **not** cross-engine
pooled counts. `assert_within_engine_only` raises on any summary carrying a
pooled or cross-engine total.

## Preflight, before any run

- **Scale is the only fixture variable** — one semantic core, one query, one
  scope, one configuration; only the distractor count changes. Re-asserted here
  against the frozen fixture.
- **Every engine receives identical records and the identical query.** Only the
  binding primitives differ, and those are the Gen77/79 ones.
- **`saturated` is meaningful for three engines and explicitly not for the
  fourth.**

`preflight_sha256` is recorded. Nothing has been run.
