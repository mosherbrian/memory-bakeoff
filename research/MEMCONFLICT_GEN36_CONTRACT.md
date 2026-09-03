# Gen36 — MemConflict external benchmark contract (no contestant score)

**Evidence class: external-benchmark contract / no contestant score.** No memory
product ran. No reader, no LLM, no external API, no GPU. Round-1 and Round-2
results, `longitudinal-v1`, the Gen34 ledger and the Gen35 ablation are untouched.

## The pin

`TaoZhen1110/MemConflict` at `ec51d5d36e87f7665d1337f3a88cbde95fc2a964`, checked
out under `external/` (gitignored — the 39 MB dataset is not vendored). Dataset
`Data/Step4_4.jsonl`, blob `6dcbf9e536ea3e5d…`, sha256
`8ef9ec8589eccb86f63ab3a819a9180217405351a8d5846866721ea74babe092`, 30 lines.
Full identity, including the three evaluation files whose semantics this contract
depends on, is in `research/MEMCONFLICT_PIN.json`.

## What the release actually contains, measured locally

| | |
|---|---|
| personas (JSONL lines) | 30 |
| sessions | 1,579 — 900 `update`, 510 `chitchat`, 139 `initial_reveal`, 30 `future_plan` |
| sessions per persona | 51–54, mean 52.6 |
| questions | 3,750 — 2,946 dynamic, 360 static, 444 conditional |
| questions per persona | 107–144, mean 125 |
| dialogue turns | 71,060 |
| dialogue messages | 142,093 well-formed, mean 4,736 per persona |
| dialogue characters | 28,623,378 |

Token counts are deliberately omitted: they are tokenizer-specific, and repeating
the paper's numbers as if we had measured them would be exactly the kind of
borrowed fact this project keeps finding to be wrong.

**A defect in the release, counted rather than dropped.** 36 dialogue messages
across the corpus are malformed: 29 carry neither `role` nor `content` in the
expected keys (the role name is used as the key instead), 5 have content without a
role, 2 have a role without content. They are excluded from ingestion and their
exact provenance IDs are listed in `dataset-stats.json`. A corpus that silently
shrinks is indistinguishable from a memory system that forgot.

## Public input versus scorer-only gold

The registry is frozen in `field-registry.json`. The dividing line matters more
here than in `longitudinal-v1`, because MemConflict ships the construction
metadata in the same record as the dialogue.

**Public** — profile blocks, `Session_ID`, `Date`, `Session_Dialogue`, and the
question text.

**Scorer-only** — `answer`, `conflict_type`, `ability_target`, `difficulty`,
`Updated_Attributes`, `Revealed_Attributes`, `Static_Conflict_Information`,
`Conditional_Conflict_Information`, `Others_Dynamic_Information`,
`Question_Trigger_Types`, `Event_Types`, `Session_Outline`, `Session_Type`,
`metadata`, `token_cost`.

`Session_Type` is scorer-only on purpose: `update` versus `chitchat` tells a system
which sessions carry state changes, which is the thing being measured.
`assert_public_only()` walks a payload recursively and raises on any of these keys,
at any depth. Five adversarial injections are in the test suite.

## The chronology boundary

Read from upstream source, not assumed: `eval_memzero.py` iterates the session
chain in order, adds session *i*'s dialogue, then answers session *i*'s questions.
So the allowed history for a question is **sessions 0..i inclusive** — the
question's own session included. A provider that returns a unit from a later
session is rejected by `assert_within_boundary()`, and the pilot proves the
rejection fires.

## Upstream scoring, audited

Primary K is 3, with variants 2 and 5. Per conflict type upstream scores two
black-box metrics (one accuracy plus one behaviour signal) and two white-box
metrics (hit and log-rank, `1/log2(rank+1)`).

**The white-box metrics are LLM-judged.** The judge is shown the top-K retrieved
memory strings with their `created_at` values and returns a support rank. No
released identifier enters that decision, so upstream white-box scoring is
semantic, not exact.

Four fail-open paths in the pinned scorer, each of which turns "not measured" into
a number that reads as a real result:

1. `build_missing_answer_result` returns every metric as `0.0` when no model answer
   is found.
2. `evaluate_question_with_llm` catches every exception and returns `None`;
   `Evaluate_Single_Question` then falls back to `build_rule_based_result`, which
   leaves **all white-box metrics at 0.0** although nothing was measured. An API
   outage is therefore reported as a retrieval miss.
3. `parse_llm_metric_result` reads `parsed_result.get(metric_key, 0)`, so a judge
   that omits a key scores zero.
4. `parse_support_rank` returns `0` on any parse failure, which reads as "the
   support was not in the top K".

This is the Gen31 defect, in upstream code, on the metric the benchmark exists to
measure. We do not reproduce it: every one of those conditions is `UNMEASURED`
here, and the three lanes are named separately — `upstream_llm_judge`,
`upstream_rule_fallback`, `exact_provenance_whitebox` — and never merged.

## The exact-provenance fork, resolved per conflict type

The question was whether gold support can be mapped to released identifiers with
no semantic judgment. The answer is yes for 3,569 of 3,750 questions (95.2 %), and
the remainder are `UNMEASURED` rather than guessed.

| conflict type | questions | exact | mechanism |
|---|---|---|---|
| dynamic | 2,946 | 2,946 | the updated state is established by the question's own session, which carries the released `Updated_Attributes` |
| static | 360 | 360 | the question's session holds exactly one `Point_B`; its `Conflict_ID` names exactly one `Point_A` session, which holds the truth |
| conditional | 444 | 263 | the session establishes rule `R_n` of one conflict and the question addresses `R_{n-1}`, located by released `Rule_ID` order |
| conditional | | 181 unmeasured | the session establishes several rules and carries several questions; which question addresses which rule is not determined by any released identifier |

Every static session has exactly one question and exactly one `Point_B` — 360 and
360 — so that mapping is structural, not statistical.

For the conditional predecessor rule, the mapping mechanism is the released
`Rule_ID` ordering alone. As an **independent check** (never as the mapping), the
predecessor's released `Item` string appears in the question or its gold answer in
263 of 263 single-rule cases. Text was used to corroborate a structural rule, not
to build one.

`memconflict-exact-whitebox-v1` credits a returned unit only by released session
identity. A unit carrying the identical text under a different session earns
nothing — that is a test, not an aspiration.

## Diagnostic pilot

Benchmark-owned providers only, on the frozen calibration subset. Seven checks,
all passing:

- the `null` provider produces MEASURED_ZERO where gold support exists and
  UNMEASURED only where it does not — never the two confused;
- the existing BM25 baseline retrieves over the allowed prefix and earns
  hit@3 on 110 of 380 scored questions, so the metric is reachable and not
  saturated;
- a provider that returns a future session is rejected by the boundary assertion;
- a payload carrying the gold answer is rejected;
- a payload carrying the conflict label is rejected.

An oracle appears only inside the scorer unit tests, where it proves the metric can
reach rank 1, hit 1.0 and log-rank 1.0. It is not a contestant and is not published.

## Calibration subset

Personas whose SHA-256 digest is divisible by 5, chosen with no reference to any
label or outcome: 3 of 30 personas, about 380 questions. Frozen in
`calibration-manifest.json` before any outcome was inspected, and permanently
development-exposed. The full release stays byte-for-byte pinned; the held-out
slice is a reporting view over the same release, not a modified benchmark.

## Gen37 proposal — design only, not executed

The scale is the finding. Each persona is about 4,736 ingestible messages and 125
questions; the full release is 142,093 writes and 3,750 queries **per engine**.
Round 2's entire longitudinal fixture was 16 writes.

Rough cost, taking 0.3–1.0 s per write from the Round-2 profiles as the range
(the products were never timed per write, so this is an estimate and is labelled
as one):

| scope | writes | estimated wall time per engine |
|---|---|---|
| calibration (3 personas) | ~14,200 | 1.2–4 hours |
| full release (30 personas) | 142,093 | 12–40 hours |
| four engines, full release | 568,372 | 2–7 days |

Recommended matrix, in this order:

1. **Perseus Gen29 identity** and **Mem0 Gen32 raw `infer=False`** first: both
   ingest plain text with no LLM and no new feature, so their Round-2 identity
   carries over unchanged.
2. **Hindsight Gen31 raw/no-LLM**: carries over, but its `occurred_*` axis stays
   unreachable, exactly as in Round 2.
3. **agentmemory Gen33 raw**: carries over, and is the interesting one — its
   Jaccard retirement will fire far more often at 4,736 messages than at 16.
4. **OM**: excluded. It has no natural semantic query surface; forcing it into a
   retrieval benchmark would measure the adapter, not the product.

Repetitions: run one full retrieval pass per engine and repeat only where the
engine is nondeterministic. Round 2 showed all four are deterministic at retrieval
level across three repetitions; mechanically tripling 3,750 identical queries buys
nothing. Where a reader is later authorised, its randomness — not the retrieval —
is what needs repeats.

The answer-level lane stays `requires_reader_authorization`. When it is opened, the
same reader, model, configuration and prompt must be frozen before scoring, its
inputs limited to query plus returned memories, and its effect reported separately
from retrieval.

## Reproduction

```
scripts/build_memconflict_contract.py     # statistics, registries, audit, calibration
scripts/preflight_memconflict_gen36.py    # diagnostic pilot, no product
```

Contract `memconflict-benchmark-v1`, hash
`0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28`. Contract
content digest `057dd9587f61ce5e9d2100ec21e3bd7800d8115a091626384afd9efa9900410e`;
pilot digest `68ca5fcfa360e4b655dca71c304f909481713b0465fcd5061defe79aa7a788e7`.
Both are deterministic: no wall-clock value enters hashed content, and re-running
either builder on unchanged inputs reproduces the digest byte for byte.
