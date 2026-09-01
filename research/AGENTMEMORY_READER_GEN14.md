# agentmemory Gen13 downstream-reader package: generation 14

Generation 14 did **not** rerun agentmemory.  It freezes the reader inputs
from the authoritative Gen13 retrieval artifacts and fails closed before
answer scoring because this Codex session has no interactive ChatGPT-sidecar
responder.

## Compatible prior reader configuration

The only configuration identical to the earlier real reader trial is the
file-queue `chatgpt_sidecar` backend:

- response model label: `GPT-5.6 Sol via ChatGPT sidecar`;
- system prompt: `You are a strict memory-grounded coding assistant. Never use outside knowledge or guess.`;
- user prompt/template: `memory_bakeoff.reader_eval._reader_prompt`;
- temperature: 0.0; no max-output override, tools, or seed;
- held-out set: the unchanged 14 `ANSWER_SPECS` cases;
- deterministic grader: `memory_bakeoff.reader_eval.score_answer`.

The existing `replay` backend is intentionally unavailable for this new
evaluation: it returns only an archived answer when both request ID and
semantic fingerprint match an earlier request, and Gen13’s frozen contexts
produce different fingerprints.  The local `fake` backend is plumbing only,
not a substitute for the real reader.  No OpenAI-compatible or Anthropic
backend was configured as a previously supported reader identity for this
evaluation.  Generating answers with any of those would create an incomparable
new reader experiment, so no answer was fabricated.

## Frozen evidence and request packages

`results/agentmemory_raw_product_gen14_reader_requests/` contains two complete
sidecar-compatible pending batches:

- `core/`: Gen13 `core-r1/run.json`, SHA-256
  `5a026371738611da90715b47d6555cb7a5b6b2462b713918555f8890dae4c347`;
- `stress/`: Gen13 `stress-r1/run.json`, SHA-256
  `fe72f67efe2651a0ca164c6dfaa0589d799c39d47f08208a378b177bf20fc17c`.

Each package includes 14 exact ranked-ID contexts, OpenAI-shaped sidecar
request envelopes, a pending batch record, source artifact hash, context
evidence, and request fingerprints.  Responses are deliberately absent.  The
writer reconstructed text only through the published native provenance chain
`canonical_record_id -> native_memory.content`; it neither called
`/smart-search` nor filtered/reranked the returned IDs.  Every generated
fingerprint was independently reconstructed and validated.  Gen13 r1/r2/r3
had identical reader-facing IDs and texts in both conditions, so r1 is a
representative frozen input rather than a cherry-picked repetition.

## Context risk before reader answers

This is context exposure, not answer propagation.

| Frozen condition | Held-out cases | Prohibited/stale context present | Wrong-scope context present | Reader answer metrics |
|---|---:|---:|---:|---|
| Core | 14 | 10/14 (0.714) | 1/14 (0.071) | pending interactive sidecar responses |
| Stress | 14 | 9/14 (0.643) | 1/14 (0.071) | pending interactive sidecar responses |

The core harmful-context cases are Q003, Q007, Q008, Q010, Q014, Q015, Q016,
Q019, Q022, and Q024.  The stress cases are the same except Q019.  The
wrong-scope exposure is Q019 in both conditions (rank 2 in core; ranks 1, 3,
4, and 5 in stress).  Notable stress contexts preserve the intended risk
without preprocessing: Q007 has stale M011 at rank 1 before M012; Q008 has
stale M013 at rank 1 before M014; Q022 has stale M041 at rank 1 before M042;
and procedure queries retain prohibited failure memories.

Until the sidecar requests are answered, the requested downstream rates—answer
success/coverage/abstention, prohibited/stale/wrong-scope answer rate, and
harmful-context-to-harmful-answer conversion—are **not measured**.  They must
not be inferred from context presence alone.  Once responses are supplied, the
existing deterministic grader can report both propagation and successful
harmful-context avoidance per case using the stored rank/context evidence.

## Lifecycle-adjusted interpretation

The stress retrieval score remains Gen13’s `raw_product` metric, not a memory
quality verdict: Hit@5 1.000, MRR 0.847, all-relevant@5 0.958, and
prohibited@5 0.133 occurred after the product had retained only 82/500 live
memories and falsely superseded 418/450 distinct stress distractors (92.9%).
The pending reader analysis is therefore explicitly adjacent to both the
retrieval metrics and lifecycle loss.  A high downstream answer rate, if later
observed, would not erase the destructive lifecycle finding; a harmful answer
would instead show that the surviving returned context still propagates stale,
failed, or wrong-scope evidence.
