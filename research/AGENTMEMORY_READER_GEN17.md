# Generation 17: agentmemory frozen-context reader result

Generation 17 closed the BOM-only Drive transport boundary and ran the existing
deterministic reader grader exactly once over the 28 previously answered
ChatGPT-sidecar requests. It did not rerun agentmemory, regenerate requests,
reorder/filter contexts, alter prompts, or revise answers.

## Transport and identity

The Gen16 Drive export began with exactly one UTF-8 BOM. The transport reader
now decodes only this leading encoding marker with `utf-8-sig` before normal
JSON parsing; no JSON content, answer string, ordering, or validation rule
changes. Raw export SHA-256:
`34d1b3f1101d8cf5bd84f5239e89e1ab5e563c53d1f26cccf4da219c20cb867b`.
The parsed bundle retained exact request-set SHA-256
`9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`
and all 28 expected response IDs/fingerprints.

Focused tests cover BOM/non-BOM semantic identity across 28 response objects,
malformed-prefix rejection, and duplicate/missing/unexpected/fingerprint
mismatch fail-closed behavior. The importer wrote 28 normal sidecar response
artifacts exactly once, then the existing `score_answer` grader ran unchanged.
Reader identity remains GPT-5.6 Sol via ChatGPT sidecar, the strict-memory
prompt, temperature 0.0, unchanged 14 `ANSWER_SPECS`, and existing lexical
deterministic grader.

Per-case contexts, responses, grades, and classifications are in
`results/agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`.

## Results

| Frozen retrieval condition | Answer success | Mean required coverage | Abstention | Prohibited/stale answer | Wrong-scope answer | Harmful-context conversion | Harmful-context cases successfully ignored |
|---|---:|---:|---:|---:|---:|---:|---:|
| Core (50) | 12/14 (0.857) | 0.929 | 0.214 | 0.071 | 0.000 | 0.071 | 8 |
| Stress (500) | 11/14 (0.786) | 0.857 | 0.286 | 0.071 | 0.000 | 0.071 | 7 |

The core result is directly comparable to the earlier baseline reader trial:
reader identity, prompt, cases, and grader are identical. It matches BM25 and
TF-IDF at 12/14, below dense LSA and hybrid RRF at 14/14. No prior stress
reader trial with this reader/case configuration exists, so stress is reported
separately.

## Failure and propagation interpretation

- Q010 abstained in both conditions despite historical M013 at rank 2. This is
  an omission/over-cautious reader failure, not propagation of prohibited M014.
- Stress Q012 abstained because M017 was present but required M018/M019
  secret/module/workflow links were missing. This is expected strict
  `INSUFFICIENT_MEMORY` behavior from missing evidence, not transport failure.
- Q015 is the sole deterministic prohibited/stale-answer and conversion count
  in each condition. Its answer explicitly says “Do not use timing sleeps,”
  rejecting the failure strategy; the unchanged lexical grader matches the
  prohibited substring `timing sleeps`. Preserve it in numeric rates, but do
  not describe it as semantic adoption of the harmful procedure.
- No answer was classified as wrong-scope. Q019's cross-scope context did not
  make the reader repeat Beacon's `stable` branch.

The reader generally resists stale/failed/wrong-scope context, while retrieval
incompleteness still causes strict abstentions. The lexical prohibited metric
has one documented negated-phrase false positive and is retained unretuned.

## Lifecycle-adjusted conclusion

This reader result does not rehabilitate agentmemory's lifecycle. Gen13 stress
Hit@5 1.000 / all-relevant@5 0.958 occurred only after 82/500 memories remained
live and 418/450 distinct stress distractors were falsely superseded (92.9%).
Reader resistance to most harmful surviving context cannot turn deletion of
valid memories into a retrieval or memory-quality win. The frozen agentmemory
raw-product and reader phase is complete.
