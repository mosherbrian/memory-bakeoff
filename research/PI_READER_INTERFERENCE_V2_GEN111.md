# Gen111 — the repaired ruler, frozen and deliberately unrun

**Nothing was executed.** No reader, model, sidecar, memory engine, inference
endpoint or GPU. **The reader question is still OPEN.** Gen111 is not a result.

Frozen: `reader-interference-v2`, `contract_sha256` `fe34e5b116a4f298…`, at
`results/gen111/attempt1/` with a verifying manifest.
`reader-interference-v1` is recorded **`SUPERSEDED_AS_RULER / NON_EVIDENCE`**,
with every Gen109 and Gen110 byte left untouched.

## Four defects, and who found them

Gen110 executed perfectly and measured nothing, because the ruler was wrong four
ways. **I found two of them in my own output. The control plane found two more
by reading the requests I had actually sent** — which is the part worth dwelling
on, because I had looked at the same data and missed them.

| # | defect | found by |
|---|---|---|
| 1 | graded record prose instead of an answer value | executor |
| 2 | abstention was not expressible in the contract | executor |
| 3 | **the experiment was not blinded** | control plane |
| 4 | the negative control was graded as a failure | control plane |

**Defect 3 is the serious one and it is mine.** v1 showed the model ids
`C1-CUR` and `C1-SUP`. The suffixes name which record is current and which is
superseded, so **every conflict prompt handed the reader the answer**. No v1
conflict measurement could have meant anything, whatever the grader had done.

**Defect 4 is the one I half-saw.** The Gen110 report says in prose that six
stale answers in the stale-only control were "the control working" — while my
grader labelled the same cells `prohibited_stale_answer`. I wrote the correct
interpretation next to a ruler that contradicted it and did not notice.

## The repairs

**1. Answer values, separate from record prose.** Each record keeps its exact
Round 3 text; an evaluator-only canonical value sits beside it — Atlas
`41 t/s` / `27 t/s`, Vega `release/vega-4.x` / `release/vega-3.x`, Kestrel
`platform rota` / `network rota`, Solstice `512 GiB` / `256 GiB`. Normalisation
is written down, not assumed: NFKC, trim, collapse whitespace, and case-fold only
where the value permits. No LLM, embedding, fuzzy match, similarity, or alias
learned from Gen110. Every pair is proven distinct after normalisation, and a
short answer and a full sentence carrying the same value now classify
identically.

**2. Abstention made legal.** A strict two-field JSON object,
`{"answer", "citations"}`, with the exact sentinel `INSUFFICIENT` and an empty
citation list. One optional Markdown JSON fence is **accepted** — decided
explicitly and tested, not left implicit. Everything else fails closed into a
named parse state.

**3. Blinding.** Opaque role-neutral ids (`REC-4FAADF1FD6`), the mapping held in
evaluator truth only, and an enforced projection audit. The model now sees:

```
RECORDS:
[REC-4FAADF1FD6] Vega ships from branch release/vega-3.x.
[REC-677608760E] Vega ships from branch release/vega-4.x.
```

Nothing there says which is current. The eight v1 ids are kept as **negative
regression examples** — strings a prompt must never contain.

**4. Condition-relative grading.** Nine outcomes, none pooled, including the new
`correct_stale_control_answer`. Answering with the stale value is **correct** in
`CLEAN_STALE_NEGATIVE_CONTROL` and **prohibited** where current truth is
expected. A frozen truth table crosses condition × answer class × citation
relation; all nine outcomes are reachable and each row resolves to exactly one.

## Control gates, frozen before any run

A core is interpretable only if **every planned repetition** of `CLEAN_CURRENT`,
`CLEAN_STALE_NEGATIVE_CONTROL` and `INSUFFICIENT_CONTROL` receives its correct
outcome. A core that fails reports `NOT_INTERPRETABLE_CONTROL_FAILURE` for
Q1–Q3, and **no across-core label may be issued unless all four cores pass**.
Control failure is never excluded, averaged away, or used to revise the rule.

## What is unchanged

Same four semantic cores, same record texts, scopes, configurations, questions
and five conditions. v2 repairs the ruler, not the subject. A serialized change
ledger names every changed and unchanged field, the defect it addresses, the
reason, the expected effect, and who found it.

## Tests

46, covering each repair, the blinding audit, both control gates, truth-table
completeness, parser acceptance and rejection, the fence decision, and that
Gen109 and Gen110 still verify byte-for-byte.

## What this does not establish

Nothing about reader behaviour. No model has been asked anything under v2.
Gen110's 60 responses are cited only as the reason the contract changed; they
supply no alias, tolerance or fixture, and they may never serve as a reader
result.
